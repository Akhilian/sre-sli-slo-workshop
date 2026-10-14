## Why

Le workshop accueille jusqu'à 4 équipes qui doivent chacune casser leur propre DocShare sans gêner les autres, sur un cluster fourni par l'animateur (EKS, ou local en développement). Il faut une installation en une commande, reproductible sur ces deux cibles, avec une pile de métriques partagée.

## What Changes

- Chart Helm `deploy/helm/docshare` : une pile DocShare complète par namespace (api, worker, notifier, Redis, Postgres), avec capacité fixe et sans autoscaling.
- Namespace `monitoring` partagé : kube-prometheus-stack (Prometheus Operator, Prometheus, Grafana), configuré pour collecter tous les namespaces d'équipe.
- Isolation par équipe : namespace `team-<nom>`, `ResourceQuota`, `LimitRange`, ServiceAccount avec rôle `edit` limité au namespace, kubeconfig à jeton par équipe.
- Scripts `deploy/scripts/setup.sh` (installation du monitoring et des équipes en une commande) et `deploy/scripts/teardown.sh`.
- Portabilité EKS / k3s local (colima) par fichiers de valeurs, sans dépendance à un fournisseur.
- **BREAKING** (par rapport au plan initial) : abandon de `docker-compose`.

## Capabilities

### New Capabilities
- `team-environment` : pile DocShare par namespace d'équipe, isolation, droits, quotas, installation et suppression des équipes.
- `observability-stack` : Prometheus et Grafana partagés, collecte des métriques des équipes, persistance, accès à Grafana.
- `cluster-portability` : fonctionnement identique sur EKS et k3s local, image, stockage, accès et dimensionnement.

### Modified Capabilities

Aucune.

## Impact

- Nouveaux fichiers : `deploy/helm/docshare/`, `deploy/monitoring/values.yaml`, `deploy/environments/{local,eks}/{monitoring,docshare}.yaml`, `deploy/scripts/setup.sh`, `deploy/scripts/teardown.sh`, `deploy/terraform/eks/` (provisionnement du cluster EKS), guide de déploiement.
- Dépend de `add-docshare-app` (image et comportements de démarrage).
- Prérequis par cible : EKS provisionné par Terraform (add-on EBS CSI, classe `gp3` par défaut, AWS Load Balancer Controller), colima avec Kubernetes activé, 6 vCPU et 10 Go pour 4 équipes en local.
- Socle de `add-slo-and-dashboards` (Prometheus Operator, Grafana) et de `add-traffic-and-runbook` (chart dans lequel s'ajoute le Job k6).
