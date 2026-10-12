# DocShare

Système fictif de partage de documents, support d'un workshop SLI / SLO de 2 h. Les participants partent d'un SLI fonctionnel, l'implémentent en SLO avec Sloth, puis regardent le budget d'erreur brûler pendant de vraies pannes.

> État actuel : seule l'application existe. Le déploiement Kubernetes, les SLO, les dashboards et le trafic k6 arrivent dans les changes OpenSpec suivants (`openspec list`). Ce README sera complété au fur et à mesure.

## Architecture

Une seule image, trois rôles choisis par la variable `ROLE` :

```
client ──POST /documents──▶ api ──LPUSH jobs──▶ Redis ──BRPOP──▶ worker ──LPUSH notifications──▶ Redis ──BRPOP──▶ notifier
                             │                                     │
                             └──────────── Postgres ◀──────────────┘
                               (documents + index plein texte)
```

1. `api` insère le document (statut `pending`), le met en file et répond 202.
2. `worker` simule l'OCR (1 à 3 s), indexe le document, le passe en `done` et demande une notification.
3. `notifier` « envoie » la notification (simulé).

## Lancer l'application en local

Prérequis : Docker.

```bash
docker build -t docshare:dev .
docker network create docshare

docker run -d --name redis --network docshare redis:7.4-alpine
docker run -d --name postgres --network docshare \
  -e POSTGRES_USER=docshare -e POSTGRES_PASSWORD=docshare -e POSTGRES_DB=docshare \
  postgres:16-alpine

docker run -d --name api --network docshare -p 8000:8000 -e ROLE=api \
  -e REDIS_URL=redis://redis:6379/0 \
  -e DATABASE_URL=postgresql://docshare:docshare@postgres:5432/docshare \
  docshare:dev
docker run -d --name worker --network docshare -p 9100:9100 -e ROLE=worker \
  -e REDIS_URL=redis://redis:6379/0 \
  -e DATABASE_URL=postgresql://docshare:docshare@postgres:5432/docshare \
  docshare:dev
docker run -d --name notifier --network docshare -p 9101:9100 -e ROLE=notifier \
  -e REDIS_URL=redis://redis:6379/0 \
  docshare:dev
```

L'ordre de démarrage n'a pas d'importance : chaque rôle réessaie toutes les 2 s tant que Redis ou Postgres ne répond pas, et l'API crée le schéma au démarrage.

> Piège zsh : ne factorisez pas les options dans une variable (`E="-e A=1 -e B=2"; docker run $E ...`). zsh ne découpe pas la variable en mots et Docker reçoit une seule option mal formée. Écrivez les `-e` en entier comme ci-dessus.

Arrêt et nettoyage :

```bash
docker rm -f api worker notifier redis postgres && docker network rm docshare
```

### Configuration

| Variable | Rôles | Défaut | Rôle |
| --- | --- | --- | --- |
| `ROLE` | tous | (obligatoire) | `api`, `worker` ou `notifier` ; toute autre valeur arrête le processus |
| `REDIS_URL` | tous | `redis://localhost:6379/0` | files de jobs et hash des pannes |
| `DATABASE_URL` | api, worker | `postgresql://docshare:docshare@localhost:5432/docshare` | documents et index |
| `PORT` | api | `8000` | port HTTP de l'API (métriques comprises) |
| `METRICS_PORT` | worker, notifier | `9100` | port des métriques, utilisable aussi comme sonde |
| `WORKER_CONCURRENCY` | worker | `4` | jobs traités en parallèle (capacité ≈ 2 jobs/s) |

## Utiliser l'API

| Endpoint | Rôle |
| --- | --- |
| `POST /documents` | upload `{"title", "content"}`, répond 202 avec l'`id` (422 si un champ est vide) |
| `GET /documents/{id}` | statut (`pending` / `done`) et métadonnées, 404 si inconnu |
| `GET /search?q=` | recherche plein texte, 20 résultats au plus |
| `GET /admin/faults` | pannes actives |
| `POST /admin/faults` | active ou coupe une panne |
| `GET /healthz` | sonde, insensible aux pannes |
| `GET /metrics` | métriques Prometheus de l'API |

```bash
# Upload
curl -s -X POST localhost:8000/documents -H 'content-type: application/json' \
  -d '{"title": "Facture", "content": "facture électricité doc-abc12345"}'
# {"id":1}

# Statut : pending, puis done après 1 à 3 s
curl -s localhost:8000/documents/1

# Recherche : le document n'est trouvé qu'une fois traité par le worker
curl -s 'localhost:8000/search?q=doc-abc12345'
```

