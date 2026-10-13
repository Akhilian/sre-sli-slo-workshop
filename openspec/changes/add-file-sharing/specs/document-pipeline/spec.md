## MODIFIED Requirements

### Requirement: Upload asynchrone
`POST /documents` SHALL accepter un fichier en `multipart/form-data` (champ `file`) et un titre optionnel (champ `title`, par défaut le nom du fichier), enregistrer le document et son fichier avec le statut `pending`, pousser un job dans Redis, et répondre 202 avec l'`id` du document. Un fichier vide MUST être refusé en 422, un fichier de plus de 5 Mio en 413, sans création de document.

#### Scenario: Upload nominal
- **WHEN** un client envoie `POST /documents` avec un fichier `rapport.txt`
- **THEN** l'API répond 202 avec un `id`, et `GET /documents/{id}` renvoie le statut `pending` ou `done`, le titre `rapport.txt`, le nom, le type et la taille du fichier

#### Scenario: Requête invalide
- **WHEN** un client envoie `POST /documents` sans fichier, ou avec un fichier vide
- **THEN** l'API répond 422 et aucun document n'est créé

#### Scenario: Fichier trop gros
- **WHEN** un client envoie un fichier de 6 Mio
- **THEN** l'API répond 413 et aucun document n'est créé

### Requirement: Traitement par le worker
Le worker SHALL dépiler chaque job, simuler l'OCR par une attente de 1 à 3 s en extrayant le texte des fichiers texte (`text/*`, `.txt`, `.md`, `.csv`, `.json`, décodés en UTF-8), écrire explicitement le `tsvector` du document à partir de son titre et du texte extrait, passer le statut à `done`, observer `document_processing_delay_seconds` (maintenant moins date d'upload), puis pousser un message de notification. Les autres fichiers MUST être indexés sur leur titre seulement. Le worker MUST traiter jusqu'à `WORKER_CONCURRENCY` jobs en parallèle (4 par défaut).

#### Scenario: Document traité et indexé
- **WHEN** un fichier texte est uploadé et qu'aucune panne n'est active
- **THEN** en quelques secondes son statut passe à `done` et une recherche sur un mot de son contenu le renvoie

#### Scenario: Fichier non textuel
- **WHEN** un fichier `photo.png` est uploadé puis traité
- **THEN** une recherche sur `photo.png` le renvoie, et son contenu binaire n'est pas indexé

#### Scenario: Indexation non automatique
- **WHEN** un document est inséré en base mais pas encore traité par le worker
- **THEN** il n'apparaît dans aucun résultat de recherche (pas de colonne générée ni de trigger d'indexation)

### Requirement: Consultation et recherche
`GET /documents/{id}` SHALL renvoyer le statut et les métadonnées du document (`id`, `title`, `filename`, `content_type`, `size`, `status`, `uploaded_at`, `processed_at`), ou 404 s'il n'existe pas. `GET /documents/{id}/file` SHALL renvoyer le fichier avec son type et son nom d'origine (`Content-Disposition`), ou 404. `GET /search?q=` SHALL effectuer une recherche plein texte Postgres sur le `tsvector` et renvoyer la liste des documents trouvés.

#### Scenario: Document inexistant
- **WHEN** un client demande un `id` inconnu
- **THEN** l'API répond 404

#### Scenario: Téléchargement
- **WHEN** un client demande `GET /documents/{id}/file` pour un document déposé
- **THEN** il reçoit exactement les octets déposés, avec le type et le nom de fichier d'origine

#### Scenario: Échec de la base pendant une recherche
- **WHEN** la requête Postgres de recherche lève une exception ou expire
- **THEN** l'API répond 200 avec une liste vide et incrémente `search_fallback_total`
