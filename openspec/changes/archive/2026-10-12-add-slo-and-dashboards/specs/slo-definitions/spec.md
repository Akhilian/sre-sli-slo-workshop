## ADDED Requirements

### Requirement: SLO déclarés comme ressources Kubernetes
Les SLO SHALL être des ressources `PrometheusServiceLevel` (`sloth.slok.dev/v1`) appliquées dans le namespace de l'équipe. Le contrôleur Sloth installé dans `monitoring` MUST générer la `PrometheusRule` correspondante dans le même namespace.

#### Scenario: Application d'un SLO par une équipe
- **WHEN** une équipe applique un `PrometheusServiceLevel` valide avec `kubectl apply -n team-a`
- **THEN** une `PrometheusRule` est générée dans `team-a` et ses règles sont évaluées par Prometheus en moins d'une minute

#### Scenario: Squelette incomplet
- **WHEN** une équipe applique un fichier dont l'objectif est encore `TODO`
- **THEN** `kubectl apply` est refusé avec un message indiquant que `objective` doit être un nombre

#### Scenario: Requêtes encore en TODO
- **WHEN** une équipe applique un fichier dont l'objectif est renseigné mais les requêtes encore en `TODO`
- **THEN** la ressource affiche `GEN OK false`, aucune règle n'est générée pour elle, et les autres SLO de l'équipe et des autres équipes continuent de fonctionner

#### Scenario: Droits des équipes
- **WHEN** une équipe utilise son kubeconfig pour appliquer, lister ou supprimer des `PrometheusServiceLevel` et lire les `PrometheusRule` de son namespace
- **THEN** l'API Kubernetes l'autorise

### Requirement: Isolation des règles par namespace
Prometheus SHALL appliquer `enforcedNamespaceLabel: namespace` : toute règle d'une `PrometheusRule` de `team-x` MUST ne lire que des séries de `team-x` et produire des séries portant `namespace="team-x"`. Les règles de `monitoring` MUST être exclues de ce mécanisme.

#### Scenario: Même YAML pour deux équipes
- **WHEN** `team-a` et `team-b` appliquent le même SLO d'upload, sans filtre de namespace dans les requêtes, et qu'une panne est active dans `team-a` seulement
- **THEN** le burn rate de `team-a` monte et celui de `team-b` reste nominal

#### Scenario: Règles de l'infrastructure intactes
- **WHEN** l'isolation est active
- **THEN** les règles fournies par kube-prometheus-stack dans `monitoring` continuent d'être évaluées sur tous les namespaces

### Requirement: SLO d'upload fourni
`scripts/setup.sh` SHALL appliquer `sloth/upload-availability.yaml` dans chaque namespace d'équipe : SLO `docshare-upload` / `availability` à l'objectif 99.5, avec `errorQuery` sur les 5xx de `/documents` complétée par `or vector(0)`, `totalQuery` excluant les 4xx, et des alertes page et ticket.

#### Scenario: Équipe fraîchement installée
- **WHEN** une équipe vient d'être installée
- **THEN** les règles du SLO d'upload existent dans son namespace, sans action de sa part

#### Scenario: Aucune erreur depuis l'installation
- **WHEN** aucun upload n'a jamais échoué dans l'équipe (la série des 5xx n'existe pas)
- **THEN** le SLI d'erreur vaut 0 et le burn rate s'affiche à 0, au lieu d'être absent

### Requirement: Alertes multi-fenêtres par défaut
Les SLO SHALL utiliser les fenêtres d'alerte par défaut de Sloth pour une période de 30 j : page 1 h + 5 min (burn rate 14.4), page 6 h + 30 min (6), ticket 1 j + 2 h (3), ticket 3 j + 6 h (1).

#### Scenario: Page sur forte panne de disponibilité
- **WHEN** `upload_error_rate=0.5` est active après au moins 15 min de trafic sain
- **THEN** l'alerte page `DocshareUploadAvailability` se déclenche en moins de 10 min

#### Scenario: Petite fuite sans alerte
- **WHEN** `upload_error_rate=0.02` est active pendant 25 min
- **THEN** le burn rate affiché est d'environ 4 et aucune alerte ne se déclenche

### Requirement: Squelettes et solutions
`sloth/` SHALL contenir un fichier par parcours : `upload-availability.yaml` complet, et `upload-latency.yaml`, `processing-freshness.yaml`, `search-quality.yaml`, `notification-coverage.yaml` avec requêtes et objectif marqués `TODO`. Chaque squelette MUST rappeler les métriques disponibles, le format flottant des bornes `le` et la commande pour l'appliquer. `sloth/solutions/` MUST contenir une version complète de chaque squelette.

#### Scenario: Chaque panne couverte par une solution
- **WHEN** l'animateur applique toutes les solutions dans un namespace
- **THEN** chacune des cinq pannes fait monter le burn rate d'un SLO, et d'un seul
