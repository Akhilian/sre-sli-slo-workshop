## Why

Le workshop SLI / SLO a besoin d'un système réaliste mais lisible, sur lequel des développeurs sans connaissance SRE peuvent définir des SLI puis observer de vraies pannes. DocShare est ce système : il doit exister avant tout le reste (déploiement, SLO, trafic), car toutes les métriques et toutes les pannes du workshop en dépendent.

## What Changes

- Création d'une application Python unique (FastAPI + `prometheus_client`) avec trois rôles choisis par la variable `ROLE` : `api`, `worker`, `notifier`.
- Parcours de bout en bout : upload (202), traitement asynchrone simulant l'OCR et indexant le document, notification simulée.
- Endpoints : `POST /documents`, `GET /documents/{id}`, `GET /search?q=`, `POST /admin/faults`, `GET /healthz`, `GET /metrics`.
- Métriques Prometheus par parcours, avec des buckets alignés sur les seuils de l'exercice (dont `le="0"` pour la qualité de recherche).
- Injection de pannes à chaud via un hash Redis `faults` : `upload_latency`, `upload_error_rate`, `worker_slow`, `stale_index`, `notifier_drop`.
- Comportements nécessaires sur Kubernetes, mais aussi utiles en local : démarrage robuste (réessais, schéma idempotent), sonde insensible aux pannes, port de métriques nommé pour le worker et le notifier.
- Image Docker multi-arch (amd64 + arm64) publiée sur `ghcr.io` par un workflow GitHub Actions.

## Capabilities

### New Capabilities
- `document-pipeline` : flux upload → traitement → indexation → notification, endpoints de l'API, démarrage et sondes.
- `service-metrics` : métriques exposées par chaque rôle, labels, buckets, et ce qui ne doit volontairement pas être exposé.
- `fault-injection` : pannes pilotées par Redis, effet de chacune et SLI qu'elle doit (ou ne doit pas) dégrader.
- `container-image` : image unique multi-arch et sa publication.

### Modified Capabilities

Aucune.

## Impact

- Nouveau code : `app/`, `Dockerfile`, `.github/workflows/image.yml`.
- Dépendances : FastAPI, uvicorn, `prometheus_client`, `redis`, `psycopg`.
- Services requis à l'exécution : Redis et Postgres (fournis par le change `add-k8s-deployment` ; un `docker run` local suffit pour développer).
- Socle des changes suivants : `add-k8s-deployment`, `add-slo-and-dashboards`, `add-traffic-and-runbook`.
