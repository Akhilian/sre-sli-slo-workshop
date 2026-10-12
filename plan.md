# DocShare : dépôt de démo pour le workshop SLI / SLO

Objectif : construire le système fictif DocShare, utilisé pendant un workshop de 2 h pour des développeurs sans connaissance SRE. Les participants passent d'un SLI fonctionnel à un SLO implémenté (Sloth), puis voient le budget d'erreur brûler en direct sur de vraies pannes.

Contraintes : outils open source uniquement, déploiement sur Kubernetes (GKE en priorité, EKS et local possibles) avec **un namespace par équipe**, jusqu'à 4 équipes par session, code minimal et lisible (c'est un support pédagogique, pas un produit). L'animateur installe tout en une commande ; les équipes n'ont rien à configurer.

## Topologie Kubernetes

Un cluster partagé, fourni par l'animateur. Cible principale : GKE. Doit aussi fonctionner sur EKS et en local (k3d), sans modifier le chart : seules les valeurs de `values-<cible>.yaml` changent.

- **Namespace `monitoring`** (partagé, géré par l'animateur) : kube-prometheus-stack (Prometheus Operator, Prometheus, Grafana) et le contrôleur Sloth.
- **Namespaces `team-<nom>`** (un par équipe) : une pile DocShare complète et isolée (api, worker, notifier, Redis, Postgres, k6). Chaque équipe a ses propres pannes, son propre trafic et son propre budget d'erreur.

Packaging : un chart Helm `charts/docshare`, installé une fois par équipe. Le script `scripts/setup.sh team-a team-b ...` installe la pile de monitoring si elle est absente, puis crée chaque namespace, ses droits et sa release.

Isolation et droits :
- `ResourceQuota` et `LimitRange` par namespace, dimensionnés pour la pile d'une équipe.
- Chaque équipe a un ServiceAccount avec un rôle `edit` limité à son namespace. `setup.sh` génère un kubeconfig par équipe dans `out/kubeconfigs/`.
- Grafana est partagé, en lecture seule pour les équipes, avec une variable `namespace` sur tous les dashboards.

## Portabilité GKE / EKS / local

Principe : ne dépendre que de Kubernetes standard. Pas d'Artifact Registry ni d'ECR, pas de classe de stockage nommée, pas de load balancer spécifique à un fournisseur.

| Sujet | Choix | GKE | EKS | Local (k3d) |
| --- | --- | --- | --- | --- |
| Image | Registre public (`ghcr.io`), image multi-arch amd64 + arm64 | pull | pull (nœuds Graviton possibles) | pull, ou `k3d image import` en développement |
| Stockage | Classe de stockage par défaut du cluster (aucun `storageClassName`) | `standard-rwo` | `gp3` ; **prérequis : add-on EBS CSI installé** | `local-path` |
| Accès des équipes à l'API | `kubectl port-forward` dans leur namespace | oui | oui | oui |
| Accès à Grafana | Service `LoadBalancer` restreint par `loadBalancerSourceRanges` (IP de la salle) ; repli : port-forward par l'animateur | LB L4 | NLB/CLB | servicelb de k3s |
| Ingress | Optionnel, `ingressClassName` en valeur du chart, désactivé par défaut | `gce` | `alb` (contrôleur à installer) | `traefik` |
| Authentification des équipes | Kubeconfig avec jeton de ServiceAccount (`kubectl create token --duration=8h`), aucun plugin d'authentification du fournisseur | oui | oui | oui |

Particularités de kube-prometheus-stack à désactiver sur un cluster managé, sinon des alertes `TargetDown` permanentes polluent la page `/alerts` : scrape d'etcd, kube-scheduler, kube-controller-manager et kube-proxy (plan de contrôle inaccessible sur GKE et EKS). Sur GKE, utiliser **Standard et non Autopilot** : Autopilot refuse node-exporter (`hostNetwork`, `hostPath`) et impose ses propres requêtes de ressources.

Hors périmètre : la création des clusters (pas de Terraform). Le README donne les commandes `gcloud` et `eksctl` de référence ; `infra/k3d.yaml` décrit le cluster local.

Dimensionnement pour 4 équipes (requêtes de ressources) :

| Composant | CPU | Mémoire |
| --- | --- | --- |
| Pile d'une équipe (api, worker, notifier, Redis, Postgres, k6) | ~0.6 vCPU | ~1 Gi |
| 4 équipes | ~2.5 vCPU | ~4 Gi |
| Monitoring (Prometheus, Grafana, opérateur, kube-state-metrics, node-exporter, Sloth) | ~1.5 vCPU | ~3 Gi |
| **Total** | **~4 vCPU** | **~7 Gi** |

Soit 2 nœuds `e2-standard-4` sur GKE ou `m6i.xlarge` sur EKS (3 pour la marge et les mises à jour de nœuds). En local, 4 équipes demandent une machine avec Docker à 6 vCPU et 10 Go ; une seule équipe suffit pour le développement. Prometheus : rétention de 2 jours et PVC de 10 Gi, la cardinalité reste faible. Le `ResourceQuota` de chaque namespace est calé sur la ligne « pile d'une équipe » avec 50 % de marge.

## Architecture applicative

Une seule base de code Python (FastAPI + `prometheus_client`), une seule image Docker, trois rôles choisis par la variable `ROLE` : `api`, `worker`, `notifier`. Chaque rôle est un Deployment.

Autres composants par namespace : Redis (file de jobs + hash `faults`), Postgres (métadonnées + recherche plein texte `tsvector`), k6. Redis et Postgres sont de simples StatefulSets d'une réplique (pas d'opérateur, pas de haute disponibilité : ce n'est pas le sujet). Pas d'Alertmanager : la page `/alerts` de Prometheus et un panneau Grafana sur `ALERTS` suffisent.

Flux : `POST /documents` insère en base (statut `pending`), pousse un job dans Redis, répond 202. Le worker dépile, simule l'OCR (`sleep` 1 à 3 s), indexe, calcule `document_processing_delay_seconds` (maintenant moins date d'upload), puis pousse un message de notification. Le notifier dépile et « envoie » (simulé).

