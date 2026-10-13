# web-ui Specification

## Purpose
TBD - created by archiving change add-web-ui. Update Purpose after archive.
## Requirements
### Requirement: Dépôt de fichiers par glisser-déposer
L'interface SHALL proposer une zone de dépôt qui accepte un ou plusieurs fichiers par glisser-déposer, et un bouton « Choisir des fichiers » qui ouvre le sélecteur de fichiers du système. Chaque fichier MUST être envoyé par son propre `POST /api/documents` (multipart, titre égal au nom du fichier). La zone MUST indiquer pour chaque fichier l'envoi en cours, puis l'échec éventuel avec son message et un bouton pour réessayer ; un fichier déposé avec succès rejoint la liste de suivi.

#### Scenario: Dépôt nominal
- **WHEN** l'utilisateur glisse `facture.txt` sur la zone de dépôt
- **THEN** le document apparaît dans la liste de suivi avec son `id`, son nom et le statut `pending`

#### Scenario: Plusieurs fichiers
- **WHEN** l'utilisateur dépose 10 fichiers d'un coup
- **THEN** 10 envois partent, et chacun réussit ou échoue indépendamment des autres

#### Scenario: Upload lent
- **WHEN** `upload_latency=2` est active
- **THEN** la zone indique l'envoi en cours pendant environ 2 s, puis le document rejoint la liste de suivi

#### Scenario: Sans souris
- **WHEN** l'utilisateur atteint le bouton « Choisir des fichiers » au clavier et le valide
- **THEN** le sélecteur de fichiers s'ouvre et les fichiers choisis sont envoyés comme par glisser-déposer

### Requirement: Suivi des documents déposés
L'interface SHALL lister les documents déposés depuis ce navigateur, conservés dans le `localStorage`, et interroger `GET /api/documents/{id}` chaque seconde tant qu'un document est `pending`. Elle MUST afficher pour chaque document son statut, le temps écoulé entre le dépôt et `done`, et un lien de téléchargement (`/api/documents/{id}/file`). Au-delà de 60 s en `pending`, le suivi MUST s'arrêter et le document MUST être signalé comme bloqué, avec un bouton pour relancer le suivi.

#### Scenario: Passage à done
- **WHEN** un document déposé est traité par le worker
- **THEN** son statut passe à `done` en quelques secondes et le temps de traitement s'affiche

#### Scenario: Worker lent
- **WHEN** `worker_slow=10` est active et qu'un document reste `pending` plus de 60 s
- **THEN** le document est signalé comme bloqué et l'interface cesse de l'interroger

#### Scenario: Rechargement de la page
- **WHEN** l'utilisateur recharge la page
- **THEN** la liste de suivi est conservée et le suivi des documents `pending` reprend

### Requirement: Recherche
L'interface SHALL proposer un champ de recherche qui envoie `GET /api/search?q=...` et affiche les titres et `id` trouvés, chacun avec un lien de téléchargement, ou « Aucun résultat » quand la liste est vide.

#### Scenario: Recherche d'un document déposé
- **WHEN** l'utilisateur cherche un mot du contenu d'un fichier texte `done`
- **THEN** le document figure dans les résultats, et son lien télécharge le fichier d'origine

### Requirement: Erreurs visibles
Une réponse 5xx, une erreur réseau ou un délai dépassé (10 s) SHALL produire un message d'erreur lisible à l'endroit de l'action concernée, sans bloquer le reste de l'interface. Une réponse 422 MUST afficher le détail renvoyé par l'API.

#### Scenario: Erreurs d'upload
- **WHEN** `upload_error_rate=1` est active et que l'utilisateur dépose un fichier
- **THEN** la zone de dépôt indique l'échec de ce fichier avec un bouton pour réessayer, et aucun document n'est ajouté à la liste de suivi

#### Scenario: Fichier trop gros
- **WHEN** l'utilisateur dépose un fichier de plus de 5 Mio
- **THEN** la zone de dépôt affiche le message de l'API (413) pour ce fichier

#### Scenario: API indisponible
- **WHEN** l'API ne répond pas
- **THEN** l'action en cours affiche une erreur, et la recherche et la liste de suivi restent utilisables

### Requirement: Angles morts préservés
L'interface MUST NOT révéler ce que l'API masque, pour ne pas gâcher l'exercice : une recherche en repli (`200` vide) MUST s'afficher comme « Aucun résultat », un document non indexé MUST apparaître `done` comme les autres, et l'interface MUST NOT afficher d'état de notification. Elle MUST NOT exposer de métriques ni envoyer de télémétrie.

#### Scenario: Index périmé vu par l'utilisateur
- **WHEN** `stale_index=1` est active et que l'utilisateur cherche le contenu d'un document qu'il voit `done`
- **THEN** l'interface affiche « Aucun résultat », sans autre indication

### Requirement: Pupitre des pannes
Avec le paramètre `?admin` dans l'URL, l'interface SHALL afficher un pupitre qui liste les cinq pannes, leur valeur active (`GET /api/admin/faults`), et permet de saisir une valeur, de l'appliquer et de couper une panne (`POST /api/admin/faults`). Sans `?admin`, le pupitre MUST NOT être affiché. Le pupitre MUST rappeler, pour chaque panne, le SLI qu'elle dégrade.

#### Scenario: Activation depuis le pupitre
- **WHEN** l'animateur ouvre `/?admin`, saisit `0.5` pour `upload_error_rate` et applique
- **THEN** la panne apparaît active, et environ la moitié des fichiers déposés ensuite échouent

#### Scenario: Interface des participants
- **WHEN** un participant ouvre `/`
- **THEN** le pupitre n'est pas affiché

