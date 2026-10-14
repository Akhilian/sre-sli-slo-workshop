# Développement

## Développement

- Code : `app/`, organisé en ports et adaptateurs (voir « Architecture »). Un nouvel adaptateur implémente un port de `domain/ports.py` et se branche dans `bootstrap.py`.
- Tests : `pip install -r app/requirements-dev.txt` puis `pytest`, à la racine. Ils tournent sur les adaptateurs en mémoire, sans Redis, Postgres ni cluster, et vérifient notamment que chaque panne ne dégrade que son SLI et que les métriques respectent le contrat des SLO.
- SLO et dashboards : `observability/sloth/` (SLO et squelettes), `observability/sloth/solutions/`, `observability/grafana/generate.py`, `deploy/monitoring/sloth-values.yaml`, `deploy/monitoring/rbac.yaml`.
- Déploiement : `deploy/helm/docshare/` (pile d'une équipe), `deploy/monitoring/values.yaml` (kube-prometheus-stack), `deploy/environments/<cible>/` (différences par cible), `deploy/scripts/setup.sh` et `deploy/scripts/teardown.sh`. Les scripts tournent avec le bash 3.2 de macOS.
- Image : `.github/workflows/image.yml` lance les tests, puis publie à chaque push sur `main` une image amd64 + arm64 sur Docker Hub (`akhilian/docshare`, secret GitHub `DOCKERHUB_TOKEN` requis), taguée par SHA et `latest`.
- Spécifications et plan de travail : `openspec/` (`openspec list`, `openspec show <change>`).
