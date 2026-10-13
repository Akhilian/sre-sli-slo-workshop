---
version: 1
slug: "web-src-app-vue"
primary_target: "web/src/App.vue"
related_targets: ["web/src/style.css","web/src/components"]
---

# Surface : écran principal DocShare (dépôt, mes fichiers, recherche)

Mode : Operate. Public : participants de l'atelier sur portable, et la salle via le vidéoprojecteur. Tâche : déposer des fichiers, suivre leur trajet, les retrouver et les télécharger. Contraintes : angles morts de PRODUCT.md intacts ; pupitre `?admin` hors périmètre de la refonte, déplacé sous la vue pour ne plus la masquer. Moment mémorable : le trajet de chaque fichier, qui cale visiblement pendant une panne.

## Direction contract

THESIS: Un gestionnaire de fichiers crédible, au niveau de Drive ou de La Suite Fichiers, dont chaque ligne raconte le trajet du fichier comme un suivi de colis. Refuse la page de panneaux blancs empilés, pastilles et bleu unique.

OWN-WORLD: Barre du haut bleu nuit (#14213d) portant le nom et la recherche ; fond gris froid clair, tableau blanc à lignes généreuses ; action principale safran (#f5b700) à texte bleu nuit ; états : bleu (en cours), vert (disponible), rouge (bloqué, échec). Atkinson Hyperlegible Next auto-hébergée, icônes Lucide à trait unique. Thème clair seul : salle éclairée et projecteur.

STORY: Le participant dépose, voit chaque fichier avancer Envoyé → En traitement → Disponible, le cherche, le télécharge ; pendant une panne, le trajet cale et la synthèse le dit.

FIRST VIEWPORT: Barre du haut : nom à gauche, champ de recherche large au centre. Sous elle : titre « Mes fichiers », synthèse des états, bouton safran « Déposer des fichiers » à droite. Puis le tableau Nom | Trajet | Taille | Déposé. Panneau d'envois ancré en bas à droite. Glisser un fichier n'importe où affiche un voile de dépôt plein écran.

FORM: Canon du gestionnaire de fichiers, choisi par l'utilisateur (références Drive, WeTransfer, La Suite Fichiers) ; pas de tirage concept-seed (direction épinglée) ; signature : le suivi en trois étapes par ligne.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
