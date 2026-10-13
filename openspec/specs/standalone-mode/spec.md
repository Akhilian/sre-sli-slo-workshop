# standalone-mode Specification

## Purpose
TBD - created by archiving change refactor-hexagonal-architecture. Update Purpose after archive.
## Requirements
### Requirement: Application complète dans un seul processus
Avec `ROLE=standalone`, le processus SHALL démarrer l'API HTTP, `WORKER_CONCURRENCY` threads de worker et un thread de notifier, reliés par des adaptateurs en mémoire : dépôt de documents, index de recherche, files de jobs et de notifications, pannes. Il MUST démarrer sans Redis ni Postgres et sans lire `REDIS_URL` ni `DATABASE_URL`.

#### Scenario: Parcours complet sans infrastructure
- **WHEN** on lance `docker run -p 8000:8000 -e ROLE=standalone docshare:dev`, puis qu'on envoie un upload
- **THEN** l'API répond 202, le document passe `done` en quelques secondes, et une recherche sur un mot de son contenu le renvoie

#### Scenario: Données éphémères
- **WHEN** le processus redémarre
- **THEN** les documents et les pannes actives sont perdus, et l'application démarre vide

### Requirement: Recherche en mémoire équivalente
L'index en mémoire SHALL découper titre et contenu en mots en minuscules, et renvoyer au plus 20 documents indexés contenant tous les mots de la requête, comme la configuration `simple` de Postgres pour les jetons utilisés par k6.

#### Scenario: Recherche d'un jeton
- **WHEN** un document contenant `doc-1a2b3c4d` est indexé et qu'on cherche `doc-1a2b3c4d`
- **THEN** la recherche renvoie ce document

#### Scenario: Document non indexé
- **WHEN** un document est passé `done` sous `stale_index=1`
- **THEN** la recherche de son jeton renvoie 0 résultat

### Requirement: Pannes et métriques en mode standalone
Les cinq pannes SHALL être pilotables par `/admin/faults` en mode `standalone`, avec les mêmes décorateurs et les mêmes effets qu'en mode distribué. `GET /metrics` de l'API MUST exposer les métriques des trois parcours (upload, traitement, recherche, notifications), avec les noms, labels et buckets de `service-metrics`.

#### Scenario: Panne de perte de notifications
- **WHEN** `notifier_drop=1` est active en mode `standalone` et qu'un document est traité
- **THEN** `notifications_enqueued_total` augmente et `notifications_sent_total` n'augmente pas

#### Scenario: Un seul point de scrape
- **WHEN** on interroge `GET /metrics` en mode `standalone`
- **THEN** la réponse contient `http_requests_total`, `queue_depth`, `search_results_count` et `notifications_sent_total`

