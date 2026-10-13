## Context

DocShare n'a qu'une API JSON. Le chart déploie par équipe `api`, `worker`, `notifier`, Redis, Postgres et un Job k6 ; les équipes accèdent à l'API par `kubectl port-forward svc/api 8000:80`. Le contrat d'observation (`service-metrics`) et les angles morts voulus (repli de recherche masqué, perte de notifications silencieuse, absence de métriques côté client) font partie de l'exercice. Le code doit rester court et lisible par des développeurs qui découvrent le SRE.

## Goals / Non-Goals

**Goals:**
- Une interface web légère et connue (Vue 3), dans son propre conteneur, déployée avec chaque équipe.
- Aucune modification de l'API, des métriques, des SLO ni des dashboards.
- Un pupitre de pannes pour l'animateur.
- Utilisable hors cluster face au mode `standalone`.

**Non-Goals:**
- État des notifications, bandeau « vue utilisateur », métriques côté client (RUM) : changes ultérieurs éventuels.
- Authentification : le pupitre est seulement masqué derrière `?admin`, comme `/admin/faults` est déjà ouvert sur l'API.
- Routeur, store (Pinia), bibliothèque de composants, TypeScript, rendu serveur.
- Tests de bout en bout dans un navigateur (Playwright, Cypress).

## Decisions

### Vue 3 + Vite, en JavaScript

Vue 3 avec composants monofichiers (`.vue`) et `<script setup>`, construit par Vite. Versions courantes à la rédaction : Vue 3.5, Vite 8, `@vitejs/plugin-vue` 6, Vitest 5 ; elles seront figées dans `package-lock.json`.