Points d'implémentation :
- **Démarrage robuste** : pas d'ordre de démarrage garanti sur Kubernetes. Chaque rôle réessaie la connexion à Redis et Postgres. L'API crée le schéma au démarrage de façon idempotente (`CREATE TABLE IF NOT EXISTS`).
- **Indexation explicite** : la colonne `tsvector` est écrite par le worker (`UPDATE ... SET search_vector = to_tsvector(...)`), jamais par une colonne générée ni un trigger. Sinon l'indexation a lieu à l'INSERT et `stale_index` n'a aucun effet.
- **Capacité fixe** : worker à **1 réplique**, `WORKER_CONCURRENCY=4` threads, soit une capacité d'environ 2 jobs/s pour un trafic d'upload de 1/s (charge ~50 %). **Aucun autoscaling** (ni HPA, ni KEDA) : un autoscaler sur la file absorberait `worker_slow` et le SLI de fraîcheur ne bougerait plus.
- **Sondes** : l'API expose `/healthz`, qui ne lit pas le hash `faults` (sinon `upload_latency` fait échouer la sonde de vivacité et redémarre le pod). Le worker et le notifier utilisent leur port de métriques comme sonde.
- **Exposition des métriques** : l'API sert `/metrics` via FastAPI (uvicorn avec un seul worker, pour éviter le mode multiprocess de `prometheus_client` ; on monte en charge par réplicas). Le worker et le notifier exposent leurs métriques avec `start_http_server` sur un port nommé `metrics`. Le chart crée un `PodMonitor` par namespace.
- **Propriété des métriques** : `queue_depth` est exposée par le worker uniquement. Avec une seule réplique, pas de doublon ; le README précise d'agréger avec `max()` et non `sum()`.

## Endpoints de l'API

- `POST /documents` : upload (titre + contenu texte), répond 202 avec l'`id`
- `GET /documents/{id}` : statut et métadonnées
- `GET /search?q=` : recherche plein texte Postgres
- `POST /admin/faults` : active ou coupe une panne
- `GET /healthz` : sonde, insensible aux pannes
- `GET /metrics`

Accès des équipes à l'API (pour déclencher les pannes) : `kubectl port-forward svc/api 8000:80 -n team-<nom>`. Un Ingress par équipe (`team-<nom>.docshare.<domaine>`) est optionnel, activable dans le chart si le cluster a un contrôleur d'Ingress.

## Métriques à exposer

| Parcours | Métriques |
| --- | --- |
| Upload | `http_requests_total{route,status}`, `http_request_duration_seconds` |
| Traitement | `jobs_processed_total{status}`, `queue_depth`, `document_processing_delay_seconds` |
| Recherche | `search_requests_total{status}`, `search_results_count`, `search_fallback_total` |
| Notifications | `notifications_enqueued_total` (incrémenté par le worker), `notifications_sent_total{status}` (par le notifier), `notification_delay_seconds` |