Si Postgres ne répond pas pendant une recherche, l'API renvoie quand même 200 avec une liste vide et incrémente `search_fallback_total`. C'est volontaire : un 200 n'est pas forcément un succès.

## Métriques

| Rôle | URL | Métriques |
| --- | --- | --- |
| api | `localhost:8000/metrics` | `http_requests_total{route,status}`, `http_request_duration_seconds{route}`, `search_requests_total{status}`, `search_results_count`, `search_fallback_total` |
| worker | `localhost:9100/metrics` | `jobs_processed_total{status}`, `queue_depth`, `document_processing_delay_seconds`, `notifications_enqueued_total` |
| notifier | `localhost:9101/metrics` | `notifications_sent_total{status}`, `notification_delay_seconds` |

Buckets des histogrammes, alignés sur les seuils de l'exercice :

| Histogramme | Buckets |
| --- | --- |
| `http_request_duration_seconds` | 0.1, 0.3, 1, 3 s |
| `document_processing_delay_seconds` | 10, 60, 300, 900 s |
| `search_results_count` | 0, 1, 5, 20 |
| `notification_delay_seconds` | 1, 5, 30, 120 s |

Points d'attention pour écrire les requêtes PromQL :
- Les bornes sont écrites au format flottant : `le="0.0"`, `le="0.3"`, `le="1.0"`, `le="60.0"`. Une requête sur `le="0"` ou `le="60"` ne renvoie rien.
- Le label `route` contient le modèle de route (`/documents/{id}`), jamais l'identifiant réel.
- `/metrics`, `/healthz`, `/admin/faults` et les URL inconnues ne sont pas mesurés.
- Il n'y a volontairement ni métrique côté client, ni métrique de diagnostic supplémentaire : leur absence fait partie de l'exercice.

## Pannes

Les pannes sont stockées dans le hash Redis `faults` et relues à chaque requête ou job : elles s'appliquent immédiatement, sans redémarrage.

```bash
# Activer
curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' \
  -d '{"name": "worker_slow", "value": 10}'
# Couper (valeur 0)
curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' \
  -d '{"name": "worker_slow", "value": 0}'
# Lister les pannes actives
curl -s localhost:8000/admin/faults
```

| Panne | Valeur | Effet | SLI dégradé | SLI intacts |
| --- | --- | --- | --- | --- |
| `upload_latency` | secondes, ex. `2.0` | délai ajouté à chaque upload | latence | disponibilité, fraîcheur, qualité, couverture |
| `upload_error_rate` | proportion, `0.02` puis `0.5` | uploads en 500, avant toute écriture (aucun document fantôme) | disponibilité | latence, fraîcheur, qualité, couverture |
| `worker_slow` | facteur, ex. `10` | traitement 10 fois plus lent, la file s'engorge | fraîcheur | disponibilité, latence, qualité |
| `stale_index` | `1` | documents marqués `done` sans être indexés : recherche en 200 avec 0 résultat | qualité | disponibilité, latence, fraîcheur |
| `notifier_drop` | proportion, ex. `0.2` | notifications perdues sans erreur, sans log, sans compteur | couverture | disponibilité, latence, fraîcheur, qualité |

Effets mesurés en local :

| Panne | Mesure |
| --- | --- |
| `upload_latency=2.0` | upload en 2,01 s ; `/healthz` en 2 ms |
| `upload_error_rate=0.5` | 93 erreurs sur 200 uploads, aucun document créé pour ces requêtes |
| `worker_slow=10` à 1 upload/s | uploads toujours en 202 ; au bout de 2 min, file à 92 jobs et premiers documents traités en plus de 60 s |
| `stale_index=1` | document `done` mais introuvable ; de nouveau trouvable après la coupure |
| `notifier_drop=0.2` | 18,7 % de notifications perdues sur 300, aucune ligne de log |

Une panne à la fois. Après `worker_slow`, la file met du temps à se vider (environ 1 min pour 100 jobs en attente). Attendez que `queue_depth` revienne à 0 avant la panne suivante, sinon le retard hérité fausse ce qu'elle montre.

## Développement

- Code : `app/` (`main.py` aiguille vers `api.py`, `worker.py` ou `notifier.py` ; `db.py`, `jobqueue.py` et `faults.py` sont partagés).
- Image : `.github/workflows/image.yml` publie à chaque push sur `main` une image amd64 + arm64 sur `ghcr.io/<owner>/docshare`, taguée par SHA et `latest`.
- Spécifications et plan de travail : `openspec/` (`openspec list`, `openspec show <change>`).
