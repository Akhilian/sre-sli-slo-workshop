## 1. Squelette

- [x] 1.1 Créer `app/` avec `main.py` (aiguillage sur `ROLE`, arrêt explicite si inconnu), `requirements.txt` et un `Dockerfile` (python 3.12 slim, utilisateur non root)
- [x] 1.2 Écrire `db.py` : connexion Postgres avec réessais, création idempotente du schéma (`documents` avec `search_vector` nullable et index GIN)
- [x] 1.3 Écrire `jobqueue.py` : connexion Redis avec réessais, `push` / `pop` bloquant sur les listes `jobs` et `notifications`
- [x] 1.4 API FastAPI minimale avec `/healthz` et `/metrics`, servie par uvicorn avec un seul worker

## 2. Parcours de bout en bout

- [x] 2.1 `POST /documents` : validation, INSERT `pending`, `LPUSH jobs`, réponse 202 avec `id`
- [x] 2.2 `GET /documents/{id}` : statut et métadonnées, 404 si absent
- [x] 2.3 Worker : `WORKER_CONCURRENCY` threads, `sleep` 1 à 3 s, écriture du `tsvector` (config `simple`), statut `done`, `LPUSH notifications`
- [x] 2.4 Notifier : dépile et simule l'envoi
- [x] 2.5 `GET /search?q=` : `plainto_tsquery('simple', q)`, `statement_timeout` 2 s, repli 200 + liste vide en cas d'échec
- [x] 2.6 Vérifier en local (Redis et Postgres en conteneurs) : un upload passe `done` et son jeton est trouvé par la recherche

## 3. Métriques

- [x] 3.1 Middleware HTTP : `http_requests_total{route,status}` et `http_request_duration_seconds{route}` (buckets 0.1, 0.3, 1, 3), label `route` = modèle de route, exclusions
- [x] 3.2 Recherche : `search_requests_total{status}`, `search_results_count` (buckets 0, 1, 5, 20), `search_fallback_total`
- [x] 3.3 Worker : `start_http_server`, `jobs_processed_total{status}`, `queue_depth`, `document_processing_delay_seconds` (buckets 10, 60, 300, 900), `notifications_enqueued_total`
- [x] 3.4 Notifier : `start_http_server`, `notifications_sent_total{status}`, `notification_delay_seconds` (buckets 1, 5, 30, 120)
- [x] 3.5 Vérifier que la liste des métriques métier exposées correspond exactement à la spec et que `route` ne contient jamais d'`id`

## 4. Injection de pannes

- [x] 4.1 `faults.py` : lecture `HGETALL faults` sans cache, valeurs numériques, 0 par défaut
- [x] 4.2 `POST /admin/faults` : activation / coupure, 422 sur nom inconnu
- [x] 4.3 `upload_latency` et `upload_error_rate` dans l'upload, erreur avant l'INSERT
- [x] 4.4 `worker_slow` (multiplie le `sleep`) et `stale_index` (statut `done` sans `tsvector`) dans le worker
- [x] 4.5 `notifier_drop` : perte silencieuse, sans log ni incrémentation
- [x] 4.6 Vérifier en local chaque panne : effet attendu présent, `/healthz` inchangé, coupure efficace

## 5. Image

- [x] 5.1 Workflow `.github/workflows/image.yml` : build multi-arch amd64 + arm64, push sur `ghcr.io` avec tags SHA et `latest`
- [x] 5.2 Vérifier que l'image démarre en arm64 (Mac) et en amd64 pour les trois rôles

## 6. Documentation

- [x] 6.1 `README.md` minimal limité à l'application : lancement local, configuration, endpoints, métriques et format des bornes `le`, pannes et effets mesurés
- [x] 6.2 Vérifier que les commandes du README fonctionnent telles quelles (bash et zsh)