Label `route` : toujours le modèle de route (`/documents/{id}`), jamais le chemin réel, pour éviter l'explosion de cardinalité. `/metrics`, `/healthz` et `/admin/faults` ne sont pas instrumentés. Le label `namespace` est ajouté par le scrape, l'application ne le connaît pas.

`search_fallback_total` : si la requête Postgres échoue (exception, timeout), l'API répond quand même 200 avec une liste vide et incrémente ce compteur. C'est une dégradation « gracieuse » qui masque l'erreur derrière un 200 : elle sert de point de discussion (« un 200 n'est pas un succès ») et n'est déclenchée par aucune panne du scénario.

Buckets d'histogramme alignés sur les seuils de l'exercice (sinon le SLI ne s'écrit pas en PromQL) :
- latence (`http_request_duration_seconds`) : 0.1, 0.3, 1, 3 s
- fraîcheur (`document_processing_delay_seconds`) : 10, 60, 300, 900 s
- qualité (`search_results_count`) : **0**, 1, 5, 20 ; le bucket `le="0"` est indispensable pour calculer la part de recherches sans résultat
- notifications (`notification_delay_seconds`) : 1, 5, 30, 120 s

Choix pédagogiques à respecter : aucune métrique côté client ; ne pas ajouter de métriques utiles en plus (CPU du worker, etc. sont des pièges volontaires, la taille de la file existe mais n'est pas un bon SLI). Sur Kubernetes, les métriques de cAdvisor et de kube-state-metrics (CPU, mémoire, redémarrages de pods) sont visibles dans Grafana : elles jouent le même rôle de piège.

Biais du survivant, à présenter au débrief : `document_processing_delay_seconds` n'est observé qu'à la fin d'un job. Pendant un engorgement, les documents bloqués dans la file restent invisibles jusqu'à leur traitement. Le SLI de fraîcheur réagit quand même (chaque job terminé arrive en retard), mais avec moins d'échantillons. C'est un effet attendu, pas un bug.

## Injection de pannes

Hash Redis `faults` du namespace, lu par chaque service avant chaque traitement (aucun redémarrage). `POST /admin/faults` le modifie. Une panne dans `team-a` n'a aucun effet sur `team-b`.

| Panne | Effet | SLI touché |
| --- | --- | --- |
| `upload_latency=2.0` | délai ajouté sur l'upload | latence |
| `upload_error_rate=0.02` (puis `0.5`) | proportion d'uploads en 5xx, **avant** l'INSERT et la mise en file (pas de document fantôme) | disponibilité |
| `worker_slow=10` | traitement ×10 plus lent, la file s'engorge | fraîcheur |
| `stale_index=1` | le worker marque `done` sans indexer : la recherche répond 200 avec 0 résultat | qualité |
| `notifier_drop=0.2` | 20 % des notifications perdues, sans erreur ni log | couverture |

Critère de réussite : chaque panne n'est visible que par le SLI du bon type (disponibilité, latence, fraîcheur, qualité, couverture), et uniquement dans le namespace où elle est déclenchée. En particulier `worker_slow` et `stale_index` doivent laisser la disponibilité de l'API intacte, et `worker_slow` ne doit pas dégrader le SLI de qualité (voir le scénario k6).

Calibrage de `upload_error_rate`, pour un objectif de 99.5 (budget de 0.5 %) :
- `0.02` donne un burn rate de 4. L'alerte ticket 1 j + 2 h demande plus de 1.5 % d'erreurs sur 2 h, soit environ 90 min de panne : **rien ne sonne pendant le workshop**. Message : une petite fuite se voit sur le burn rate, elle ne réveille personne.
- `0.5` donne un burn rate de 100. L'alerte page 1 h + 5 min (seuil 7.2 % sur 1 h) se déclenche après **environ 9 min** de panne. Avec `0.15`, il faudrait environ 29 min, ce qui dépasse le créneau de 25 min.

Calibrage de `worker_slow=10` : la capacité tombe à ~0.2 job/s pour 1 upload/s, l'attente augmente d'environ 4 s par seconde. Le seuil de 60 s est franchi en moins d'une minute, celui de 300 s en un peu plus.

## Sloth

Sloth tourne en **contrôleur** dans `monitoring`. Les SLO sont des ressources `PrometheusServiceLevel` (CRD `sloth.slok.dev/v1`) ; le contrôleur génère une `PrometheusRule` dans le même namespace, que Prometheus Operator charge.

Un fichier YAML par parcours dans `sloth/`. Seul le SLO d'upload (disponibilité, objectif 99.5) est prérempli et installé par le chart. Les autres sont des squelettes à compléter par les groupes (requêtes laissées en `TODO`). Format :

```yaml
apiVersion: sloth.slok.dev/v1
kind: PrometheusServiceLevel
metadata:
  name: docshare-upload
spec:
  service: "docshare-upload"
  slos:
    - name: "availability"
      objective: 99.5
      sli:
        events:
          errorQuery: sum(rate(http_requests_total{route="/documents",status=~"5.."}[{{.window}}]))
          totalQuery: sum(rate(http_requests_total{route="/documents",status!~"4.."}[{{.window}}]))
      alerting:
        name: DocshareUploadAvailability
        pageAlert:
          labels:
            severity: page
        ticketAlert:
          labels:
            severity: ticket
```

Workflow des équipes : compléter le YAML, puis `kubectl apply -f sloth/<parcours>.yaml -n team-<nom>`. Un squelette invalide est rejeté pour cette ressource seulement (erreur visible dans `kubectl describe` / le statut), sans effet sur les autres SLO ni sur les autres équipes.

Isolation des requêtes entre équipes : les YAML ne filtrent **pas** par namespace (même fichier pour toutes les équipes, plus lisible pour les débutants). Prometheus est configuré avec `enforcedNamespaceLabel: namespace` : l'opérateur injecte `namespace="<namespace de la règle>"` dans toutes les expressions et sur les séries produites. Les règles de `team-a` ne voient que les métriques de `team-a`, et leurs résultats ne se mélangent pas à ceux de `team-b` malgré le même nom de service. À valider en premier lors de l'étape Sloth ; en repli, ajouter `{namespace="..."}` aux requêtes via une valeur du chart.

Règles multi-fenêtres attendues (celles de Sloth par défaut, période de 30 j) : page 1 h + 5 min (burn rate 14.4), page 6 h + 30 min (6), ticket 1 j + 2 h (3), ticket 3 j + 6 h (1).

## Prometheus

kube-prometheus-stack, configuré pour :
- sélectionner les `PodMonitor` et `PrometheusRule` de tous les namespaces, sans exiger le label de release Helm (`*SelectorNilUsesHelmValues: false`) ;
- `enforcedNamespaceLabel: namespace` (voir Sloth) ;
- scrape toutes les 5 s, évaluation des règles toutes les 15 s, pour que les fenêtres de 5 min réagissent en une à deux minutes ;
- stockage sur un PVC : un redémarrage de Prometheus en plein workshop ne doit pas effacer l'historique ni les burn rates.

## Grafana

Grafana de kube-prometheus-stack, dashboards provisionnés par ConfigMaps (label `grafana_dashboard`, détectés par le sidecar), aucune configuration manuelle. Accès anonyme en lecture seule. Tous les dashboards ont une variable `namespace` (une équipe choisit la sienne ; l'animateur peut comparer). Construits sur les recording rules de Sloth (`slo:sli_error:ratio_rate5m`, `..._rate30m`, `..._rate1h`, `slo:error_budget:ratio`, etc.) :
- vue par parcours avec les métriques ci-dessus
- dashboard burn rate : burn rate sur 5 min, 30 min et 1 h avec lignes de seuil à 14.4 et 6, alertes actives (`ALERTS{namespace="$namespace"}`), temps avant épuisement au rythme actuel, budget restant sur 30 jours

Budget restant : ne pas utiliser `slo:period_error_budget_remaining:ratio` tel quel. Sloth calcule le ratio sur 30 j comme une moyenne des échantillons disponibles. Avec 2 h d'historique, 30 min de panne comptent comme un quart du mois et le budget passe largement en négatif. Le dashboard calcule plutôt :
- budget total = (1 − objectif) × volume attendu sur 30 j (débit moyen actuel × 30 j)
- budget consommé = erreurs réellement observées depuis le déploiement de l'équipe
- budget restant = 1 − consommé / total
- temps avant épuisement = budget restant × 30 j / burn rate actuel

Un texte sur le panneau indique l'hypothèse : « la période non observée est supposée parfaite ».

## k6

Un `Job` k6 par namespace (durée 3 h), installé par le chart, qui cible le Service `api` du namespace. Scénario unique en `constant-arrival-rate` (le débit ne baisse pas quand la latence monte, sinon `upload_latency` fausse les ratios). Débits indicatifs : 1 upload/s, 2 consultations/s, 2 recherches/s.

Chaque upload contient un jeton unique (par exemple `doc-<uuid court>`) en plus d'un texte tiré d'un petit corpus. k6 garde les `id` de ses uploads récents, les consulte via `GET /documents/{id}`, et ne cherche le jeton d'un document **qu'une fois son statut `done`**. Donc :
- en régime normal, toute recherche renvoie au moins 1 résultat : un résultat vide est anormal ;
- avec `stale_index`, les documents passent `done` sans être indexés : la recherche renvoie 0, le SLI de qualité chute ;
- avec `worker_slow`, les documents arrivent en `done` plus tard mais indexés : la qualité reste intacte, seule la fraîcheur bouge.

Les pannes sont déclenchées à la main via `POST /admin/faults`.

## À produire

- `app/` : code Python (3 rôles) et `Dockerfile` ; image multi-arch publiée sur `ghcr.io` (ou importée avec `k3d image import` en développement)
- `.github/workflows/image.yml` : construction et publication de l'image multi-arch
- `infra/k3d.yaml` : cluster local ; `values-gke.yaml`, `values-eks.yaml`, `values-local.yaml` : différences par cible (Ingress, `loadBalancerSourceRanges`, composants du plan de contrôle à ne pas scraper)
- `charts/docshare/` : Deployments (api, worker, notifier), StatefulSets (Redis, Postgres), Services, `PodMonitor`, `PrometheusServiceLevel` d'upload, Job k6, ConfigMaps des dashboards, Ingress optionnel
- `monitoring/values.yaml` : valeurs de kube-prometheus-stack et du contrôleur Sloth
- `sloth/` : un YAML `PrometheusServiceLevel` par parcours (upload complet, les autres en squelette)
- `k6/` : script de trafic (monté dans le Job par ConfigMap)
- `grafana/` : JSON des dashboards (empaquetés en ConfigMaps par le chart)
- `scripts/setup.sh` : installation du monitoring + création des namespaces, RBAC, quotas, releases et kubeconfigs par équipe
- `scripts/teardown.sh` : suppression d'une équipe ou de tout ; recréer une équipe avec un nouveau nom repart avec un budget vierge (l'historique de Prometheus est partagé)
- `README.md` : création du cluster (commandes `gcloud`, `eksctl`, `k3d`) et prérequis par cible, installation, distribution des kubeconfigs, déclenchement de chaque panne, ce que chaque panne doit montrer et en combien de temps

## Ordre de travail suggéré

1. Squelette de l'app (démarrage robuste, `/healthz`, `/metrics`) et image Docker
2. Upload, worker et notifier de bout en bout (indexation explicite par le worker)
3. Métriques et buckets
4. Injection de pannes
5. Chart `docshare` sur k3d, avec un namespace
6. kube-prometheus-stack + `PodMonitor` + dashboards Grafana
7. Contrôleur Sloth, SLO d'upload ; **valider `enforcedNamespaceLabel` avec deux namespaces** avant d'aller plus loin
8. Job k6 (jeton unique, recherche après `done`)
9. `setup.sh` multi-équipes, RBAC, quotas, kubeconfigs
10. Vérifier chaque panne une par une contre le critère de réussite, sur deux équipes en parallèle (une panne dans l'une, rien dans l'autre), en chronométrant le temps de réaction (en particulier `upload_error_rate=0.5` → page en moins de 10 min)
11. Répétition générale sur GKE avec 4 équipes : installation en une commande, kubeconfigs, accès Grafana, absence d'alertes parasites, consommation réelle contre le dimensionnement
12. Test d'installation sur EKS (au moins une fois avant la première session qui l'utilise)

## Session cible

2 h : mise en situation (10 min), SLI fonctionnel (25), SLI mesurable (25), SLO + error budget + burn rate (25), pannes en direct (25), débrief (10).

Préparation par l'animateur : cluster créé la veille (ou le matin), IP de la salle renseignée dans `loadBalancerSourceRanges`, puis `scripts/setup.sh` au moins 15 min avant la séance pour avoir un historique sain, puis distribution des kubeconfigs. Prérequis côté participants : `kubectl` installé. Pendant les pannes en direct : ne pas cumuler les pannes dans une même équipe, les couper une à une avant la suivante.
