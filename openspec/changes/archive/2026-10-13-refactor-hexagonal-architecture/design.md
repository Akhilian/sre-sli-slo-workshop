## Context

`app/` compte environ 450 lignes en 7 fichiers. Chaque rôle (`api.py`, `worker.py`, `notifier.py`) mêle requêtes SQL, appels Redis, métriques et lecture des pannes. Le comportement est fixé par les specs `document-pipeline`, `fault-injection` et `service-metrics`, et les SLO Sloth, leurs solutions et les dashboards dépendent des noms exacts des métriques. Le code est lu par des développeurs pendant le workshop : il doit rester court et lisible.

## Goals / Non-Goals

**Goals:**
- Séparer domaine, adaptateurs et points d'entrée, avec des ports explicites.
- Regrouper les pannes dans un fichier, sous forme de décorateurs, et les métriques dans un autre.
- Rendre les cas d'usage et les pannes testables sans infrastructure.
- Faire tourner toute l'application sans Redis ni Postgres (`ROLE=standalone`), pour découvrir le code ou préparer une démo sur un poste.
- Ne rien changer d'autre de visible : routes, réponses, rôles, métriques, effets des pannes, image, chart.

**Non-Goals:**
- CQRS, événements de domaine, bus de messages, conteneur d'injection de dépendances.
- Passage en asynchrone (`async def` avec drivers asynchrones).
- Port de télémétrie : les métriques restent dans les points d'entrée et les adaptateurs.
- Tests d'intégration avec Postgres et Redis réels : la vérification de bout en bout reste faite sur le cluster.
- Mode `standalone` multi-processus ou persistant : il reste un seul processus, aux données éphémères.
- Déploiement du mode `standalone` par le chart : le workshop reste en mode distribué sur Kubernetes.

## Decisions

### Arborescence

```
app/
  main.py                 # inchangé : ROLE -> bootstrap
  bootstrap.py            # construit les adaptateurs et les cas d'usage par rôle
  domain/
    models.py             # Document, ProcessingJob, Notification (dataclasses)
    ports.py              # Protocols
    services.py           # cas d'usage
    errors.py             # DocumentNotFound, SearchUnavailable
  adapters/
    postgres.py           # PostgresDocuments (dépôt + indexation + recherche), schéma, attente
    redis.py              # RedisQueue, RedisFaultStore, attente
    simulated.py          # SimulatedOcr (1 à 3 s), SimulatedEmailSender (50 ms)
    faults.py             # décorateurs de pannes
    metrics.py            # toutes les métriques Prometheus
    memory.py             # adaptateurs en mémoire (mode standalone et tests)
  entrypoints/
    http.py               # create_app(), routes, MetricsMiddleware
    worker.py             # boucle du worker
    notifier.py           # boucle du notifier
    standalone.py         # API + threads worker et notifier dans un processus
tests/
```

`app/` reste la racine de l'image (`COPY app/ .`) : les paquets `domain`, `adapters` et `entrypoints` sont importés en absolu, comme aujourd'hui. Alternative écartée : un paquet `docshare/` englobant, qui ajoute un niveau d'imbrication sans bénéfice ici. `adapters/memory.py` est embarqué dans l'image : il sert au mode `standalone`.

### Ports

- `DocumentRepository` : `add(title, content) -> Document`, `get(id)`, `mark_done(id)`.
- `Indexer` : `index(id)`.
- `SearchIndex` : `search(query, limit) -> list[Document]`, lève `SearchUnavailable`.
- `JobQueue` et `NotificationQueue` : `push(message)`, `pop(timeout) -> message | None`, `length()`.
- `Ocr` : `extract(document_id)`.
- `EmailSender` : `send(notification)`.
- `FaultStore` : `current() -> dict[str, float]`, `set(name, value)`.

Les ports sont des `typing.Protocol` : pas d'héritage imposé aux adaptateurs. L'adaptateur Postgres implémente à lui seul `DocumentRepository`, `Indexer` et `SearchIndex`.

### Cas d'usage

- `UploadDocument` : `repository.add` puis `jobs.push`. Si `add` échoue, rien n'est mis en file.
- `GetDocument`, `SearchDocuments`.
- `ProcessDocument` : `ocr.extract`, puis `indexer.index`, puis `repository.mark_done`, puis `notifications.push`. Renvoie le délai depuis l'upload, que le point d'entrée observe dans `document_processing_delay_seconds`.
- `SendNotification` : `email.send`, renvoie le délai depuis la mise en file.

L'indexation passe avant `mark_done` : aujourd'hui les deux sont faites dans le même `UPDATE`. En les séparant dans l'autre ordre, k6 pourrait chercher un document `done` pas encore indexé, ce qui dégraderait le SLI de qualité sans panne.

### Pannes en décorateurs

Chaque décorateur reçoit le port décoré et le `FaultStore`, et relit les pannes à chaque appel :

| Décorateur | Port | Effet |
| --- | --- | --- |
| `FaultyDocumentRepository` | `DocumentRepository.add` | attend `upload_latency`, puis lève `InjectedFault` avec la probabilité `upload_error_rate`, avant d'appeler l'adaptateur réel. Les autres méthodes sont déléguées. |
| `SlowOcr` | `Ocr.extract` | mesure la durée de l'appel réel et attend `(worker_slow - 1)` fois cette durée : même distribution qu'aujourd'hui (`uniform(1, 3) * facteur`). |
| `StaleIndexer` | `Indexer.index` | ne fait rien quand `stale_index` est active. |
| `LossyNotificationQueue` | `NotificationQueue.pop` | consomme le message et renvoie `None` avec la probabilité `notifier_drop`. |

