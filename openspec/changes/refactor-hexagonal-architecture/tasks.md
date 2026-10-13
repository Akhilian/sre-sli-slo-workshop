## 1. Domaine

- [x] 1.1 Créer `domain/models.py` (Document, ProcessingJob, Notification) et `domain/errors.py`
- [x] 1.2 Déclarer les ports dans `domain/ports.py`
- [x] 1.3 Écrire les cas d'usage dans `domain/services.py` (upload, consultation, recherche, traitement avec indexation avant `mark_done`, envoi)

## 2. Adaptateurs

- [x] 2.1 `adapters/postgres.py` : dépôt, indexation, recherche (`SearchUnavailable`), schéma et attente de disponibilité
- [x] 2.2 `adapters/redis.py` : files JSON aux clés inchangées, `FaultStore`, attente de disponibilité
- [x] 2.3 `adapters/simulated.py` : OCR (1 à 3 s) et envoi d'e-mails (50 ms)
- [x] 2.4 `adapters/metrics.py` : toutes les métriques, noms, labels et buckets inchangés
- [x] 2.5 `adapters/faults.py` : les quatre décorateurs et `InjectedFault`
- [x] 2.6 `adapters/memory.py` : dépôt avec indexation et recherche par mots, files (`queue.Queue`) et `FaultStore` en mémoire, sûrs entre threads

## 3. Points d'entrée et câblage

- [x] 3.1 `entrypoints/http.py` : `create_app()`, routes avec `Depends`, `MetricsMiddleware`, gestionnaire `InjectedFault` -> 500, repli de recherche
- [x] 3.2 `entrypoints/worker.py` et `entrypoints/notifier.py` : boucles, gestion des erreurs Redis, métriques
- [x] 3.3 `bootstrap.py` : construction par rôle, décorateurs de pannes, `queue_depth` par `set_function`
- [x] 3.4 `entrypoints/standalone.py` et rôle `standalone` dans `bootstrap.py` et `main.py` : threads worker et notifier, uvicorn au premier plan, un seul `/metrics`
- [x] 3.5 Basculer `main.py` sur `bootstrap.py` et supprimer `api.py`, `worker.py`, `notifier.py`, `db.py`, `jobqueue.py` et `faults.py`

## 4. Tests

- [x] 4.1 `app/requirements-dev.txt`, `pytest.ini`, exclusion de `tests/` dans `.dockerignore`
- [x] 4.2 Tests des cas d'usage sur adaptateurs en mémoire
- [x] 4.3 Tests des cinq pannes : effet sur leur SLI, aucun effet sur les autres
- [x] 4.4 Tests de l'API avec `TestClient` : codes de réponse, label `route`, routes non instrumentées, 422 sur panne inconnue
- [x] 4.5 Test d'indépendance du domaine et test de la liste des métriques exposées
- [x] 4.6 Test du mode standalone : upload, passage `done`, recherche du jeton, métriques des trois parcours sur `/metrics`
- [x] 4.7 Job de tests dans `.github/workflows/image.yml`, requis avant la construction

## 5. Documentation et vérification

- [x] 5.1 README : lancement en une commande (`docker run -e ROLE=standalone` et `python app/main.py`), pannes en mode standalone ; mettre à jour la section « Développement » du README et renvoyer vers `adapters/faults.py` et `adapters/metrics.py`
- [x] 5.2 Lancer l'image en mode standalone avec Docker, rejouer le parcours et une panne à la main
- [x] 5.3 Sur le k3s local : relever `/metrics` des trois rôles avant la bascule, redéployer `docshare:dev`, comparer les séries (écart trouvé et corrigé : chaque rôle exposait les métriques des autres ; `metrics.expose_only`)
- [x] 5.4 Rejouer le scénario court des cinq pannes et comparer les burn rates au tableau du README (à 2 min 30 : fraîcheur 1,4 et qualité 47 identiques au tableau ; disponibilité 38 à 105 s, latence en montée ; couverture 10,8 contre 21,7, encore en montée)
