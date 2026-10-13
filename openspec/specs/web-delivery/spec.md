# web-delivery Specification

## Purpose
TBD - created by archiving change add-web-ui. Update Purpose after archive.
## Requirements
### Requirement: Image web séparée
L'interface SHALL être livrée dans une image `docshare-web` distincte de l'image `docshare`, construite en plusieurs étapes : build Vite, puis fichiers statiques servis par nginx en utilisateur non root. L'image MUST se construire avec `docker build web/` sans Node.js installé sur le poste.

#### Scenario: Construction locale
- **WHEN** on lance `docker build -t docshare-web:dev web/`
- **THEN** l'image est construite et ne contient ni Node.js ni `node_modules`

### Requirement: Relais vers l'API
nginx SHALL relayer `/api/` vers l'API en retirant le préfixe `/api`, en acceptant des corps de requête jusqu'à 6 Mio (pour que l'API, et non nginx, réponde 413 au-delà de 5 Mio), l'adresse de l'API étant donnée par la variable `API_URL` (`http://api` par défaut). L'interface MUST appeler l'API uniquement par ce chemin relatif, sans CORS ni adresse codée en dur. Ce change MUST NOT modifier l'API ; le dépôt et le téléchargement de fichiers viennent du change `add-file-sharing`.

#### Scenario: Appel relayé
- **WHEN** le navigateur appelle `/api/documents/1` sur le conteneur web
- **THEN** l'API reçoit `GET /documents/1` et la métrique `http_requests_total{route="/documents/{id}"}` augmente comme pour un appel direct

#### Scenario: Fichiers statiques
- **WHEN** le navigateur charge `/` ou un fichier de l'application
- **THEN** nginx répond sans appeler l'API, et `http_requests_total` n'augmente pas

### Requirement: Interface déployée avec la pile d'équipe
Le chart SHALL déployer dans chaque namespace d'équipe un Deployment `web` d'une réplique et un Service `web` sur le port 80, avec sonde de disponibilité, ressources et image configurables. `web` MUST NOT être collecté par Prometheus. L'Ingress, quand il est activé, MUST router vers `web`.

#### Scenario: Accès d'une équipe sans Ingress
- **WHEN** une équipe lance `kubectl port-forward svc/web 8080:80` avec son kubeconfig
- **THEN** l'interface s'ouvre sur `http://localhost:8080` et dialogue avec l'API de son namespace

#### Scenario: Isolation
- **WHEN** l'équipe `team-a` dépose un document depuis son interface
- **THEN** le document est créé dans la base de `team-a` uniquement

### Requirement: Exécution locale
L'interface SHALL pouvoir tourner hors cluster, face à une API locale (mode `standalone` ou pile Docker) : par `docker run` avec `API_URL`, et par `npm run dev` avec un relais Vite vers `http://localhost:8000`.

#### Scenario: Face au mode standalone
- **WHEN** l'API tourne en `ROLE=standalone` sur le port 8000 et qu'on lance l'image web avec `API_URL=http://host.docker.internal:8000`
- **THEN** le parcours dépôt, suivi et recherche fonctionne dans le navigateur

### Requirement: Publication par la CI
La CI SHALL vérifier le build de l'interface et publier `ghcr.io/<owner>/docshare-web`, taguée par SHA et `latest`, pour `linux/amd64` et `linux/arm64`, à chaque push sur `main` qui modifie `web/`.

#### Scenario: Build cassé
- **WHEN** `npm run build` ou les tests de `web/` échouent
- **THEN** l'image `docshare-web` n'est pas publiée

