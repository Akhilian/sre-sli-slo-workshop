## ADDED Requirements

### Requirement: Pannes pilotées par Redis
Chaque rôle SHALL lire le hash Redis `faults` avant chaque traitement, sans redémarrage. `POST /admin/faults` MUST permettre d'activer une panne (`{"name": ..., "value": ...}`) ou de la couper (valeur `0` ou suppression).

#### Scenario: Activation à chaud
- **WHEN** l'animateur envoie `POST /admin/faults` avec `upload_latency=2.0`
- **THEN** l'upload suivant subit le délai, sans redémarrage d'aucun pod

#### Scenario: Coupure
- **WHEN** l'animateur coupe la panne
- **THEN** les requêtes suivantes retrouvent un comportement nominal

#### Scenario: Panne inconnue
- **WHEN** `POST /admin/faults` reçoit un nom qui n'est pas dans la liste des pannes
- **THEN** l'API répond 422

### Requirement: Panne de latence d'upload
`upload_latency=<secondes>` SHALL ajouter ce délai à chaque `POST /documents`. Elle MUST dégrader le SLI de latence et MUST laisser intacts les SLI de disponibilité, fraîcheur, qualité et couverture.

#### Scenario: Latence au-delà des seuils
- **WHEN** `upload_latency=2.0` est active
- **THEN** les uploads tombent dans le bucket `le="3.0"` et hors des buckets `le="0.3"` et `le="1.0"`, tout en répondant 202

### Requirement: Panne d'erreurs d'upload
`upload_error_rate=<proportion>` SHALL faire répondre 5xx à cette proportion d'uploads, **avant** l'INSERT et la mise en file. Elle MUST dégrader le SLI de disponibilité et MUST laisser intacts les autres SLI.

#### Scenario: Pas de document fantôme
- **WHEN** `upload_error_rate=0.5` est active et qu'un upload reçoit 500
- **THEN** aucun document ni job n'a été créé pour cette requête

#### Scenario: Proportion respectée
- **WHEN** `upload_error_rate=0.5` est active pendant 1000 uploads
- **THEN** environ la moitié répondent 5xx

### Requirement: Panne de lenteur du worker
`worker_slow=<facteur>` SHALL multiplier la durée de traitement de chaque job. Elle MUST dégrader le SLI de fraîcheur et MUST laisser intacts les SLI de disponibilité, latence et qualité.

#### Scenario: File qui s'engorge
- **WHEN** `worker_slow=10` est active avec 1 upload/s
- **THEN** `queue_depth` augmente, des observations de `document_processing_delay_seconds` dépassent 60 s, et l'API continue de répondre 202

### Requirement: Panne d'index périmé
`stale_index=1` SHALL faire passer les documents à `done` sans écrire leur `tsvector`. Elle MUST dégrader le SLI de qualité et MUST laisser intacts les SLI de disponibilité, latence et fraîcheur.

#### Scenario: Recherche vide mais en succès
- **WHEN** `stale_index=1` est active et qu'on cherche le jeton d'un document passé `done` pendant la panne
- **THEN** la recherche répond 200 avec 0 résultat et `search_results_count` est observé à 0

### Requirement: Panne de perte de notifications
`notifier_drop=<proportion>` SHALL faire perdre silencieusement cette proportion de notifications : aucune erreur, aucun log, aucune incrémentation de `notifications_sent_total`. Elle MUST dégrader le SLI de couverture (envoyées / mises en file) et MUST laisser intacts les autres SLI.

#### Scenario: Perte silencieuse
- **WHEN** `notifier_drop=0.2` est active
- **THEN** `notifications_sent_total` croît environ 20 % moins vite que `notifications_enqueued_total`, et les logs du notifier ne mentionnent aucune perte
