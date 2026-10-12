## Why

Le workshop accueille jusqu'à 4 équipes qui doivent chacune casser leur propre DocShare sans gêner les autres, sur un cluster fourni par l'animateur (GKE en priorité, EKS ou local selon les sessions). Il faut une installation en une commande, reproductible sur ces trois cibles, avec une pile de métriques partagée.

## What Changes

- Chart Helm `charts/docshare` : une pile DocShare complète par namespace (api, worker, notifier, Redis, Postgres), avec capacité fixe et sans autoscaling.
- Namespace `monitoring` partagé : kube-prometheus-stack (Prometheus Operator, Prometheus, Grafana), configuré pour collecter tous les namespaces d'équipe.
- Isolation par équipe : namespace `team-<nom>`, `ResourceQuota`, `LimitRange`, ServiceAccount avec rôle `edit` limité au namespace, kubeconfig à jeton par équipe.
- Scripts `scripts/setup.sh` (installation du monitoring et des équipes en une commande) et `scripts/teardown.sh`.
- Portabilité GKE / EKS / k3d par fichiers de valeurs, sans dépendance à un fournisseur ; `infra/k3d.yaml` pour le local.
- **BREAKING** (par rapport au plan initial) : abandon de `docker-compose`.

## Capabilities

### New Capabilities
- `team-environment` : pile DocShare par namespace d'équipe, isolation, droits, quotas, installation et suppression des équipes.
- `observability-stack` : Prometheus et Grafana partagés, collecte des métriques des équipes, persistance, accès à Grafana.
- `cluster-portability` : fonctionnement identique sur GKE, EKS et k3d, image, stockage, accès et dimensionnement.

### Modified Capabilities

Aucune.

## Impact

- Nouveaux fichiers : `charts/docshare/`, `monitoring/values.yaml`, `values-gke.yaml`, `values-eks.yaml`, `values-local.yaml`, `infra/k3d.yaml`, `scripts/setup.sh`, `scripts/teardown.sh`.
- Dépend de `add-docshare-app` (image et comportements de démarrage).
- Prérequis par cible : GKE Standard (pas Autopilot), add-on EBS CSI sur EKS, Docker avec 6 vCPU et 10 Go pour 4 équipes en local.
- Socle de `add-slo-and-dashboards` (Prometheus Operator, Grafana) et de `add-traffic-and-runbook` (chart dans lequel s'ajoute le Job k6).
