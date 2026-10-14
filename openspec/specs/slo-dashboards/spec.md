# slo-dashboards Specification

## Purpose
TBD - created by archiving change add-slo-and-dashboards. Update Purpose after archive.
## Requirements
### Requirement: Requêtes PromQL accessibles aux équipes
Grafana SHALL permettre aux visiteurs anonymes d'utiliser l'Explore sur la source Prometheus (`viewers_can_edit`), sans pouvoir enregistrer de dashboard. Grafana MUST NOT proposer de source de données Alertmanager.

#### Scenario: Écrire un SLI pendant la séance
- **WHEN** un participant ouvre l'Explore de Grafana sans se connecter
- **THEN** il peut exécuter une requête PromQL sur les métriques de son équipe

### Requirement: Dashboards provisionnés
Les dashboards SHALL être livrés sous forme de JSON dans `observability/grafana/`, produits par `observability/grafana/generate.py`, empaquetés par `deploy/scripts/setup.sh` dans une ConfigMap du namespace `monitoring` avec le label `grafana_dashboard`, et visibles dans Grafana sans configuration manuelle. Chaque dashboard MUST avoir une variable `namespace`.

#### Scenario: Grafana neuf
- **WHEN** le monitoring et une équipe viennent d'être installés
- **THEN** les dashboards apparaissent dans Grafana et la variable `namespace` propose l'équipe

### Requirement: Vue par parcours
Un dashboard SHALL présenter, pour le namespace choisi, les métriques de chaque parcours (upload, traitement, recherche, notifications), y compris `queue_depth` agrégée par `max()`. Il MUST NOT afficher de ratio « bons événements / total » ni de seuil sur un histogramme : les histogrammes sont montrés en distribution brute. Construire les SLI est l'exercice des équipes.

#### Scenario: Panne de lenteur visible sur la vue
- **WHEN** `worker_slow=10` est active
- **THEN** la vue montre la file qui grossit et le délai de traitement qui augmente, tandis que les panneaux d'upload restent nominaux

#### Scenario: Aucune solution sur la vue
- **WHEN** une équipe ouvre la vue par parcours avant la séquence « SLI mesurable »
- **THEN** aucun panneau ne donne la part des événements sous un seuil

### Requirement: Dashboard burn rate
Un dashboard SHALL afficher, pour le namespace et le SLO choisis, les burn rates sur 5 min, 30 min et 1 h avec des lignes de seuil à 14.4 et 6, les alertes actives (`ALERTS`) du namespace, le budget restant sur 30 j et le temps avant épuisement au rythme actuel.

#### Scenario: Burn rate pendant une panne
- **WHEN** `upload_error_rate=0.5` est active
- **THEN** le burn rate 5 min dépasse 14.4 en quelques minutes, suivi du 30 min puis du 1 h

### Requirement: Budget calculé pour un historique court
Le budget restant MUST NOT utiliser directement `slo:period_error_budget_remaining:ratio`. Il SHALL être calculé à partir du taux d'erreur intégré sur la plage affichée : budget consommé = Σ(ratio d'erreur 5 min × intervalle d'évaluation de 15 s) / ((1 − objectif) × 30 j), budget restant = 1 − consommé (borné à 0) ; temps avant épuisement = budget restant × 30 j / burn rate 1 h. Ce calcul suppose un trafic régulier, ce que garantit k6. Le panneau MUST indiquer l'hypothèse « la période non observée est supposée parfaite ».

#### Scenario: 30 min de panne avec 2 h d'historique
- **WHEN** une équipe a subi 30 min de `upload_error_rate=0.5` après 1 h 30 de trafic sain
- **THEN** le budget restant affiché reste entre 0 et 100 % et reflète la part d'un budget mensuel consommée, au lieu de passer largement en négatif

#### Scenario: Aucune erreur
- **WHEN** aucune panne n'a eu lieu depuis l'installation
- **THEN** le budget restant affiché est 100 % et le temps avant épuisement est indéfini ou affiché comme « ∞ »

### Requirement: Guide de démarrage
Un dashboard *DocShare · Démarrage* SHALL être la page d'accueil de Grafana. Il MUST expliquer comment choisir son équipe, parcourir les métriques (*Drilldown › Metrics*) et écrire une requête dans l'Explore, et lister chaque métrique de `service-metrics` avec son type, ses labels et un lien vers l'Explore prérempli d'une requête brute filtrée sur le namespace choisi. Seul l'exemple du SLI de disponibilité de l'upload, déjà fourni, MAY y apparaître comme ratio.

#### Scenario: Premier accès d'un participant
- **WHEN** un participant ouvre Grafana sans se connecter
- **THEN** il arrive sur *DocShare · Démarrage* et un lien du catalogue ouvre l'Explore sur une requête qui renvoie des séries de son équipe

### Requirement: Vue d'ensemble des SLO
Un dashboard *DocShare · Vue d'ensemble des SLO* SHALL afficher, pour les namespaces choisis (tous par défaut), une matrice équipes × SLO du burn rate sur 1 h colorée selon les seuils 6 et 14.4, une matrice du budget restant calculé comme dans le dashboard burn rate, le burn rate sur 1 h dans le temps et les alertes actives de toutes les équipes. Chaque case MUST ouvrir le dashboard burn rate sur l'équipe et le SLO correspondants.

#### Scenario: Deux pannes sur deux équipes
- **WHEN** `stale_index=1` est active dans une équipe et `worker_slow=10` dans une autre, avec les SLO des solutions appliqués partout
- **THEN** la matrice montre un burn rate élevé sur `search-quality` de la première et sur `processing-freshness` de la seconde, et proche de 0 ailleurs

