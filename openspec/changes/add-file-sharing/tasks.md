## 1. Domaine

- [x] 1.1 `StoredFile`, champs de fichier de `Document`, ports `add(title, file)`, `get_file`, `Ocr.extract(file) -> str`, `Indexer.index(id, text)`
- [x] 1.2 Cas d'usage : upload, traitement (fichier, extraction, indexation), téléchargement

## 2. Adaptateurs

- [x] 2.1 `postgres.py` : colonnes, migration idempotente, `get_file`, indexation du titre et du texte
- [x] 2.2 `memory.py` : stockage des octets, indexation du titre et du texte
- [x] 2.3 `simulated.py` : extraction UTF-8 des fichiers texte
- [x] 2.4 `faults.py` : décorateurs alignés sur les nouvelles signatures

## 3. API et k6

- [x] 3.1 `http.py` : upload multipart, 413 et 422, `GET /documents/{id}/file` ; `python-multipart` dans `requirements.txt`
- [x] 3.2 `charts/docshare/k6/traffic.js` : upload d'un fichier texte contenant le jeton

## 4. Tests et documentation

- [x] 4.1 Mettre à jour les tests existants ; tests d'extraction, de téléchargement, de taille, de fichier non textuel
- [x] 4.2 README : section « Utiliser l'API » et exemples `curl -F`
- [x] 4.3 Vérifier en mode `standalone` : upload, recherche, téléchargement, une panne
- [ ] 4.4 Sur le k3s local : migration d'une base existante et trafic k6 nominal
