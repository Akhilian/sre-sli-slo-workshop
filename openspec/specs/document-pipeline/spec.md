# document-pipeline Specification

## Purpose
TBD - created by archiving change add-docshare-app. Update Purpose after archive.
## Requirements
### Requirement: Rôle choisi par variable d'environnement
L'application SHALL être une seule base de code et une seule image, dont le comportement est choisi par la variable `ROLE` (`api`, `worker` ou `notifier`).

#### Scenario: Démarrage d'un rôle
- **WHEN** le conteneur démarre avec `ROLE=worker`
- **THEN** le processus dépile la file de jobs et n'expose pas l'API HTTP métier

#### Scenario: Rôle inconnu
- **WHEN** le conteneur démarre avec un `ROLE` absent ou inconnu
- **THEN** le processus s'arrête avec un code de sortie non nul et un message explicite

### Requirement: Upload asynchrone
`POST /documents` SHALL accepter un titre et un contenu texte, insérer le document en base avec le statut `pending`, pousser un job dans Redis, et répondre 202 avec l'`id` du document.

#### Scenario: Upload nominal
- **WHEN** un client envoie `POST /documents` avec un titre et un contenu
- **THEN** l'API répond 202 avec un `id`, et `GET /documents/{id}` renvoie le statut `pending` ou `done`

#### Scenario: Requête invalide
- **WHEN** un client envoie `POST /documents` sans contenu
- **THEN** l'API répond 422 et aucun document n'est créé

### Requirement: Traitement par le worker
Le worker SHALL dépiler chaque job, simuler l'OCR par une attente de 1 à 3 s, écrire explicitement le `tsvector` du document, passer le statut à `done`, observer `document_processing_delay_seconds` (maintenant moins date d'upload), puis pousser un message de notification. Le worker MUST traiter jusqu'à `WORKER_CONCURRENCY` jobs en parallèle (4 par défaut).

#### Scenario: Document traité et indexé
- **WHEN** un document est uploadé et qu'aucune panne n'est active
- **THEN** en quelques secondes son statut passe à `done` et une recherche sur un mot de son contenu le renvoie

#### Scenario: Indexation non automatique
- **WHEN** un document est inséré en base mais pas encore traité par le worker
- **THEN** il n'apparaît dans aucun résultat de recherche (pas de colonne générée ni de trigger d'indexation)

### Requirement: Notification simulée
Le notifier SHALL dépiler les messages de notification et simuler leur envoi, sans appel externe.

#### Scenario: Notification envoyée
- **WHEN** le worker a poussé un message de notification
- **THEN** le notifier le dépile et le compte comme envoyé

### Requirement: Consultation et recherche
`GET /documents/{id}` SHALL renvoyer le statut et les métadonnées du document, ou 404 s'il n'existe pas. `GET /search?q=` SHALL effectuer une recherche plein texte Postgres sur le `tsvector` et renvoyer la liste des documents trouvés.

#### Scenario: Document inexistant
- **WHEN** un client demande un `id` inconnu
- **THEN** l'API répond 404

#### Scenario: Échec de la base pendant une recherche
- **WHEN** la requête Postgres de recherche lève une exception ou expire
- **THEN** l'API répond 200 avec une liste vide et incrémente `search_fallback_total`

### Requirement: Démarrage robuste
Chaque rôle SHALL réessayer la connexion à Redis et à Postgres au démarrage au lieu d'échouer, et l'API MUST créer le schéma de façon idempotente.

#### Scenario: Base indisponible au démarrage
- **WHEN** l'API démarre avant Postgres
- **THEN** elle réessaie jusqu'à ce que Postgres réponde, puis crée le schéma s'il n'existe pas

#### Scenario: Redémarrage avec schéma existant
- **WHEN** l'API redémarre alors que le schéma existe déjà
- **THEN** elle démarre sans erreur et sans perte de données

### Requirement: Sonde de santé insensible aux pannes
L'API SHALL exposer `GET /healthz`, qui ne lit pas le hash `faults`. Le worker et le notifier MUST pouvoir être sondés via leur port de métriques.

#### Scenario: Sonde pendant une panne de latence
- **WHEN** `upload_latency=2.0` est active
- **THEN** `GET /healthz` répond 200 sans délai ajouté

