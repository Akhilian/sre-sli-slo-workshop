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
Alternative de repli si l'injection pose problème avec les requêtes générées par Sloth (`{{.window}}`, `sloth_*` labels) : valeur `team` du chart injectée dans les requêtes du SLO d'upload, et filtre `namespace` ajouté à la main dans les squelettes. Moins lisible, mais sans dépendance à l'opérateur. À trancher dès la première tâche de ce change.

**Nom de service identique entre équipes.** `docshare-upload` partout ; les séries Sloth sont distinguées par le label `namespace` injecté. Les dashboards filtrent sur `namespace` puis sur `sloth_service` / `sloth_slo`.

**Calcul du budget dans Grafana.** Requêtes PromQL directes plutôt qu'une recording rule supplémentaire, pour que le calcul soit visible dans le panneau (support pédagogique). Volume attendu sur 30 j : `sum(rate(<total>[1h])) * 30 * 86400`. Erreurs consommées : `sum(increase(<errors>[$__range]))` avec une plage de temps du dashboard réglée par défaut sur « depuis 3 h », couvrant toute la séance. Temps avant épuisement : budget restant × 30 j / burn rate 1 h, affiché en heures ou jours, « ∞ » si le burn rate est nul.
Alternative écartée : `slo:period_error_budget_remaining:ratio`. C'est une moyenne sur les échantillons disponibles : avec 2 h d'historique, 30 min de panne comptent comme un quart du mois et le budget passe largement en négatif.

**Squelettes guidés.** Chaque squelette contient `service`, `name`, la section `alerting` complète, et des commentaires `# TODO` qui posent la question à résoudre (« quels événements sont mauvais ? », « quels événements comptent ? ») avec le nom des métriques disponibles. Objectif laissé en `TODO` : le choix fait partie de l'exercice.

**Solutions.** `sloth/solutions/` contient les cinq SLO complets. Exemples d'intention : latence = part des uploads au-delà de 0.3 s (bucket `le="0.3"`) ; fraîcheur = part des documents traités en plus de 60 s (`le="60.0"`) ; qualité = part des recherches avec `le="0.0"` (les bornes sont écrites au format flottant par `prometheus_client`) ; couverture = 1 − envoyées / mises en file. Le SLO de couverture n'est pas un ratio d'événements naturel : il est exprimé avec `errorQuery = enqueued − sent` et `totalQuery = enqueued`, avec un commentaire sur la limite (décalage temporel entre deux processus).

## Risks / Trade-offs

- [`enforcedNamespaceLabel` incompatible avec certaines requêtes Sloth] → validé en premier sur deux namespaces ; repli documenté ci-dessus.
- [Couverture : `enqueued − sent` peut être brièvement négatif à cause du décalage entre worker et notifier] → `clamp_min(..., 0)` dans la solution, et sujet de discussion au débrief.
- [Plage du dashboard trop courte pour le budget consommé] → plage par défaut de 3 h figée dans le JSON.
- [Fraîcheur peu échantillonnée pendant un engorgement (biais du survivant)] → assumé, présenté au débrief.

## Open Questions

- Objectifs des solutions (latence, fraîcheur, qualité, couverture) : proposer 99, 95, 99, 99.5 par défaut, à valider par l'animateur selon le discours du workshop.
