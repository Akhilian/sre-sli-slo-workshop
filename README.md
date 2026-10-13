# DocShare

DocShare est un système fictif de partage de documents servant de support à un atelier SLI/SLO de deux heures. Les participants observent l’effet de pannes réelles sur le parcours utilisateur, puis le mesurent avec Prometheus, Sloth et Grafana.

> Le backend, l’interface web, le déploiement Kubernetes, le trafic k6, les SLO et les dashboards sont présents. Le déroulé détaillé de la séance et les temps de réaction mesurés des alertes restent à finaliser ; voir `openspec list`.

## Démarrage rapide

Pour lancer le backend en mode autonome, sans Redis ni Postgres :

```bash
docker build -t docshare:dev .
docker run --rm -p 8000:8000 -e ROLE=standalone docshare:dev
```

## Interface web

```bash
# Développement : relais /api vers http://localhost:8000
cd web && npm install && npm run dev

# Image (nginx non root sur 8080), face au backend standalone
docker build -t docshare-web:dev web
docker run --rm -p 8080:8080 -e API_URL=http://host.docker.internal:8000 docshare-web:dev

# Dans le cluster, une interface par équipe
kubectl -n team-a port-forward svc/web 8080:80
```

Le pupitre de pannes de l’animateur apparaît avec `?admin` (`http://localhost:8080/?admin`). Les appels de l’interface passent par l’API et sont mesurés comme le reste du trafic : un participant qui enchaîne des recherches sans résultat fait monter le burn rate du SLI de qualité, ce qui est aussi un sujet de débrief. `web.enabled: false` retire l’interface du chart.

Le guide de [déploiement et d’exécution](docs/operations/deployment.md) décrit aussi le lancement sans Docker et les déploiements Kubernetes.

## Carte du dépôt

- `app/` : backend Python hexagonal — API, worker et notifier.
- `web/` : interface Vue/Vite et ses tests ; `tests/` contient les tests Python.
- `deploy/` : chart Helm, valeurs par environnement, configuration du monitoring et scripts d’installation.
- `observability/` : définitions SLO et solutions d’atelier, dashboards Grafana et générateur.
- `openspec/` : spécifications, changements en cours et archives.
- `docs/` : architecture et guides d’exploitation ; `docs/archive/` conserve le plan initial.
- `.github/`, `.claude/` et `.impeccable/` : intégrations GitHub, outils d’assistance et espace de travail design.

## Guides

- [Architecture](docs/architecture.md)
- [Déploiement et exécution](docs/operations/deployment.md)
- [Déroulé de la séance de 2 h](docs/operations/seance.md)
- [Observabilité et parcours de démonstration](docs/operations/observability.md)
- [Développement et tests](docs/operations/development.md)
- [Cadrage produit](docs/product.md)
- [Système visuel](docs/design/design-system.md)
- [Plan initial archivé](docs/archive/initial-architecture-plan.md)

Pour consulter les exigences et changements : `openspec list`, puis `openspec show <change>`.
