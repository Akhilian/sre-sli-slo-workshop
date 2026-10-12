## ADDED Requirements

### Requirement: Monitoring partagé
Le namespace `monitoring` SHALL héberger kube-prometheus-stack (Prometheus Operator, Prometheus, Grafana, kube-state-metrics, node-exporter), sans Alertmanager.

#### Scenario: Alertes consultables sans Alertmanager
- **WHEN** une règle d'alerte se déclenche
- **THEN** elle est visible sur la page `/alerts` de Prometheus et dans la série `ALERTS`

### Requirement: Collecte de tous les namespaces d'équipe
Prometheus SHALL sélectionner les `PodMonitor` et `PrometheusRule` de tous les namespaces sans exiger le label de la release Helm, scraper toutes les 5 s et évaluer les règles toutes les 15 s. Chaque série MUST porter le label `namespace` de son pod.

#### Scenario: Nouvelle équipe collectée
- **WHEN** une équipe est installée
- **THEN** ses métriques apparaissent dans Prometheus avec `namespace="team-<nom>"` en moins d'une minute

### Requirement: Persistance de l'historique
Prometheus SHALL stocker ses données sur un PVC de 10 Gi avec une rétention de 2 jours.

#### Scenario: Redémarrage de Prometheus
- **WHEN** le pod Prometheus redémarre pendant la séance
- **THEN** l'historique et les burn rates calculés avant le redémarrage sont conservés

### Requirement: Grafana accessible aux équipes
Grafana SHALL être exposé par un Service `LoadBalancer` limité par `loadBalancerSourceRanges`, avec un accès anonyme en lecture seule, et charger les dashboards depuis les ConfigMaps portant le label `grafana_dashboard`.

#### Scenario: Accès depuis la salle
- **WHEN** un participant ouvre l'adresse du LoadBalancer depuis une IP autorisée
- **THEN** il consulte les dashboards sans se connecter et ne peut pas les modifier

#### Scenario: Accès refusé hors de la salle
- **WHEN** une IP non autorisée tente d'accéder à Grafana
- **THEN** la connexion échoue

### Requirement: Pas d'alertes parasites
La configuration SHALL désactiver la collecte des composants du plan de contrôle inaccessibles sur un cluster managé (etcd, kube-scheduler, kube-controller-manager, kube-proxy) pour GKE et EKS.

#### Scenario: Page des alertes propre
- **WHEN** le cluster vient d'être installé et qu'aucune panne n'est active
- **THEN** aucune alerte `TargetDown` ni autre alerte de l'infrastructure n'est active
