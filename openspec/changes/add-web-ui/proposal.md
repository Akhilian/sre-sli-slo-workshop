## Why

DocShare ne se manipule aujourd'hui qu'avec `curl`. Une petite interface web rend le système concret pour les participants : ils déposent un document, le voient passer `done`, le cherchent, et vivent une panne comme un utilisateur avant de la retrouver dans les SLI. Elle donne aussi à l'animateur un pupitre de pannes plus lisible que des appels à `/admin/faults`.

## What Changes

- Nouvelle application Vue 3 dans `web/` (Vite, JavaScript, sans bibliothèque de composants, sans routeur ni store) :
  - dépôt de fichiers par glisser-déposer (ou sélecteur de fichiers), plusieurs à la fois ;
  - suivi des documents déposés depuis ce navigateur, avec leur statut et le temps jusqu'à `done` ;
  - recherche, et téléchargement des fichiers depuis la liste et les résultats ;
  - messages d'erreur explicites (500, délai dépassé, document resté `pending`) ;
  - pupitre des pannes pour l'animateur, affiché avec `?admin`.
- Nouvelle image `docshare-web` : build Vite, puis fichiers statiques servis par nginx (non root), qui relaie aussi `/api/` vers l'API. Pas de CORS, aucune modification de l'API dans ce change. Dépend de `add-file-sharing` pour l'upload de fichiers et le téléchargement.
- Le chart ajoute par équipe un Deployment et un Service `web`. L'Ingress, quand il est activé, pointe vers `web`.
- La CI publie l'image `docshare-web` (amd64 + arm64) à côté de `docshare`.
- L'interface fonctionne aussi face au mode `standalone` (`docker run` ou `npm run dev`).

## Capabilities

### New Capabilities
- `web-ui` : parcours utilisateur dans le navigateur (dépôt, suivi, recherche, erreurs) et pupitre des pannes ; l'interface ne corrige pas les angles morts voulus de l'exercice.
- `web-delivery` : image nginx, relais `/api/`, déploiement par le chart, accès par `port-forward` ou Ingress, exécution locale, publication par la CI.

### Modified Capabilities

Aucune spec archivée ne change. Le Deployment `web` et l'Ingress s'ajoutent à la pile d'équipe décrite par le change actif `add-k8s-deployment` ; `web-delivery` décrit ces ajouts.

## Impact

- Nouveaux fichiers : `web/` (application Vue, `Dockerfile`, configuration nginx), `charts/docshare/templates/web.yaml`.
- Modifiés : `charts/docshare/values.yaml` et `values/<cible>/docshare.yaml` (image et ressources de `web`), `charts/docshare/templates/ingress.yaml`, `scripts/setup.sh` (vérification de `OWNER` pour les deux images), `.github/workflows/image.yml`, README.
- API, métriques, SLO et dashboards : inchangés. Les appels de l'interface passent par l'API et sont mesurés comme n'importe quel trafic.
- Quota d'équipe : un pod de plus (≈ 10m CPU, 16 Mi demandés), dans la marge actuelle.
- Outillage : Node.js pour développer l'interface ; l'image se construit sans Node installé sur le poste.
