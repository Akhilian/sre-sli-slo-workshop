## Context

Premier déploiement sur EKS (2026-10-14) : le dashboard *Parcours* donnait aux équipes, dès leur arrivée, les quatre ratios à construire pendant « SLI mesurable » (mêmes métriques et mêmes seuils que `observability/sloth/solutions/`). Rien dans Grafana n'aidait non plus un participant qui ne connaît ni Grafana ni PromQL : il faut savoir où est l'Explore, quelles métriques existent et comment lire un histogramme.

Contraintes : Grafana 13.2.3 (kube-prometheus-stack 92.3.0), accès anonyme en lecture (`Viewer`, `viewers_can_edit` pour l'Explore), dashboards livrés par ConfigMap et sidecar, Prometheus partagé entre les équipes. Les dashboards sont produits par `observability/grafana/generate.py`.

## Goals / Non-Goals

**Goals:**
- Aucun SLI tout fait visible avant que les équipes l'aient écrit.
- Un participant sans expérience de Grafana trouve seul les métriques de son équipe et lance une première requête.
- La page d'accueil montre ce guide, sans configuration manuelle et pour les visiteurs anonymes.

**Non-Goals:**
- Un support participant hors de Grafana (fiche imprimée, site).
- Masquer les métriques des autres équipes : Prometheus reste partagé, le filtre `namespace` est enseigné.
- Former à PromQL au-delà de ce qu'exigent les SLI de l'atelier.

## Decisions

**Heatmaps des histogrammes plutôt que suppression des panneaux.** Les quatre ratios deviennent `sum by (le) (rate(<histogramme>_bucket[…]))` affichés en heatmap. Les équipes voient la distribution bouger pendant les pannes, avec les bornes `le` qu'elles utiliseront, mais choisir le seuil et écrire « bons / total » reste leur travail.
Alternatives écartées : supprimer les panneaux (on perd la lecture de `worker_slow` sur la vue) ; des quantiles `histogram_quantile` (introduit une notion hors programme et suggère un seuil).

**Un dashboard *Démarrage* généré, plutôt qu'un document externe.** Trois panneaux texte produits par `generate.py` : navigation, catalogue des métriques, PromQL en 4 étapes. Le guide vit là où les participants travaillent et reste cohérent avec les métriques, puisque le même script produit les requêtes.

**Liens vers l'Explore prérempli, requêtes brutes uniquement.** Chaque métrique du catalogue a un lien `/explore?schemaVersion=1&panes=…` dont la requête est filtrée sur `namespace="$namespace"`. `$namespace` est laissé non encodé dans l'URL pour que le panneau texte le remplace par l'équipe choisie. Le seul ratio montré est la disponibilité de l'upload, déjà fournie comme exemple de référence.

**Drilldown › Metrics comme porte d'entrée sans PromQL.** L'application est livrée avec Grafana 13 et accessible en anonyme (vérifié par `/api/plugins/grafana-metricsdrilldown-app/settings`). Le guide indique d'y filtrer `namespace`, car Prometheus contient aussi les métriques du cluster.

**Page d'accueil par préférence d'organisation, posée par l'API.** `deploy/monitoring/grafana-home.py` fait un `PATCH /api/org/preferences` (`homeDashboardUID: docshare-demarrage`). Il est lancé par `setup.sh` dans le conteneur `grafana-sc-dashboard`, qui a Python et les identifiants admin (`REQ_USERNAME`, `REQ_PASSWORD`), et il attend que le dashboard soit provisionné.
Alternative écartée : `default_home_dashboard_path`. Sous Grafana 13, le fichier est copié dans un dashboard `default-home-dashboard` sans droits : 403 pour les visiteurs anonymes (constaté). Donner des droits à cette copie ne tiendrait pas : elle est recréée à chaque démarrage et diverge du dashboard provisionné.

**Volume persistant pour Grafana.** La préférence vit dans la base SQLite de Grafana, jusqu'ici sur un `emptyDir`. On active `persistence` (1 Gi, classe par défaut : `gp3` sur EKS, `local-path` sur colima) avec `deploymentStrategy: Recreate`. Le volume est `ReadWriteOnce` : en `RollingUpdate`, un nouveau pod placé sur un autre nœud attendrait le disque indéfiniment. `helm uninstall kps` supprime le PVC : `teardown.sh --all` puis `terraform destroy` restent valables.

## Risks / Trade-offs

- [Volume recréé ou première installation : accueil par défaut] → `setup.sh` pose la préférence à chaque exécution ; commande seule documentée dans `docs/operations/observability.md`.
- [Libellés de Grafana (*Drilldown*, *Builder*, *Code*) modifiés par une future version] → version du chart épinglée ; relire le guide à chaque montée de version.
- [Heatmaps peu détaillées avec 4 à 5 bornes] → accepté : ce sont exactement les bornes utilisables dans un SLI.
- [L'exemple en 4 étapes rend les autres SLI trop faciles] → il ne traite que la disponibilité (compteur), alors que les autres SLI s'appuient sur des histogrammes ; l'animateur garde la question du seuil.

## Migration Plan

1. `python3 observability/grafana/generate.py observability/grafana`.
2. `deploy/scripts/setup.sh <cible> <équipes>` : met à jour le monitoring (Grafana redémarre avec une base neuve sur son volume), la ConfigMap des dashboards et la page d'accueil.

Retour arrière : revenir sur les valeurs et les dashboards puis relancer `setup.sh`. Une préférence d'accueil restée en base est sans effet si le dashboard disparaît, et Grafana reprend sa page standard.

## Open Questions

- Le volume persistant n'est pas encore appliqué au cluster EKS de test (2026-10-14) : il le sera au prochain `setup.sh`.
