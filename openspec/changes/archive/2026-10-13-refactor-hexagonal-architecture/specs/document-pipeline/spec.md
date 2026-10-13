## MODIFIED Requirements

### Requirement: Rôle choisi par variable d'environnement
L'application SHALL être une seule base de code et une seule image, dont le comportement est choisi par la variable `ROLE` (`api`, `worker`, `notifier` ou `standalone`). Les trois premiers rôles forment le mode distribué, sur Redis et Postgres ; `standalone` exécute les trois dans un seul processus, sur des adaptateurs en mémoire.

#### Scenario: Démarrage d'un rôle
- **WHEN** le conteneur démarre avec `ROLE=worker`
- **THEN** le processus dépile la file de jobs et n'expose pas l'API HTTP métier

#### Scenario: Démarrage en mode standalone
- **WHEN** le conteneur démarre avec `ROLE=standalone`
- **THEN** le processus expose l'API HTTP et traite lui-même les jobs et les notifications, sans se connecter à Redis ni à Postgres

#### Scenario: Rôle inconnu
- **WHEN** le conteneur démarre avec un `ROLE` absent ou inconnu
- **THEN** le processus s'arrête avec un code de sortie non nul et un message explicite
