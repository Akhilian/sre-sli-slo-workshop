## Why

Le dashboard *Burn rate et budget* montre un SLO d'une équipe à la fois. Pendant les pannes en direct, l'animateur suit jusqu'à 4 équipes × 5 SLO : il lui faut une vue qui montre d'un coup qui consomme son budget, et à quel rythme.

## What Changes

- Nouveau dashboard *DocShare · Vue d'ensemble des SLO* : matrices équipes × SLO du burn rate sur 1 h et du budget restant, colorées selon les seuils des alertes ; burn rate 1 h dans le temps ; alertes actives de toutes les équipes. Un clic sur une case ouvre *Burn rate et budget* sur l'équipe et le SLO.
- Le dashboard est empaqueté par `deploy/scripts/setup.sh` avec les autres.

## Capabilities

### New Capabilities

Aucune.

### Modified Capabilities
- `slo-dashboards` : vue d'ensemble de tous les SLO.

## Impact

- `observability/grafana/generate.py`, nouveau `observability/grafana/slo-overview.json`.
- `deploy/scripts/setup.sh` (ConfigMap des dashboards).
- `docs/operations/observability.md`, `docs/operations/seance.md`.