La perte de notifications est placée sur la file et non sur `EmailSender` : si `send` ne faisait rien, le point d'entrée compterait la notification comme envoyée et le SLI de couverture ne baisserait pas. Sur la file, le message disparaît avant d'atteindre le cas d'usage, comme une perte en transit.

`InjectedFault` est convertie en 500 par un gestionnaire d'exception FastAPI, avec le même corps qu'aujourd'hui. Le middleware de métriques voit donc toujours `status="500"`.

### Points d'entrée et FastAPI

- `create_app(services)` construit l'application. Les routes reçoivent leurs cas d'usage par `Depends`, depuis `app.state`. Les tests passent des services montés sur des adaptateurs en mémoire.
- `MetricsMiddleware` est conservé tel quel, dans `entrypoints/http.py`.
- Le repli de recherche reste dans le point d'entrée : `SearchUnavailable` donne un 200 vide, et incrémente `search_fallback_total` et `search_requests_total{status="fallback"}`. C'est un choix de présentation de l'API, pas une règle métier.
- Les routes restent en `def` synchrone : FastAPI les exécute dans son pool de threads, comme aujourd'hui.
- `queue_depth` reste lue à chaque scrape par `set_function`, branchée dans `bootstrap.py` sur `JobQueue.length` pour le seul rôle worker.

### Mode standalone

`ROLE=standalone` construit dans `bootstrap.py` un seul jeu d'adaptateurs en mémoire, partagé par les trois boucles :

- `InMemoryDocuments` : dictionnaire protégé par un verrou, implémente `DocumentRepository`, `Indexer` et `SearchIndex` ;
- `InMemoryQueue` : `queue.Queue` de la bibliothèque standard, dont `get(timeout=...)` donne le même comportement que `BRPOP` ;
- `InMemoryFaultStore` : dictionnaire.

Les décorateurs de pannes sont appliqués exactement comme en mode distribué. `entrypoints/standalone.py` démarre `WORKER_CONCURRENCY` threads de worker et un thread de notifier (en `daemon`), puis lance uvicorn au premier plan. Les boucles sont celles de `entrypoints/worker.py` et `entrypoints/notifier.py`, sans le serveur de métriques séparé : un seul registre Prometheus par processus, servi par `GET /metrics` de l'API. `queue_depth` n'existe qu'une fois.

La recherche découpe titre et contenu sur les caractères non alphanumériques (hors `-`) et met en minuscules, ce qui suffit pour les jetons `doc-xxxxxxxx` de k6 et pour une démo. Ce n'est pas une copie fidèle de `to_tsvector('simple')`, et ce n'est pas nécessaire.

Alternative écartée : une variable `STORAGE=memory` combinable avec chaque rôle. Un rôle `api` en mémoire ne pourrait pas parler à un `worker` dans un autre processus : seule la combinaison « tout dans un processus » a du sens, d'où un rôle dédié.

Le script k6 peut viser ce mode (`BASE_URL=http://localhost:8000`) pour générer du trafic sur un poste, mais sans Prometheus ni Sloth : `/metrics` se lit directement.

### Format des messages

`RedisQueue` sérialise en JSON avec les mêmes clés qu'aujourd'hui (`id`, `uploaded_at`, `enqueued_at`). Une API à jour et un worker ancien peuvent ainsi cohabiter pendant un déploiement progressif.

### Tests

- pytest et httpx dans `app/requirements-dev.txt`, hors image.
- `pytest.ini` à la racine avec `pythonpath = app`.
- Un `FaultStore` en mémoire pilote les pannes de manière déterministe : probabilité 0 ou 1, `random` injectable.
- Les temps d'attente sont injectables (`sleep`, horloge), pour que les tests ne dorment pas.
- Un test vérifie que `domain` s'importe avec `fastapi`, `psycopg`, `redis` et `prometheus_client` masqués dans `sys.modules`.

## Risks / Trade-offs

- [Une métrique change de nom ou de label sans que personne ne le voie] → test qui compare la liste des métriques exposées au tableau de `service-metrics`, puis diff de `/metrics` avant et après sur le cluster local.
- [Plus de fichiers pour un public qui découvre le code] → arborescence documentée dans le README, avec un renvoi direct vers `adapters/faults.py` et `adapters/metrics.py`.
- [Le comportement d'une panne change subtilement, par exemple la distribution de `worker_slow`] → tests unitaires par panne, puis scénario court des cinq pannes sur le cluster, comparé au tableau des burn rates du README.
- [Le mode `standalone` diverge du mode distribué, et une démo locale montre un comportement que le cluster n'a pas] → mêmes cas d'usage, mêmes décorateurs et mêmes boucles ; seuls les adaptateurs changent, et les tests de pannes tournent sur les adaptateurs en mémoire.
- [Mémoire qui grossit sans limite en mode `standalone` sous k6] → à 1 doc/s, quelques dizaines de Mo en plusieurs heures ; documenté comme éphémère, un redémarrage vide tout.
- [Deux requêtes SQL au lieu d'une pour terminer un document] → coût négligeable au débit du workshop (1 doc/s par équipe).

## Migration Plan

1. Écrire la nouvelle arborescence et les tests à côté de l'ancienne.
2. Basculer `main.py` sur `bootstrap.py`, puis supprimer les anciens modules.
3. Construire l'image `docshare:dev`, la déployer sur le k3s local, comparer `/metrics` et rejouer le scénario court des pannes.
4. Retour arrière : revert du commit, puisque l'image, le chart et les données ne changent pas.

## Open Questions

Aucune.
