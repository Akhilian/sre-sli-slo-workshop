## 1. Dashboards

- [x] 1.1 Remplacer les ratios de *Parcours* par des heatmaps des histogrammes bruts, neutraliser la description des recherches vides
- [x] 1.2 Générer *DocShare · Démarrage* : navigation, catalogue des métriques avec liens vers l'Explore, PromQL en 4 étapes
- [x] 1.3 Vérifier que chaque requête du guide renvoie des séries sur une équipe

## 2. Installation

- [x] 2.1 Ajouter `demarrage.json` à la ConfigMap des dashboards dans `deploy/scripts/setup.sh`
- [x] 2.2 Définir la page d'accueil par la préférence de l'organisation (`deploy/monitoring/grafana-home.py`, lancé par `setup.sh`) : `default_home_dashboard_path` crée sous Grafana 13 une copie illisible pour les visiteurs anonymes
- [x] 2.3 Vérifier sur un Grafana mis à jour qu'un visiteur anonyme arrive sur *Démarrage* et peut lire les trois dashboards
- [x] 2.4 Volume persistant pour Grafana (1 Gi, stratégie `Recreate`) : la préférence survit à un redémarrage du pod
- [x] 2.5 Vérifier dans un navigateur le rendu des heatmaps et le remplacement de `$namespace` dans les liens

## 3. Documentation

- [x] 3.1 Démo de prise en main dans `docs/operations/seance.md`
- [x] 3.2 Liste des dashboards dans `docs/operations/observability.md`
