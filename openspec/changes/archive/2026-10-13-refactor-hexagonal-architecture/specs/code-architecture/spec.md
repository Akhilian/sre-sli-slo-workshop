## ADDED Requirements

### Requirement: Domaine indépendant de l'infrastructure
Le code SHALL être découpé en `domain/`, `adapters/` et `entrypoints/`. Les modules de `domain/` MUST NOT importer FastAPI, psycopg, redis ni prometheus_client ; ils dépendent uniquement des ports qu'ils déclarent.

#### Scenario: Import du domaine sans dépendances
- **WHEN** un test importe `domain` dans un environnement où les modules d'infrastructure sont masqués
- **THEN** l'import réussit

#### Scenario: Câblage centralisé
- **WHEN** un rôle démarre
- **THEN** ses adaptateurs sont construits dans `bootstrap.py` et injectés dans les cas d'usage, sans qu'aucun cas d'usage n'instancie d'adaptateur

### Requirement: Pannes portées par des décorateurs de ports
Chaque panne SHALL être implémentée dans `adapters/faults.py` comme un décorateur d'un port, qui relit les pannes actives à chaque appel. Le code de `domain/` MUST NOT connaître les pannes. Chaque décorateur MUST produire exactement l'effet décrit par `fault-injection` : dégrader son SLI et laisser intacts les autres.

| Panne | Port décoré | SLI dégradé |
| --- | --- | --- |
| `upload_latency` | enregistrement d'un document | latence |
| `upload_error_rate` | enregistrement d'un document, avant l'INSERT | disponibilité |
| `worker_slow` | OCR | fraîcheur |
| `stale_index` | indexation | qualité |
| `notifier_drop` | réception des notifications | couverture |

#### Scenario: Erreur d'upload sans document fantôme
- **WHEN** `upload_error_rate=1` est active et qu'un upload est tenté avec un dépôt en mémoire
- **THEN** l'appel échoue, le dépôt ne contient aucun document et aucun job n'est en file

#### Scenario: Index périmé
- **WHEN** `stale_index=1` est active et que le worker traite un document
- **THEN** le document passe `done` et n'est pas indexé

#### Scenario: Perte de notification invisible
- **WHEN** `notifier_drop=1` est active
- **THEN** la notification disparaît avant d'atteindre le cas d'usage d'envoi, sans exception ni log, et `notifications_sent_total` n'augmente pas

#### Scenario: Effet limité à son SLI
- **WHEN** `worker_slow=10` est active
- **THEN** l'upload, l'indexation et la notification se comportent normalement ; seule la durée de l'OCR est multipliée

### Requirement: Contrat d'observation inchangé
Toutes les métriques SHALL être déclarées dans `adapters/metrics.py`. Les noms, labels, valeurs de labels et buckets MUST rester identiques à ceux de `service-metrics`, pour que les SLO Sloth, leurs solutions et les dashboards fonctionnent sans modification.

#### Scenario: Comparaison avant et après
- **WHEN** on compare la liste des séries de `/metrics` des trois rôles avant et après la réorganisation, sous le même trafic k6
- **THEN** les noms de métriques, les labels et les bornes `le` sont identiques

#### Scenario: Ordre indexation puis statut
- **WHEN** le worker termine un document sans panne active
- **THEN** le document est indexé avant de passer `done`, pour qu'une recherche lancée dès `done` le trouve

### Requirement: Tests unitaires sans infrastructure
Le projet SHALL fournir des tests pytest qui couvrent les cas d'usage et les cinq pannes avec des adaptateurs en mémoire, et l'application FastAPI avec son `TestClient`. Ils MUST tourner sans Redis, Postgres ni Kubernetes, et la CI MUST les exécuter avant de construire l'image.

#### Scenario: Lancement local
- **WHEN** un développeur lance `pytest` après `pip install -r app/requirements-dev.txt`
- **THEN** les tests passent sans service externe démarré

#### Scenario: CI bloquante
- **WHEN** un test échoue sur un push vers `main`
- **THEN** l'image n'est pas publiée
