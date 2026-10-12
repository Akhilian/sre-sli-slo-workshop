# service-metrics Specification

## Purpose
TBD - created by archiving change add-docshare-app. Update Purpose after archive.
## Requirements
### Requirement: Métriques par parcours
Chaque rôle SHALL exposer au format Prometheus les métriques de son parcours, et uniquement celles-ci :

| Parcours | Métriques | Rôle |
| --- | --- | --- |
| Upload | `http_requests_total{route,status}`, `http_request_duration_seconds{route}` | api |
| Traitement | `jobs_processed_total{status}`, `queue_depth`, `document_processing_delay_seconds` | worker |
| Recherche | `search_requests_total{status}`, `search_results_count`, `search_fallback_total` | api |
| Notifications | `notifications_enqueued_total` | worker |
| Notifications | `notifications_sent_total{status}`, `notification_delay_seconds` | notifier |

#### Scenario: Scrape de l'API
- **WHEN** Prometheus interroge `GET /metrics` sur l'API
- **THEN** la réponse contient les métriques d'upload et de recherche

#### Scenario: Scrape du worker
- **WHEN** Prometheus interroge le port `metrics` du worker
- **THEN** la réponse contient les métriques de traitement et `notifications_enqueued_total`

### Requirement: Buckets alignés sur les seuils de l'exercice
Les histogrammes SHALL utiliser exactement ces buckets :
- `http_request_duration_seconds` : 0.1, 0.3, 1, 3
- `document_processing_delay_seconds` : 10, 60, 300, 900
- `search_results_count` : 0, 1, 5, 20
- `notification_delay_seconds` : 1, 5, 30, 120

`prometheus_client` écrit les bornes au format flottant : les requêtes PromQL MUST utiliser `le="0.0"`, `le="0.3"`, `le="1.0"`, `le="60.0"`, etc.

#### Scenario: Part de recherches sans résultat calculable
- **WHEN** on interroge `search_results_count_bucket{le="0.0"}` et `search_results_count_count`
- **THEN** les deux séries existent et leur ratio donne la part de recherches vides

#### Scenario: SLI de latence calculable
- **WHEN** on interroge `http_request_duration_seconds_bucket{route="/documents",le="0.3"}`
- **THEN** la série existe

### Requirement: Cardinalité maîtrisée
Le label `route` SHALL contenir le modèle de route (par exemple `/documents/{id}`), jamais le chemin réel. `/metrics`, `/healthz` et `/admin/faults` MUST NOT être instrumentés.

#### Scenario: Consultation de plusieurs documents
- **WHEN** des clients consultent 1000 documents différents
- **THEN** une seule série `http_requests_total{route="/documents/{id}",status="200"}` existe

### Requirement: Source unique de la taille de file
`queue_depth` SHALL être exposée par le worker uniquement.

#### Scenario: Pas de doublon
- **WHEN** on interroge `queue_depth` dans un namespace
- **THEN** une seule série est renvoyée (un seul worker)

### Requirement: Absence volontaire de métriques
L'application MUST NOT exposer de métriques côté client, ni de métriques supplémentaires utiles au diagnostic (CPU du worker, etc.) : leur absence fait partie de l'exercice.

#### Scenario: Revue des métriques exposées
- **WHEN** on liste les métriques métier exposées par les trois rôles
- **THEN** on retrouve exactement celles du tableau des métriques par parcours (hors métriques par défaut du runtime Python)

### Requirement: Un seul processus par conteneur API
L'API SHALL tourner avec un seul worker uvicorn, pour que `prometheus_client` fonctionne sans mode multiprocess. La montée en charge MUST se faire par réplicas.

#### Scenario: Compteurs cohérents
- **WHEN** on envoie 100 requêtes à un pod API
- **THEN** `http_requests_total` de ce pod augmente de 100

