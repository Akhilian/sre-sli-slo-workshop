## MODIFIED Requirements

### Requirement: Vue par parcours
Un dashboard SHALL présenter, pour le namespace choisi, les métriques de chaque parcours (upload, traitement, recherche, notifications), y compris `queue_depth` agrégée par `max()`. Il MUST NOT afficher de ratio « bons événements / total » ni de seuil sur un histogramme : les histogrammes sont montrés en distribution brute. Construire les SLI est l'exercice des équipes.

#### Scenario: Panne de lenteur visible sur la vue
- **WHEN** `worker_slow=10` est active
- **THEN** la vue montre la file qui grossit et le délai de traitement qui augmente, tandis que les panneaux d'upload restent nominaux

#### Scenario: Aucune solution sur la vue
- **WHEN** une équipe ouvre la vue par parcours avant la séquence « SLI mesurable »
- **THEN** aucun panneau ne donne la part des événements sous un seuil

## ADDED Requirements

### Requirement: Guide de démarrage
Un dashboard *DocShare · Démarrage* SHALL être la page d'accueil de Grafana. Il MUST expliquer comment choisir son équipe, parcourir les métriques (*Drilldown › Metrics*) et écrire une requête dans l'Explore, et lister chaque métrique de `service-metrics` avec son type, ses labels et un lien vers l'Explore prérempli d'une requête brute filtrée sur le namespace choisi. Seul l'exemple du SLI de disponibilité de l'upload, déjà fourni, MAY y apparaître comme ratio.

#### Scenario: Premier accès d'un participant
- **WHEN** un participant ouvre Grafana sans se connecter
- **THEN** il arrive sur *DocShare · Démarrage* et un lien du catalogue ouvre l'Explore sur une requête qui renvoie des séries de son équipe