Alternatives écartées : Vue chargé depuis un CDN sans build (pas de composants monofichiers, dépendance réseau dans une salle de formation), htmx (moins connu des développeurs front), React (plus lourd pour quatre écrans), TypeScript (une étape de plus à lire pour un public qui n'en a pas besoin).

### Arborescence

```
web/
  package.json, package-lock.json, vite.config.js, index.html
  src/
    main.js
    App.vue                 # mise en page, ?admin
    api.js                  # fetch vers /api, délai de 10 s, erreurs normalisées
    tracking.js             # suivi des documents : localStorage, interrogation, délai de 60 s
    components/
      UploadForm.vue
      DocumentList.vue
      SearchBox.vue
      FaultConsole.vue
    style.css
  tests/                    # Vitest sur api.js et tracking.js
  nginx/default.conf.template
  Dockerfile
```

L'état partagé (la liste de suivi) vit dans `tracking.js` sous forme d'un `reactive()` exporté : pas besoin de Pinia pour une seule liste.

### Image : build Node, service nginx non root

`Dockerfile` en deux étapes : `node:22-alpine` lance `npm ci` et `npm run build`, puis `nginxinc/nginx-unprivileged` (alpine) reçoit `dist/` et le gabarit de configuration. L'image écoute sur 8080 en utilisateur non root, comme l'image `docshare` (uid 10001).

Le gabarit `default.conf.template` est traité au démarrage par l'`envsubst` intégré à l'image nginx officielle, qui remplace `${API_URL}` :

```
location /api/ { proxy_pass ${API_URL}/; }   # le "/" final retire le préfixe /api
location /     { try_files $uri /index.html; }
```

`API_URL` vaut `http://api` par défaut, le nom du Service de l'API dans le namespace de l'équipe. Hors cluster : `http://host.docker.internal:8000`.

Alternative écartée : appeler l'API directement depuis le navigateur. Il faudrait CORS dans l'API et une adresse publique de l'API, ce qui change l'API et le parcours `port-forward`.

### Appels à l'API

`api.js` encapsule `fetch` : préfixe `/api`, délai de 10 s par `AbortController`, et une erreur unique `ApiError(status, message)`. Pour une 422, le message reprend `detail` de FastAPI. Les composants n'appellent jamais `fetch` eux-mêmes.

### Suivi des documents

`tracking.js` conserve `{id, title, uploadedAt, status, doneAt}` dans le `localStorage` (50 documents au plus) et interroge chaque document `pending` toutes les secondes. Au-delà de 60 s, comme le `FOLLOW_TIMEOUT` de k6, le document passe à l'état local « bloqué » et n'est plus interrogé ; un bouton relance le suivi. Le temps affiché est mesuré dans le navigateur (`doneAt - uploadedAt`) : c'est le temps vécu par l'utilisateur, pas une métrique.

### Pupitre des pannes

`FaultConsole.vue` n'est monté que si `new URLSearchParams(location.search).has("admin")`. La liste des pannes et le SLI de chacune sont écrits dans le composant, à l'image du tableau du README. Le pupitre relit `GET /api/admin/faults` après chaque modification.

### Chart

`templates/web.yaml` : Deployment `web` (1 réplique, `API_URL=http://api`, sondes HTTP sur `/`) et Service `web` (port 80 vers 8080). Valeurs : `web.enabled` (`true` par défaut : l'interface fait partie de la pile nominale d'une équipe ; `false` sert au retour arrière ou à une session sans interface, sans toucher au reste), `web.image` (`ghcr.io/OWNER/docshare-web`, `latest`), ressources `10m/16Mi` demandées et `100m/64Mi` limites. Pas de `PodMonitor`. L'Ingress existant change de backend : `api` vers `web` quand `web.enabled`, et reste sur `api` sinon. Les appels `/api/...` passent alors par nginx, et `/admin/faults` reste accessible comme aujourd'hui.

En local, `values/local/docshare.yaml` utilise `docshare-web:dev` avec `pullPolicy: Never`, comme l'image de l'API. `scripts/setup.sh` refuse `OWNER` dans l'une ou l'autre image.

### CI

Dans `.github/workflows/image.yml`, un job `web-test` (`npm ci`, `npm test`, `npm run build`) puis un job `web-build` qui publie `ghcr.io/<owner>/docshare-web` en amd64 + arm64. Les jobs de l'API et de l'interface restent indépendants.

### Effet sur les SLI

Les appels de l'interface passent par l'API et sont mesurés comme le reste du trafic. C'est voulu : un participant qui dépose un document pendant `upload_error_rate` contribue au SLI de disponibilité. Les fichiers statiques sont servis par nginx et ne touchent pas l'API.

## Risks / Trade-offs

- [Des recherches de participants sans résultat font baisser le SLI de qualité] → volume négligeable face à k6 (environ 120 recherches par minute), mais une équipe qui enchaîne des recherches au hasard peut faire monter le burn rate sur 5 min. Documenté dans le README. C'est aussi un sujet de débrief : un SLI de qualité qui compte les fautes de frappe des utilisateurs mesure-t-il la bonne chose ?
- [L'interrogation toutes les secondes ajoute du trafic sur `/documents/{id}`] → cette route n'entre dans aucun SLO, et le suivi s'arrête à `done` ou après 60 s.
- [Un participant découvre `?admin` et active des pannes] → atelier entre collègues ; le même pouvoir existe déjà par `curl` sur `/admin/faults`. Documenté comme pupitre de l'animateur, pas comme une sécurité.
- [Une deuxième image à publier et à épingler] → même workflow, même `OWNER`, même vérification dans `setup.sh`.
- [Node.js requis pour développer l'interface] → seulement pour `npm run dev` ; l'image se construit dans Docker.

## Migration Plan

1. Écrire l'application et ses tests, la faire tourner avec `npm run dev` face au mode `standalone`.
2. Construire l'image, la tester avec `docker run` face au mode `standalone`.
3. Ajouter `web` au chart, installer sur le k3s local, vérifier le `port-forward` et le parcours sous les cinq pannes.
4. Retour arrière : `web.enabled: false` désactive l'interface sans toucher au reste de la pile.

## Open Questions

Aucune.
