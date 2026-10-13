# DocShare

Système fictif de partage de documents, support d'un workshop SLI / SLO de 2 h. Les participants partent d'un SLI fonctionnel, l'implémentent en SLO avec Sloth, puis regardent le budget d'erreur brûler pendant de vraies pannes.

> État actuel : l'application, son déploiement Kubernetes, le trafic k6, les SLO et les dashboards existent. Restent à écrire le déroulé de séance et les temps de réaction mesurés des alertes (`openspec list`).

## Architecture

Une seule image, trois rôles choisis par la variable `ROLE` (plus `standalone`, qui regroupe les trois dans un processus, voir plus bas) :

```
client ──POST /documents──▶ api ──LPUSH jobs──▶ Redis ──BRPOP──▶ worker ──LPUSH notifications──▶ Redis ──BRPOP──▶ notifier
                             │                                     │
                             └──────────── Postgres ◀──────────────┘
                               (documents + index plein texte)
```

1. `api` insère le document (statut `pending`), le met en file et répond 202.
2. `worker` simule l'OCR (1 à 3 s), indexe le document, le passe en `done` et demande une notification.
3. `notifier` « envoie » la notification (simulé).

Dans le code, architecture hexagonale (ports et adaptateurs) :

```
app/
  domain/        modèles, ports (Protocol) et cas d'usage ; ni FastAPI, ni Redis, ni Postgres, ni métriques
  adapters/      postgres.py, redis.py, memory.py, simulated.py (OCR, e-mail),
                 faults.py (les pannes), metrics.py (toutes les métriques)
  entrypoints/   http.py (FastAPI), worker.py, notifier.py, standalone.py
  bootstrap.py   câblage : adaptateurs du rôle, pannes posées sur les ports, cas d'usage
  main.py        ROLE -> bootstrap
```

Pour savoir ce qui est mesuré, lisez `app/adapters/metrics.py`. Pour savoir comment une panne agit, lisez `app/adapters/faults.py` : chaque panne y est un décorateur posé sur un port, le code métier n'en sait rien.

## Lancer l'application en local

### En un seul processus (mode standalone)

Sans Redis ni Postgres : l'API, le worker et le notifier tournent dans un seul processus, sur des adaptateurs en mémoire. Pratique pour découvrir l'application ou préparer une démo. Les données et les pannes actives sont perdues à l'arrêt.

```bash
docker build -t docshare:dev .
docker run --rm -p 8000:8000 -e ROLE=standalone docshare:dev

# ou sans Docker (Python 3.12)
pip install -r app/requirements.txt
ROLE=standalone python app/main.py
```

Tout fonctionne comme en mode distribué : routes, pannes (`/admin/faults`) et métriques. `GET /metrics` de l'API expose alors les métriques des trois rôles. Le trafic k6 peut viser ce mode (`k6 run -e API_URL=http://localhost:8000 -e DURATION=10m charts/docshare/k6/traffic.js`), mais il n'y a ni Prometheus ni Sloth : lisez `/metrics` directement.

### Pile distribuée avec Docker

Prérequis : Docker.

```bash
docker build -t docshare:dev .
docker network create docshare

docker run -d --name redis --network docshare redis:7.4-alpine
docker run -d --name postgres --network docshare \
  -e POSTGRES_USER=docshare -e POSTGRES_PASSWORD=docshare -e POSTGRES_DB=docshare \
  postgres:16-alpine

docker run -d --name api --network docshare -p 8000:8000 -e ROLE=api \
  -e REDIS_URL=redis://redis:6379/0 \
  -e DATABASE_URL=postgresql://docshare:docshare@postgres:5432/docshare \
  docshare:dev
docker run -d --name worker --network docshare -p 9100:9100 -e ROLE=worker \
  -e REDIS_URL=redis://redis:6379/0 \
  -e DATABASE_URL=postgresql://docshare:docshare@postgres:5432/docshare \
  docshare:dev
docker run -d --name notifier --network docshare -p 9101:9100 -e ROLE=notifier \
  -e REDIS_URL=redis://redis:6379/0 \
  docshare:dev
```

L'ordre de démarrage n'a pas d'importance : chaque rôle réessaie toutes les 2 s tant que Redis ou Postgres ne répond pas, et l'API crée le schéma au démarrage.

> Piège zsh : ne factorisez pas les options dans une variable (`E="-e A=1 -e B=2"; docker run $E ...`). zsh ne découpe pas la variable en mots et Docker reçoit une seule option mal formée. Écrivez les `-e` en entier comme ci-dessus.

Arrêt et nettoyage :

