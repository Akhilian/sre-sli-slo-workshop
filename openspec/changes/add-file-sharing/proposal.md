## Why

DocShare ne partage aujourd'hui aucun fichier : l'API reçoit un titre et un texte en JSON, et rien ne se télécharge. Pour un système appelé « DocShare », et maintenant qu'une interface web existe, c'est déroutant. Les participants doivent pouvoir déposer un vrai fichier, le retrouver par la recherche et le télécharger.

## What Changes

- **BREAKING** `POST /documents` reçoit un fichier en `multipart/form-data` (champ `file`, titre optionnel qui vaut par défaut le nom du fichier) au lieu d'un JSON `{title, content}`. La route, le code 202 et la réponse `{"id"}` ne changent pas.
- Le fichier est stocké avec le document (Postgres `BYTEA`, mémoire en mode `standalone`), dans la limite de 5 Mio : au-delà, 413 ; fichier vide, 422.
- L'OCR simulé du worker extrait le texte des fichiers texte (`text/*`, `.txt`, `.md`, `.csv`, `.json`) ; les autres fichiers sont indexés sur leur titre seulement. Le `tsvector` est calculé à partir du titre et du texte extrait.
- Nouvelle route `GET /documents/{id}/file` : téléchargement du fichier, avec son nom et son type d'origine.
- `GET /documents/{id}` renvoie aussi `filename`, `content_type` et `size`.
- Le script k6 envoie un petit fichier texte contenant le jeton, au lieu du JSON.
- Pannes, métriques, SLO et dashboards inchangés.

## Capabilities

### New Capabilities

Aucune.

### Modified Capabilities
- `document-pipeline` : upload de fichier, extraction du texte par le worker, téléchargement.

## Impact

- Code : `domain/` (modèle `StoredFile`, ports `DocumentRepository`, `Ocr`, `Indexer`), `adapters/postgres.py` (colonnes et migration idempotente), `adapters/memory.py`, `adapters/simulated.py`, `entrypoints/http.py`, tests.
- Dépendance : `python-multipart`, requise par FastAPI pour les formulaires.
- k6 : `charts/docshare/k6/traffic.js` (change actif `add-traffic-and-runbook`, dont les exigences restent vraies : le jeton est dans le fichier).
- Interface : la zone de dépôt par glisser-déposer et les liens de téléchargement relèvent du change `add-web-ui`, mis à jour en conséquence.
- Données : une base existante est migrée au démarrage de l'API (colonnes ajoutées, colonne `content` retirée). Les anciens documents restent consultables, sans fichier à télécharger.
- Documentation : section « Utiliser l'API » du README (`curl -F file=@...`).
- Nouvelle série `http_requests_total{route="/documents/{id}/file"}`, hors de tout SLO.
