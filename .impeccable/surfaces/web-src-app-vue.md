---
version: 1
slug: "web-src-app-vue"
primary_target: "web/src/App.vue"
related_targets: ["web/src/style.css","web/src/components"]
---

# Surface : écran principal DocShare (dépôt, mes fichiers, recherche)

Mode : Operate. Public : participants de l'atelier sur portable, et la salle via le vidéoprojecteur. Tâche : déposer des fichiers, suivre leur trajet, les retrouver et les télécharger. Contraintes : angles morts de PRODUCT.md intacts ; structure validée conservée (barre, Mes fichiers, tableau, trajet, panneau d'envois) ; pupitre `?admin` restylé avec les jetons partagés, sous la liste. Retour utilisateur à l'origine de la refonte : « même padding, même police, même radius, super commun ; aucune identité ». Choix utilisateur sur le statut : ressenti seulement (« Disponible », sans durée finale).

## Direction contract

THESIS: La typographie porte l'état : le nom d'un fichier prend du poids à mesure qu'il avance. Refuse les cartes arrondies, le rembourrage SaaS confortable et la sans-serif générique.

OWN-WORLD: Papier #fbfbfa, encre #0e0e0e, un seul accent outremer #3a2bff (action principale, étape en cours), vermillon #e5361c (texte #c42a12) pour bloqué et échec, gris #6b6b6b. Rayon 0 partout ; filets d'encre de 1 px comme seule structure ; aplats sans ombre, sauf le panneau flottant. Bricolage Grotesque variable (opsz, wdth, wght) pour tout ; Martian Mono uniquement pour les données (taille, date, état, légende).

STORY: Le participant dépose, voit le nom s'affiner en outremer puis s'alourdir en noir quand le fichier est disponible ; une panne barre le nom en vermillon ; il cherche et télécharge.

FIRST VIEWPORT: Barre fine sans fond, mot-symbole étroit et gras à gauche, recherche carrée au centre. « Mes fichiers » en display ~132 px, synthèse mono dessous, bouton outremer carré aligné sur la ligne de base. Tableau en filets : Nom (graisse = état) | trois cases carrées + état mono | Taille | Déposé | Télécharger. Panneau d'envois carré, en-tête encre inversé, en bas à droite.

FORM: Spécimen de fonte variable (challenger catalog variable-font-specimen, relance 1 registre « plus audacieux », choisi par l'utilisateur) ; seed key 5d8261d8 ; dons : grille de filets dense (site japonais), aplats sans grain (plan de zoo), bascules nettes sans demi-état (fil vertical). Signature : poids, largeur et couleur du nom selon l'état.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