```bash
docker rm -f api worker notifier redis postgres && docker network rm docshare
```

### Configuration

| Variable | Rôles | Défaut | Rôle |
| --- | --- | --- | --- |
| `ROLE` | tous | (obligatoire) | `api`, `worker`, `notifier` ou `standalone` ; toute autre valeur arrête le processus |
| `REDIS_URL` | api, worker, notifier | `redis://localhost:6379/0` | files de jobs et hash des pannes |
| `DATABASE_URL` | api, worker | `postgresql://docshare:docshare@localhost:5432/docshare` | documents et index |
| `PORT` | api, standalone | `8000` | port HTTP de l'API (métriques comprises) |
| `METRICS_PORT` | worker, notifier | `9100` | port des métriques, utilisable aussi comme sonde |
| `WORKER_CONCURRENCY` | worker, standalone | `4` | jobs traités en parallèle (capacité ≈ 2 jobs/s) |
| `MAX_UPLOAD_BYTES` | api, standalone | `5242880` | taille maximale d'un fichier déposé (5 Mio), au-delà 413 |

## Déployer sur Kubernetes

Un cluster partagé, un namespace par équipe (`team-<nom>`) avec sa pile DocShare complète, et un monitoring commun dans `monitoring` (kube-prometheus-stack : Prometheus, Grafana, sans Alertmanager).

### Prérequis

Sur le poste de l'animateur : `kubectl` et `helm`. Les participants n'ont besoin que de `kubectl`.

| Cible | Création du cluster de référence | Prérequis |
| --- | --- | --- |
| Local | `colima start --kubernetes --cpu 6 --memory 10 --disk 60` | aucun ; l'image se construit localement (`docker build -t docshare:dev .`), le k3s de colima l'utilise sans registre |
| GKE | `gcloud container clusters create docshare --zone europe-west1-b --machine-type e2-standard-4 --num-nodes 3` | cluster **Standard** (Autopilot refuse node-exporter) |
| EKS | `eksctl create cluster --name docshare --region eu-west-3 --node-type m6i.xlarge --nodes 3` puis `eksctl create addon --cluster docshare --name aws-ebs-csi-driver` | add-on EBS CSI et classe de stockage par défaut (`gp3`) |

Sur GKE et EKS, l'image vient de `ghcr.io` : remplacez `OWNER` dans `values/<cible>/docshare.yaml` par le compte qui publie l'image.

Dimensionnement (ressources demandées) : ~0,6 vCPU et ~1 Gi par équipe, ~1,5 vCPU et ~3 Gi pour le monitoring, soit ~4 vCPU et ~7 Gi pour 4 équipes. En local, 4 vCPU suffisent pour 2 équipes ; prévoir 6 vCPU pour 4.

### Installation

```bash
# Local (contexte kubectl « colima »)
docker build -t docshare:dev .
scripts/setup.sh local a b

# GKE ou EKS : l'accès à Grafana est restreint aux plages indiquées (IP de la salle)
GRAFANA_SOURCE_RANGES=203.0.113.10/32 scripts/setup.sh gke a b c d
```

Le script affiche le contexte kubectl et demande confirmation hors du k3s local (`-y` pour ne pas demander, `KUBE_CONTEXT=<contexte>` pour en choisir un autre que le contexte courant). Il est idempotent : le relancer met à jour sans recréer. Il installe ou met à jour le monitoring, puis pour chaque équipe :
- le namespace `team-<nom>`, un quota et des valeurs par défaut de ressources ;
- la pile DocShare (api, worker à 1 réplique sans autoscaling, notifier, Redis, Postgres) et sa collecte de métriques ;
- un ServiceAccount aux droits `edit` limités au namespace, et son kubeconfig dans `out/kubeconfigs/<nom>.yaml` (jeton valable 8 h, `TOKEN_DURATION` pour changer).

Lancez l'installation au moins 15 min avant la séance : les fenêtres d'une heure des alertes ont besoin d'un historique sain pour que les pannes réagissent dans les temps annoncés.

À la fin, il affiche l'adresse de Grafana (port 3000, lecture anonyme ; le mot de passe admin est dans le secret `kps-grafana` du namespace `monitoring`).

### Trafic

Chaque équipe reçoit un trafic constant, sans action de sa part : un Job k6 (`k6-<révision>`) démarre avec l'installation et tourne 3 h. Script : `charts/docshare/k6/traffic.js`.

Débits par défaut : 1 upload/s, ~1,5 consultation/s, 2 recherches/s. Chaque upload contient un jeton unique (`doc-xxxxxxxx`) ; k6 consulte le document jusqu'à ce qu'il soit `done` (60 s au plus), puis recherche ce jeton. On ne cherche donc que des documents traités : une recherche vide signale un index périmé (`stale_index`), jamais un simple retard (`worker_slow`).

