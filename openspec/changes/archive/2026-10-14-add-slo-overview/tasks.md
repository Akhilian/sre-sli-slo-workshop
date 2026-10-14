## 1. Dashboard

- [x] 1.1 Générer *DocShare · Vue d'ensemble des SLO* dans `generate.py` : matrices burn rate 1 h et budget restant, courbe du burn rate, alertes actives, lien vers le détail
- [x] 1.2 Vérifier les requêtes sur 4 équipes × 5 SLO avec deux pannes actives (`stale_index`, `worker_slow`)
- [x] 1.3 Vérifier dans un navigateur la matrice (couleurs, noms de colonnes) et le lien vers le détail

## 2. Installation et documentation

- [x] 2.1 Ajouter `slo-overview.json` à la ConfigMap des dashboards dans `deploy/scripts/setup.sh`
- [x] 2.2 Liste des dashboards dans `docs/operations/observability.md`, séquence des pannes dans `docs/operations/seance.md`
