## Why

Le cœur du workshop est le passage d'un SLI à un SLO implémenté, puis l'observation du budget d'erreur qui brûle. Il faut donc que les équipes puissent écrire leurs SLO en YAML Sloth, les appliquer dans leur namespace et voir immédiatement burn rates, alertes et budget restant dans Grafana, sans que les règles d'une équipe ne voient les métriques d'une autre.

## What Changes

- Installation du contrôleur Sloth dans `monitoring` : les SLO sont des ressources `PrometheusServiceLevel` transformées en `PrometheusRule`.
- Isolation des règles par équipe grâce à `enforcedNamespaceLabel` de Prometheus Operator : un même YAML, sans filtre de namespace, sert à toutes les équipes.
- `sloth/` : SLO d'upload (disponibilité 99.5) complet et installé par le chart ; squelettes à compléter pour la latence, la fraîcheur, la qualité et la couverture.
- `sloth/solutions/` : versions complètes réservées à l'animateur, pour la démo et la vérification des pannes.
- Dashboards Grafana provisionnés : vue par parcours, et dashboard burn rate (burn rates 5 min / 30 min / 1 h, seuils 14.4 et 6, alertes actives, budget restant et temps avant épuisement calculés pour une période courte).

## Capabilities

### New Capabilities
- `slo-definitions` : format et cycle de vie des SLO Sloth, isolation par namespace, règles d'alerte multi-fenêtres, squelettes et solutions.
- `slo-dashboards` : dashboards par parcours et dashboard burn rate / budget, variable `namespace`.

### Modified Capabilities

Aucune.

## Impact

- Nouveaux fichiers : `sloth/*.yaml`, `sloth/solutions/*.yaml`, `grafana/*.json`, templates du chart pour le SLO d'upload et les ConfigMaps de dashboards.
- Modification de `monitoring/values.yaml` (`enforcedNamespaceLabel`, exclusion des règles de `monitoring`) et de `scripts/setup.sh` (installation du contrôleur Sloth).
- Dépend de `add-docshare-app` (métriques) et de `add-k8s-deployment` (Prometheus Operator, Grafana, chart).