Le débit d'upload ne baisse pas quand l'API ralentit (`constant-arrival-rate`). Les métriques de k6 ne sont exportées nulle part : les SLI se mesurent uniquement côté serveur.

```bash
kubectl get jobs -n team-a                 # Job en cours
scripts/setup.sh local a                   # relancer le trafic pour 3 h (remplace le Job)
```

Réglages dans les valeurs du chart : `k6.uploadRate`, `k6.searchesPerDoc`, `k6.duration`, `k6.enabled`.

### Côté équipe

```bash
export KUBECONFIG=out/kubeconfigs/a.yaml
kubectl get pods
kubectl port-forward svc/api 8000:80
# l'API de l'équipe répond sur localhost:8000 (voir « Utiliser l'API » et « Pannes »)
```

Une équipe ne voit que son namespace : `kubectl get pods -n team-b` ou `-n monitoring` est refusé.

### Suppression

```bash
scripts/teardown.sh b        # supprime l'équipe b et son kubeconfig
scripts/teardown.sh --all    # supprime toutes les équipes et le monitoring
```

Pour repartir avec un budget d'erreur vierge, recréez l'équipe sous un autre nom : l'historique de Prometheus est partagé et garde les séries de l'ancien namespace.

## SLO et dashboards

### Écrire un SLO (équipes)

Les SLO sont des ressources Sloth (`PrometheusServiceLevel`). Le contrôleur Sloth du namespace `monitoring` les transforme en règles Prometheus : enregistrement des SLI sur plusieurs fenêtres et alertes multi-fenêtres (page 1 h + 5 min à un burn rate de 14,4, page 6 h + 30 min à 6, ticket 1 j + 2 h à 3, ticket 3 j + 6 h à 1).

| Fichier | État |
| --- | --- |
| `sloth/upload-availability.yaml` | complet, installé dans chaque équipe par `setup.sh` : c'est l'exemple de référence |
| `sloth/upload-latency.yaml` | squelette à compléter |
| `sloth/processing-freshness.yaml` | squelette à compléter |
| `sloth/search-quality.yaml` | squelette à compléter |
| `sloth/notification-coverage.yaml` | squelette à compléter |

Chaque squelette rappelle les métriques disponibles. Les requêtes s'écrivent **sans filtre de namespace** : Prometheus ajoute lui-même `namespace="team-<nom>"` à chaque règle d'une équipe, qui ne voit donc que ses propres métriques.

```bash
export KUBECONFIG=out/kubeconfigs/a.yaml
kubectl apply -f sloth/search-quality.yaml
kubectl get prometheusservicelevels     # GEN OK = true : les règles sont générées
```

| Symptôme | Cause |
| --- | --- |
| `kubectl apply` refusé : `objective ... must be of type number` | l'objectif est encore `TODO` |
| `GEN OK` à `false` | une requête est invalide ou encore `TODO` ; l'animateur lit la cause avec `kubectl logs -n monitoring deploy/sloth` |
| Burn rate absent au lieu de 0 | la requête d'erreurs ne renvoie rien tant qu'aucune erreur n'a eu lieu : ajouter `or vector(0)` (voir le SLO d'upload) |

Solutions pour l'animateur : `sloth/solutions/` (`kubectl apply -n team-a -f sloth/solutions/`).

### Grafana

Accès anonyme en lecture, à l'adresse affichée par `setup.sh` (port 3000).

- **DocShare · Parcours** : métriques brutes de chaque parcours pour l'équipe choisie.
- **DocShare · Burn rate et budget** : pour un SLO de l'équipe, burn rate sur 5 min, 30 min et 1 h avec les seuils 6 et 14,4, SLI et objectif, budget restant sur 30 jours, temps avant épuisement, alertes actives.
- **Explore** : ouvert aux visiteurs pour écrire des requêtes PromQL (séquence « SLI mesurable »). Les dashboards ne peuvent pas être enregistrés.

Le budget restant suppose que **la période non observée est parfaite** : il intègre le taux d'erreur sur la plage affichée (3 h par défaut) et le rapporte au budget de 30 jours. On n'utilise pas `slo:period_error_budget_remaining:ratio` de Sloth, qui ferait la moyenne sur le seul historique disponible et compterait 30 min de panne comme un quart du mois.

Avec un historique de quelques heures, les fenêtres longues réagissent fort : après une grosse panne, l'alerte page 6 h + 30 min peut sonner encore une vingtaine de minutes après la coupure. Attendez que les burn rates repassent sous 1 avant la panne suivante.

