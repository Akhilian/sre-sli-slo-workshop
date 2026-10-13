## Context

L'API reçoit aujourd'hui `{title, content}` en JSON ; le worker indexe `title || content` ; rien ne se télécharge. L'architecture hexagonale (`domain/`, `adapters/`, `entrypoints/`) et le mode `standalone` sont en place. Le contrat d'observation (noms de métriques, label `route="/documents"` du SLO de disponibilité, effets des pannes) ne doit pas bouger.

## Goals / Non-Goals

**Goals:**
- Déposer, rechercher et télécharger de vrais fichiers, par l'API et par l'interface.
- Garder la même route d'upload, les mêmes codes et le même parcours pour que SLO, pannes et dashboards restent valables.

**Non-Goals:**
- Extraction de texte des PDF, documents Office ou images : l'OCR reste simulé, seuls les fichiers texte sont lus.
- Stockage objet (S3, GCS) : un service de plus par équipe pour un atelier de 2 h.
- Liste de tous les documents de l'équipe, liens de partage signés, droits d'accès.

## Decisions

### Upload en multipart sur la même route

`POST /documents` prend `file` (`UploadFile`) et `title` (`Form`, optionnel). Garder la route garde le label `route="/documents"` sur lequel repose le SLO de disponibilité, et les décorateurs de pannes posés sur `DocumentRepository.add`. Une nouvelle route (`/files`) aurait obligé à réécrire le SLO fourni, ses solutions et le runbook.

Le JSON n'est plus accepté : garder les deux formats sur une route compliquerait l'API pour aucun client restant (k6 passe au multipart).

FastAPI exige `python-multipart` pour lire les formulaires. Le fichier est lu en entier par le point d'entrée HTTP, dans la limite de `MAX_UPLOAD_BYTES` (5 Mio par défaut, variable d'environnement) + 1 octet : au-delà, 413 ; vide, 422. 413 est un 4xx : comme les 422, il est exclu du SLI de disponibilité.

### Modèle et ports

- `StoredFile(filename, content_type, data)` dans `domain/models.py`.
- `Document` gagne `filename`, `content_type`, `size` ; `GET /documents/{id}` les renvoie (ajout compatible).
- `DocumentRepository.add(title, file)` et `DocumentRepository.get_file(id) -> StoredFile | None`.
- `Ocr.extract(file) -> str` : l'OCR renvoie le texte extrait.
- `Indexer.index(id, text)` : indexe le titre et le texte reçu.
- `ProcessDocument` : `get_file`, `ocr.extract`, `indexer.index`, `mark_done`, notification. Les décorateurs `SlowOcr` et `StaleIndexer` gardent leur effet.
- Nouveau cas d'usage `DownloadDocument`.

### Extraction du texte

`SimulatedOcr` attend 1 à 3 s, puis décode en UTF-8 (caractères invalides remplacés) les fichiers dont le type commence par `text/` ou dont l'extension est `.txt`, `.md`, `.csv` ou `.json`. Pour les autres, il renvoie une chaîne vide : seul le titre, donc par défaut le nom du fichier, est indexé.

### Stockage

Postgres : colonnes `filename`, `content_type`, `size`, `data BYTEA`, et suppression de `content`. `create_schema()` reste idempotent : `CREATE TABLE IF NOT EXISTS` avec les nouvelles colonnes, puis `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` et `DROP COLUMN IF EXISTS content` pour une base créée par une version précédente. Les anciens documents ont `data` à `NULL` : leur téléchargement répond 404.

`get` ne lit jamais `data` : seul `get_file` charge les octets.

Volume : k6 dépose environ 100 octets par seconde et par équipe, soit environ 1 Mo en 3 h, loin des 2 Gi du PVC. Un participant qui dépose des fichiers de 5 Mio reste lui aussi loin de la limite.

Mémoire (`standalone`) : les octets sont gardés dans le dictionnaire des documents, perdus à l'arrêt comme le reste.

### Téléchargement

`GET /documents/{id}/file` renvoie les octets avec `Content-Type` d'origine et `Content-Disposition: attachment; filename*=UTF-8''...` (nom encodé, pour les accents). La route apparaît dans `http_requests_total` avec son modèle `/documents/{id}/file`, sans risque de cardinalité, et n'entre dans aucun SLO.

### k6

Chaque itération envoie `http.file("<texte du corpus> <jeton>", "<jeton>.txt", "text/plain")` avec le titre du corpus. Le jeton est dans le contenu, donc indexé par l'extraction : le parcours et la détection de `stale_index` sont inchangés.

## Risks / Trade-offs

- [Un client JSON existant casse] → seuls k6, l'interface et le README appellent l'API ; tous sont mis à jour dans ce change ou dans `add-web-ui`.
- [Lire le fichier dans le point d'entrée HTTP compte dans la latence d'upload] → c'est la réalité d'un upload ; les fichiers de k6 font 100 octets, la latence nominale ne bouge pas.
- [Migration d'une base existante] → instructions idempotentes au démarrage de l'API ; sur les clusters d'atelier, la base est de toute façon recréée à chaque session.
- [Fichiers malveillants téléchargés par d'autres participants] → `Content-Disposition: attachment` force le téléchargement plutôt que l'affichage dans le navigateur ; atelier entre collègues, pas de scan antivirus.

## Migration Plan

1. API et tests, puis k6.
2. Sur le k3s local : reconstruire l'image, mettre à jour une équipe existante, vérifier la migration et le parcours k6.
3. Retour arrière : revert ; la colonne `content` supprimée n'est pas restaurée, il faut alors recréer la base de l'équipe.

## Open Questions

Aucune.
