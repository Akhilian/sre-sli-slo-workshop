# Développement

## Développement

- Code : `app/`, organisé en ports et adaptateurs (voir « Architecture »). Un nouvel adaptateur implémente un port de `domain/ports.py` et se branche dans `bootstrap.py`.
- Tests : `pip install -r app/requirements-dev.txt` puis `pytest`, à la racine. Ils tournent sur les adaptateurs en mémoire, sans Redis, Postgres ni cluster, et vérifient notamment que chaque panne ne dégrade que son SLI et que les métriques respectent le contrat des SLO.
- SLO et dashboards : `observability/sloth/` (SLO et squelettes), `observability/sloth/solutions/`, `observability/grafana/generate.py`, `deploy/monitoring/sloth-values.yaml`, `deploy/monitoring/rbac.yaml`.
- Déploiement : `deploy/helm/docshare/` (pile d'une équipe), `deploy/monitoring/values.yaml` (kube-prometheus-stack), `deploy/environments/<cible>/` (différences par cible), `deploy/scripts/setup.sh` et `deploy/scripts/teardown.sh`. Les scripts tournent avec le bash 3.2 de macOS.
- CI : `.github/workflows/ci.yml` (pull requests, push sur `main`) lance en parallèle les tests Python, les tests et le build de `web/`, `helm lint` et `helm template` (local, eks), `shellcheck` des scripts, `terraform fmt` et `validate`, la cohérence des dashboards avec `generate.py`, `sloth validate` (SLO fourni et solutions, pas les squelettes), `openspec validate --all` et le build des deux images sans publication.
- Images : `.github/workflows/image.yml` rejoue cette CI, puis publie à chaque push sur `main` (`app/`, `web/`, `Dockerfile`) les images amd64 + arm64 `akhilian/docshare` et `akhilian/docshare-web` sur Docker Hub, taguées par SHA complet et `latest`. Secret de dépôt requis : `DOCKERHUB_TOKEN`.
- Spécifications et plan de travail : `openspec/` (`openspec list`, `openspec show <change>`).