Les dashboards sont produits par `grafana/generate.py` (modifier le script, puis `python3 grafana/generate.py grafana` et relancer `setup.sh`).

## Utiliser l'API

| Endpoint | Rôle |
| --- | --- |
| `POST /documents` | upload d'un fichier en `multipart/form-data` (champ `file`, titre optionnel `title`, par défaut le nom du fichier), répond 202 avec l'`id` ; 422 si le fichier manque ou est vide, 413 au-delà de 5 Mio (`MAX_UPLOAD_BYTES`) |
| `GET /documents/{id}` | statut (`pending` / `done`) et métadonnées (titre, nom, type et taille du fichier), 404 si inconnu |
| `GET /documents/{id}/file` | téléchargement du fichier d'origine, 404 si inconnu |
| `GET /search?q=` | recherche plein texte, 20 résultats au plus |
| `GET /admin/faults` | pannes actives |
| `POST /admin/faults` | active ou coupe une panne |
| `GET /healthz` | sonde, insensible aux pannes |
| `GET /metrics` | métriques Prometheus de l'API |

```bash
# Upload d'un fichier
echo "facture électricité doc-abc12345" > facture.txt
curl -s -F file=@facture.txt localhost:8000/documents
# {"id":1}
curl -s -F file=@photo.png -F title="Photo du chantier" localhost:8000/documents

# Statut : pending, puis done après 1 à 3 s
curl -s localhost:8000/documents/1

# Recherche : le document n'est trouvé qu'une fois traité par le worker
curl -s 'localhost:8000/search?q=doc-abc12345'

# Téléchargement
curl -s -OJ localhost:8000/documents/1/file
```

Le worker simule un OCR : il lit le texte des fichiers texte (`text/*`, `.txt`, `.md`, `.csv`, `.json`), qui deviennent recherchables par leur contenu. Les autres fichiers (PDF, images...) ne sont recherchables que par leur titre.

Si Postgres ne répond pas pendant une recherche, l'API renvoie quand même 200 avec une liste vide et incrémente `search_fallback_total`. C'est volontaire : un 200 n'est pas forcément un succès.

## Métriques

| Rôle | URL | Métriques |
| --- | --- | --- |
| api | `localhost:8000/metrics` | `http_requests_total{route,status}`, `http_request_duration_seconds{route}`, `search_requests_total{status}`, `search_results_count`, `search_fallback_total` |
| worker | `localhost:9100/metrics` | `jobs_processed_total{status}`, `queue_depth`, `document_processing_delay_seconds`, `notifications_enqueued_total` |
| notifier | `localhost:9101/metrics` | `notifications_sent_total{status}`, `notification_delay_seconds` |

Buckets des histogrammes, alignés sur les seuils de l'exercice :

| Histogramme | Buckets |
| --- | --- |
| `http_request_duration_seconds` | 0.1, 0.3, 1, 3 s |
| `document_processing_delay_seconds` | 10, 60, 300, 900 s |
| `search_results_count` | 0, 1, 5, 20 |
| `notification_delay_seconds` | 1, 5, 30, 120 s |

Points d'attention pour écrire les requêtes PromQL :
- Les bornes sont écrites au format flottant : `le="0.0"`, `le="0.3"`, `le="1.0"`, `le="60.0"`. Une requête sur `le="0"` ou `le="60"` ne renvoie rien.
- Le label `route` contient le modèle de route (`/documents/{id}`), jamais l'identifiant réel.
- `/metrics`, `/healthz`, `/admin/faults` et les URL inconnues ne sont pas mesurés.
- Il n'y a volontairement ni métrique côté client, ni métrique de diagnostic supplémentaire : leur absence fait partie de l'exercice.

## Pannes

Les pannes sont stockées dans le hash Redis `faults` (en mémoire en mode standalone) et relues à chaque requête ou job : elles s'appliquent immédiatement, sans redémarrage. Leur code est dans `app/adapters/faults.py`.

```bash
# Activer
curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' \
  -d '{"name": "worker_slow", "value": 10}'
# Couper (valeur 0)
curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' \
  -d '{"name": "worker_slow", "value": 0}'
# Lister les pannes actives
curl -s localhost:8000/admin/faults
```

