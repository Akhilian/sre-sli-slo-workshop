## Context

Prometheus Operator et Grafana sont en place (change `add-k8s-deployment`), une pile par namespace d'équipe, avec des métriques portant le label `namespace`. Les participants écrivent leurs SLO en YAML pendant le workshop et doivent les voir fonctionner tout de suite. Ils sont débutants : moins le YAML contient de détails techniques (filtres de namespace, labels), mieux c'est.

## Goals / Non-Goals

**Goals:**
- Un YAML de SLO identique pour toutes les équipes, lisible par un débutant.
- Règles d'une équipe strictement limitées à ses propres métriques.
- Dashboards qui racontent l'histoire en 25 min : burn rate qui monte, alerte qui sonne, budget qui baisse.

**Non-Goals:**
- Fenêtres d'alerte personnalisées (on garde celles de Sloth par défaut et on calibre les pannes).
- Alertmanager et routage des notifications d'alerte.
- SLO basés sur des métriques côté client.

## Decisions

**Contrôleur Sloth plutôt que CLI.** Les équipes font `kubectl apply` ; pas de script de génération ni de rechargement de Prometheus. Le contrôleur est installé par son chart Helm officiel dans `monitoring`, version figée, avec droits sur tous les namespaces.
Alternative écartée : `sloth generate` dans un conteneur d'initialisation. Il faudrait un script de rechargement et donner aux équipes l'accès à un volume ou à `monitoring`.

**Isolation par `enforcedNamespaceLabel`.** Prometheus Operator réécrit chaque expression de règle pour y injecter `namespace="<namespace de la règle>"` et ajoute ce label aux séries produites. Les YAML de SLO restent sans filtre. Les règles de kube-prometheus-stack, qui vivent dans `monitoring` et doivent voir tous les namespaces, sont exclues via `excludedFromEnforcement`.
Validé sur le k3s local : l'opérateur injecte le filtre dans chaque sélecteur (requêtes SLI, alertes) et ajoute le label `namespace` à toutes les séries produites, y compris aux métadonnées `vector(...)` de Sloth. kube-prometheus-stack exclut déjà ses propres règles ; les ServiceMonitors et PodMonitors de `monitoring` sont exclus en plus, sinon les métriques du kubelet seraient toutes rattachées à `monitoring`. Le repli envisagé (filtre manuel dans chaque YAML) n'a pas été nécessaire.

**Nom de service identique entre équipes.** `docshare-upload` partout ; les séries Sloth sont distinguées par le label `namespace` injecté. Les dashboards filtrent sur `namespace` puis sur `sloth_service` / `sloth_slo`.

**Calcul du budget dans Grafana.** Requêtes PromQL directes plutôt qu'une recording rule supplémentaire, pour que le calcul soit visible dans le panneau. Le dashboard est générique (un SLO choisi par variable) et ne connaît pas les requêtes brutes de chaque SLO : il intègre donc le ratio d'erreur 5 min de Sloth sur la plage affichée (`sum_over_time(...[$__range]) × 15 s`, l'intervalle d'évaluation), et le rapporte au budget de 30 j (`(1 − objectif) × 30 j`). Sous trafic régulier, c'est la part du budget mensuel consommée par les erreurs observées. Plage par défaut : 3 h. Temps avant épuisement : budget restant × 30 j / burn rate 1 h, « ∞ (aucune erreur) » si le burn rate est nul.
Alternative écartée : `slo:period_error_budget_remaining:ratio`. C'est une moyenne sur les échantillons disponibles : avec 2 h d'historique, 30 min de panne comptent comme un quart du mois et le budget passe largement en négatif.

**SLO d'upload appliqué par `setup.sh`.** Le fichier `sloth/upload-availability.yaml` reste la source unique : Helm ne peut pas lire un fichier hors du chart, et le dupliquer dans le chart créerait deux versions. `setup.sh` l'applique dans chaque namespace.

**`or vector(0)` sur les compteurs d'erreurs.** Tant qu'aucun upload n'a échoué, la série `status=~"5.."` n'existe pas : le ratio est vide et le burn rate absent au lieu de valoir 0. Point à faire remarquer aux équipes (absence de donnée ≠ zéro).

**Droits des équipes sur les SLO.** Un ClusterRole agrégé au rôle `edit` (`monitoring/rbac.yaml`) ajoute la gestion des `PrometheusServiceLevel` et la lecture des `PrometheusRule`.

**Accès PromQL.** `viewers_can_edit` ouvre l'Explore de Grafana aux visiteurs anonymes ; les équipes y voient toutes les équipes, ce qui est acceptable (lecture seule, données factices). La source Alertmanager créée par défaut est désactivée.

**Dashboards générés.** `grafana/generate.py` produit les deux JSON ; modifier le script plutôt que les JSON garde les requêtes cohérentes entre panneaux.

**Squelettes guidés.** Chaque squelette contient `service`, `name`, la section `alerting` complète, et des commentaires `# TODO` qui posent la question à résoudre (« quels événements sont mauvais ? », « quels événements comptent ? ») avec le nom des métriques disponibles. Objectif laissé en `TODO` : le choix fait partie de l'exercice.

**Solutions.** `sloth/solutions/` contient les cinq SLO complets. Exemples d'intention : latence = part des uploads au-delà de 0.3 s (bucket `le="0.3"`) ; fraîcheur = part des documents traités en plus de 60 s (`le="60.0"`) ; qualité = part des recherches avec `le="0.0"` (les bornes sont écrites au format flottant par `prometheus_client`) ; couverture = 1 − envoyées / mises en file. Le SLO de couverture n'est pas un ratio d'événements naturel : il est exprimé avec `errorQuery = enqueued − sent` et `totalQuery = enqueued`, avec un commentaire sur la limite (décalage temporel entre deux processus).

## Risks / Trade-offs

- [Erreur de génération invisible pour les équipes] → un squelette mal rempli affiche `GEN OK false`, mais la cause n'est que dans les logs du contrôleur Sloth (`kubectl logs -n monitoring deploy/sloth`), lisibles par l'animateur seulement.
- [Historique court : fenêtres longues très sensibles] → avec moins de 6 h d'historique, la fenêtre 6 h ne contient que ce qui existe ; une panne fait sonner la page 6 h + 30 min et l'alerte persiste tant que le burn rate 30 min reste au-dessus de 6. Attendre le retour au calme entre deux pannes.
- [Couverture : `enqueued − sent` peut être brièvement négatif à cause du décalage entre worker et notifier] → `clamp_min(..., 0)` dans la solution, et sujet de discussion au débrief.
- [Plage du dashboard trop courte pour le budget consommé] → plage par défaut de 3 h figée dans le JSON.
- [Fraîcheur peu échantillonnée pendant un engorgement (biais du survivant)] → assumé, présenté au débrief.

## Open Questions

- Objectifs des solutions (latence, fraîcheur, qualité, couverture) : 99, 95, 99, 99 par défaut, à valider par l'animateur selon le discours du workshop. La couverture est passée de 99,5 à 99 : au repos, le décalage de comptage entre worker et notifier produisait un burn rate de ~1.
