## Why

Le code de DocShare mélange dans les mêmes fonctions la logique métier, l'accès à Postgres et Redis, les métriques Prometheus et l'injection des pannes. Il est court, mais difficile à tester sans infrastructure, et une équipe qui cherche d'où vient une panne doit la repérer au milieu du code métier. Une architecture hexagonale (ports et adaptateurs) sépare ces responsabilités, rend chaque panne visible à un seul endroit et permet des tests unitaires sans Redis ni Postgres.

## What Changes

- Réorganisation de `app/` en trois couches :
  - `domain/` : modèles, ports (`Protocol`) et cas d'usage, sans dépendance à FastAPI, psycopg, redis ni prometheus_client ;
  - `adapters/` : Postgres, Redis, OCR et envoi d'e-mails simulés, pannes, métriques ;
  - `entrypoints/` : application FastAPI, boucles du worker et du notifier.
- Câblage explicite dans `bootstrap.py` ; FastAPI reçoit ses cas d'usage par `Depends`, via une fabrique `create_app()`.
- Chaque panne devient un décorateur d'un port, regroupé dans `adapters/faults.py`, sans changer son effet.
- Toutes les métriques Prometheus sont déclarées dans `adapters/metrics.py`.
- Nouveau rôle `standalone` : l'API, le worker et le notifier tournent dans un seul processus, sur des adaptateurs en mémoire, sans Redis ni Postgres. Il sert à découvrir l'application ou à préparer une démo sur un poste, sans cluster.
- Ajout de tests unitaires (`tests/`, pytest) sur des adaptateurs en mémoire, et d'un job de tests dans la CI.
- Aucun autre changement visible : mêmes routes, mêmes réponses, mêmes rôles distribués, mêmes métriques, mêmes effets de pannes. L'image, le chart, les SLO et les dashboards restent inchangés.

## Capabilities

### New Capabilities
- `code-architecture` : découpage en couches, pannes portées par des décorateurs de ports, contrat d'observation inchangé, tests unitaires sans infrastructure.
- `standalone-mode` : exécution de toute l'application dans un processus, sur des adaptateurs en mémoire.

### Modified Capabilities
- `document-pipeline` : la variable `ROLE` accepte aussi `standalone`.

Les exigences de `fault-injection` et `service-metrics` restent valables telles quelles et servent de contrat de non-régression, y compris en mode `standalone`.

## Impact

- Code : tout `app/` est réécrit ; `api.py`, `worker.py`, `notifier.py`, `db.py`, `jobqueue.py` et `faults.py` disparaissent au profit de la nouvelle arborescence. `main.py` reste le point d'entrée de l'image.
- Nouveaux fichiers : `tests/`, `app/requirements-dev.txt` (pytest, httpx), configuration pytest.
- CI : `.github/workflows/image.yml` lance les tests avant la construction de l'image.
- Documentation : section « Lancer l'application en local » du README (une seule commande `docker run` en mode `standalone`, l'actuelle pile à cinq conteneurs restant décrite), section « Développement », et renvoi vers `adapters/faults.py` et `adapters/metrics.py` pour les équipes.
- Les changes actifs `add-traffic-and-runbook` et `add-k8s-deployment` ne sont pas affectés.