| Panne | Valeur | Effet | SLI dégradé | SLI intacts |
| --- | --- | --- | --- | --- |
| `upload_latency` | secondes, ex. `2.0` | délai ajouté à chaque upload | latence | disponibilité, fraîcheur, qualité, couverture |
| `upload_error_rate` | proportion, `0.02` puis `0.5` | uploads en 500, avant toute écriture (aucun document fantôme) | disponibilité | latence, fraîcheur, qualité, couverture |
| `worker_slow` | facteur, ex. `10` | traitement 10 fois plus lent, la file s'engorge | fraîcheur | disponibilité, latence, qualité |
| `stale_index` | `1` | documents marqués `done` sans être indexés : recherche en 200 avec 0 résultat | qualité | disponibilité, latence, fraîcheur |
| `notifier_drop` | proportion, ex. `0.2` | notifications perdues sans erreur, sans log, sans compteur | couverture | disponibilité, latence, fraîcheur, qualité |

Effets mesurés en local :

| Panne | Mesure |
| --- | --- |
| `upload_latency=2.0` | upload en 2,01 s ; `/healthz` en 2 ms |
| `upload_error_rate=0.5` | 93 erreurs sur 200 uploads, aucun document créé pour ces requêtes |
| `worker_slow=10` à 1 upload/s | uploads toujours en 202 ; au bout de 2 min, file à 92 jobs et premiers documents traités en plus de 60 s |
| `stale_index=1` | document `done` mais introuvable ; de nouveau trouvable après la coupure |
| `notifier_drop=0.2` | 18,7 % de notifications perdues sur 300, aucune ligne de log |

Effets mesurés sur le k3s local avec le trafic k6, panne dans `team-a` seulement (`team-b` reste nominale à chaque fois) :

| Panne | Mesure |
| --- | --- |
| `worker_slow=10` | uploads maintenus à 60/min ; file à 138 jobs après 4 min ; 83 % des documents traités en plus de 60 s ; 0 % de recherches vides |
| `stale_index=1` | 100 % de recherches vides, toutes en 200 ; aucun upload en erreur ; fraîcheur intacte |
| `upload_latency=2` | débit d'upload maintenu à 1/s ; 100 % des uploads au-delà de 1 s ; qualité intacte |

Burn rate sur 5 min de chaque SLO (solutions de `sloth/solutions/`), mesuré sur le k3s local après 2 min 30 de panne, deux pannes différentes en parallèle dans `team-a` et `team-b`. Chaque panne ne fait monter qu'un SLO, et seulement dans son équipe :

| Panne | Disponibilité | Latence | Fraîcheur | Qualité | Couverture |
| --- | --- | --- | --- | --- | --- |
| `upload_error_rate=0.5` | **44,7** | 0 | 0 | 0 | 0 |
| `upload_latency=2` | 0 | **45,1** | 0 | 0 | 0,7 (bruit) |
| `worker_slow=10` | 0 | 0 | **1,4** | 0 | 0 |
| `stale_index=1` | 0 | 0 | 0 | **45,0** | 0 |
| `notifier_drop=0.2` | 0 | 0 | 0 | 0 | **21,7** |

La fraîcheur réagit lentement : un document n'est compté en retard qu'une fois traité, plus de 60 s après son upload. Comptez environ 5 min de `worker_slow` pour un effet net (83 % des documents en retard après 4 min).

Une panne à la fois. Après `worker_slow`, la file met du temps à se vider (environ 1 min pour 100 jobs en attente). Attendez que `queue_depth` revienne à 0 avant la panne suivante, sinon le retard hérité fausse ce qu'elle montre.

## Développement

- Code : `app/`, organisé en ports et adaptateurs (voir « Architecture »). Un nouvel adaptateur implémente un port de `domain/ports.py` et se branche dans `bootstrap.py`.
- Tests : `pip install -r app/requirements-dev.txt` puis `pytest`, à la racine. Ils tournent sur les adaptateurs en mémoire, sans Redis, Postgres ni cluster, et vérifient notamment que chaque panne ne dégrade que son SLI et que les métriques respectent le contrat des SLO.
- SLO et dashboards : `sloth/` (SLO et squelettes), `sloth/solutions/`, `grafana/generate.py`, `monitoring/sloth-values.yaml`, `monitoring/rbac.yaml`.
- Déploiement : `charts/docshare/` (pile d'une équipe), `monitoring/values.yaml` (kube-prometheus-stack), `values/<cible>/` (différences par cible), `scripts/setup.sh` et `scripts/teardown.sh`. Les scripts tournent avec le bash 3.2 de macOS.
- Image : `.github/workflows/image.yml` lance les tests, puis publie à chaque push sur `main` une image amd64 + arm64 sur `ghcr.io/<owner>/docshare`, taguée par SHA et `latest`.
- Spécifications et plan de travail : `openspec/` (`openspec list`, `openspec show <change>`).
