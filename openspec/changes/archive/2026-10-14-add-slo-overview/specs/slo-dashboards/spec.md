## ADDED Requirements

### Requirement: Vue d'ensemble des SLO
Un dashboard *DocShare · Vue d'ensemble des SLO* SHALL afficher, pour les namespaces choisis (tous par défaut), une matrice équipes × SLO du burn rate sur 1 h colorée selon les seuils 6 et 14.4, une matrice du budget restant calculé comme dans le dashboard burn rate, le burn rate sur 1 h dans le temps et les alertes actives de toutes les équipes. Chaque case MUST ouvrir le dashboard burn rate sur l'équipe et le SLO correspondants.

#### Scenario: Deux pannes sur deux équipes
- **WHEN** `stale_index=1` est active dans une équipe et `worker_slow=10` dans une autre, avec les SLO des solutions appliqués partout
- **THEN** la matrice montre un burn rate élevé sur `search-quality` de la première et sur `processing-freshness` de la seconde, et proche de 0 ailleurs
