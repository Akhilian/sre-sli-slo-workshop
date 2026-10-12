## Context

Premier change du projet : rien n'existe encore. L'application est un support pédagogique : un participant doit pouvoir lire le code d'un rôle en quelques minutes. Elle sera déployée sur Kubernetes (change `add-k8s-deployment`), une pile par namespace d'équipe, mais doit rester exécutable avec un simple `docker run` + Redis + Postgres pour le développement.

## Goals / Non-Goals

**Goals:**
- Un parcours complet upload → traitement → recherche → notification, observable par métriques.
- Cinq pannes pilotables à chaud, chacune visible par un seul type de SLI.
- Comportement prévisible sous charge (capacité du worker connue), pour que le calibrage des pannes tienne.

**Non-Goals:**
- Stockage réel des fichiers, OCR réel, envoi réel de notifications.
- Authentification, y compris sur `/admin/faults` (l'isolation vient des namespaces et du `port-forward`).
- Haute disponibilité, performances.
- Toute métrique au-delà de la liste imposée.

## Decisions

**Structure du code.** `app/main.py` lit `ROLE` et appelle `api.run()`, `worker.run()` ou `notifier.run()`. Modules partagés : `faults.py` (lecture du hash), `db.py` (connexion avec réessais, schéma), `jobqueue.py` (Redis ; pas `queue.py`, qui masquerait le module standard utilisé par `concurrent.futures`). Un fichier par rôle, sans framework de DI ni ORM : du SQL lisible.
Alternative écartée : trois images. Plus de build et de CI pour aucun bénéfice pédagogique.

**File de jobs.** Listes Redis `jobs` et `notifications`, `BRPOP` côté consommateur. Le message contient l'`id` et la date d'upload.
Alternative écartée : Redis Streams. Accusés de réception et groupes inutiles ici, et plus difficiles à lire.

**Concurrence du worker.** `WORKER_CONCURRENCY` threads (4 par défaut) qui font chacun leur `BRPOP`. Capacité ≈ 4 / 2 s = 2 jobs/s, soit ~50 % de charge pour 1 upload/s. `worker_slow=10` ramène la capacité à ~0.2 job/s : l'attente croît d'environ 4 s par seconde, le seuil de 60 s est franchi en moins d'une minute.
Alternative écartée : asyncio. Moins lisible pour le public visé.

**Indexation explicite.** Colonne `search_vector tsvector` nulle à l'INSERT, remplie par le worker (`UPDATE documents SET search_vector = to_tsvector('simple', title || ' ' || content), status = 'done'`). Configuration `simple` pour que les jetons uniques (`doc-xxxx`) soient indexés tels quels. Index GIN sur la colonne.
Alternative écartée : colonne générée. L'indexation aurait lieu à l'INSERT et `stale_index` serait sans effet.

**Lecture des pannes.** `HGETALL faults` à chaque requête ou job, sans cache. Coût négligeable au débit du workshop et effet immédiat. Les valeurs sont des nombres ; une valeur absente vaut 0. Le tirage aléatoire (`random.random() < rate`) suffit pour les proportions.

**Ordre dans l'upload.** Lecture des pannes → `sleep(upload_latency)` → tirage `upload_error_rate` (réponse 500) → INSERT → `LPUSH` → 202. La latence est donc aussi appliquée aux réponses en erreur, ce qui est réaliste.

**Métriques.** Middleware FastAPI qui utilise le modèle de route (`request.scope["route"].path`) pour le label `route` et exclut `/metrics`, `/healthz`, `/admin/faults`. Worker et notifier : `start_http_server(METRICS_PORT)` (9100 par défaut). `queue_depth` est calculée par le worker au moment du scrape (`Gauge.set_function` sur `LLEN jobs`). Séries `*_created` désactivées pour alléger `/metrics`.

**Repli de recherche.** `try/except` autour de la requête Postgres avec un `statement_timeout` de 2 s ; en cas d'échec, 200 + liste vide + `search_fallback_total`. Le statut enregistré dans `search_requests_total{status}` est alors `"fallback"`.

**Image et CI.** `python:3.12-slim`, dépendances figées dans `requirements.txt`, utilisateur non root. `docker/build-push-action` avec `platforms: linux/amd64,linux/arm64` vers `ghcr.io/<owner>/docshare`.

## Risks / Trade-offs

- [`/admin/faults` sans authentification] → acceptable : accessible uniquement par `port-forward` dans le namespace de l'équipe ; à rappeler dans le README.
- [Bruit statistique à faible débit sur les proportions] → débits k6 choisis en conséquence (change `add-traffic-and-runbook`) ; `upload_error_rate=0.5` reste nettement visible.
- [Biais du survivant sur la fraîcheur : un job bloqué n'est observé qu'à la fin] → assumé et présenté au débrief ; ne pas ajouter de métrique d'âge du plus vieux job.
- [Threads + `prometheus_client`] → les compteurs sont thread-safe, pas de risque.

## Open Questions

- Nom du compte `ghcr.io` (organisation ou compte personnel) et visibilité publique du package.
