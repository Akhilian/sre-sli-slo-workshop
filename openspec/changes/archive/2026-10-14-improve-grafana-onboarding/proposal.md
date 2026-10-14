## Why

Le dashboard *Parcours* affichait quatre ratios qui sont exactement les SLI à construire pendant la séquence « SLI mesurable » (mêmes métriques, mêmes seuils que `observability/sloth/solutions/`), et une description qui dévoilait l'angle mort de `stale_index`. Les équipes y ont accès dès le début de la séance. Par ailleurs, rien dans Grafana n'aide un participant qui ne connaît ni Grafana ni PromQL à trouver les métriques disponibles.

## What Changes

- *Parcours* ne montre plus que des métriques brutes : les quatre ratios deviennent des heatmaps des histogrammes, sans seuil.
- Nouveau dashboard *DocShare · Démarrage*, page d'accueil de Grafana : navigation (dashboards, *Drilldown › Metrics*, Explore), catalogue des métriques avec un lien vers l'Explore prérempli par métrique, PromQL en 4 étapes sur le SLI d'upload déjà fourni.
- Déroulé de séance : démo de prise en main de 5 min au début de « SLI mesurable ».

## Capabilities

### New Capabilities

Aucune.

### Modified Capabilities
- `slo-dashboards` : vue par parcours sans ratio de SLI, guide de démarrage en page d'accueil.

## Impact

- `observability/grafana/generate.py`, `parcours.json`, nouveau `demarrage.json`.
- `deploy/scripts/setup.sh` (ConfigMap des dashboards, page d'accueil), nouveau `deploy/monitoring/grafana-home.py`, `deploy/monitoring/values.yaml` (volume persistant de Grafana).
- `docs/operations/seance.md`, `docs/operations/observability.md`.
