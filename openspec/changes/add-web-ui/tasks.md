## 1. Application Vue

- [x] 1.1 Initialiser `web/` : Vue 3, Vite, `@vitejs/plugin-vue`, Vitest, versions figées ; relais `/api` de Vite vers `http://localhost:8000`
- [x] 1.2 `src/api.js` : préfixe `/api`, délai de 10 s, `ApiError`, détail des 422
- [x] 1.3 `src/tracking.js` : liste réactive, `localStorage` (50 documents), interrogation chaque seconde, état « bloqué » après 60 s, relance
- [x] 1.4 `DropZone.vue` : glisser-déposer de plusieurs fichiers, bouton « Choisir des fichiers », état par fichier, échec avec réessai (remplace le formulaire titre et contenu)
- [x] 1.5 `DocumentList.vue` : statut, temps jusqu'à `done`, état « bloqué » et relance, lien de téléchargement
- [x] 1.6 `SearchBox.vue` : résultats avec lien de téléchargement, « Aucun résultat », erreurs
- [x] 1.7 `FaultConsole.vue` : cinq pannes avec leur SLI, valeurs actives, appliquer et couper, affiché seulement avec `?admin`
- [x] 1.8 `App.vue` et `style.css` : mise en page simple, utilisable sur un écran de portable

## 2. Tests

- [x] 2.1 Vitest sur `api.js` : préfixe, upload multipart, délai, 5xx, 413, 422, erreur réseau
- [x] 2.2 Vitest sur `tracking.js` : passage à `done`, arrêt après 60 s, persistance et reprise

## 3. Image

- [x] 3.1 `web/nginx/default.conf.template` : relais `/api/` sans préfixe vers `${API_URL}`, `client_max_body_size 6m`, repli `index.html`
- [x] 3.2 `web/Dockerfile` en deux étapes (Node, puis nginx non root sur 8080), `.dockerignore`
- [ ] 3.3 Construire l'image et la lancer face au mode `standalone` : parcours complet et une panne depuis `?admin`

## 4. Déploiement

- [x] 4.1 `deploy/helm/docshare/templates/web.yaml` et valeurs `web` (`enabled`, image, ressources, `API_URL`)
- [x] 4.2 Ingress vers `web` ; `deploy/environments/<cible>/docshare.yaml` (image locale `docshare-web:dev`, `ghcr.io/OWNER/docshare-web`)
- [x] 4.3 `deploy/scripts/setup.sh` : vérification de `OWNER` pour les deux images
- [x] 4.4 CI : jobs `web-test` et `web-build` (amd64 + arm64, SHA et `latest`)

## 5. Documentation et vérification

- [x] 5.1 README : lancer l'interface (`npm run dev`, `docker run`, `port-forward svc/web`), pupitre `?admin`, effet des recherches des participants sur le SLI de qualité
- [ ] 5.2 Sur le k3s local : installer deux équipes, ouvrir l'interface de chacune par `port-forward`, vérifier l'isolation
- [ ] 5.3 Sous chacune des cinq pannes, vérifier ce que voit l'utilisateur, et que les angles morts restent masqués (`stale_index`, repli de recherche, `notifier_drop`)
