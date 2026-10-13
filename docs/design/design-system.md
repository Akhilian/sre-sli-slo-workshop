---
name: DocShare
description: Gestionnaire de fichiers en spécimen de fonte variable, où la graisse du nom dit où en est le fichier.
colors:
  paper: "#fbfbfa"
  paper-sunk: "#f2f2ef"
  ink: "#0e0e0e"
  grey: "#5f5f5f"
  ultra: "#3a2bff"
  ultra-deep: "#2a1ed6"
  verm: "#e5361c"
  verm-text: "#c42a12"
  white: "#ffffff"
typography:
  display:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "clamp(4rem, 9vw, 8.25rem)"
    fontWeight: 800
    lineHeight: 0.8
    letterSpacing: "-0.04em"
    fontVariation: "'opsz' 96"
  display-results:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "clamp(3rem, 6vw, 5.5rem)"
    fontWeight: 800
    lineHeight: 0.8
    letterSpacing: "-0.04em"
    fontVariation: "'opsz' 96"
  display-drop:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "clamp(4rem, 11vw, 10rem)"
    fontWeight: 800
    lineHeight: 0.85
    letterSpacing: "-0.04em"
    fontVariation: "'opsz' 96"
  headline:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "clamp(2.75rem, 6vw, 5.25rem)"
    fontWeight: 300
    lineHeight: 0.9
    letterSpacing: "-0.04em"
    fontVariation: "'wdth' 85"
  title:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 750
    letterSpacing: "-0.03em"
  brand:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 800
    letterSpacing: "-0.02em"
    fontVariation: "'wdth' 75"
  name-pending:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.3125rem"
    fontWeight: 300
    letterSpacing: "-0.015em"
    fontVariation: "'wdth' 85"
  name-done:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.3125rem"
    fontWeight: 750
    letterSpacing: "-0.015em"
    fontVariation: "'wdth' 100"
  name-stuck:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.3125rem"
    fontWeight: 500
    letterSpacing: "-0.015em"
    fontVariation: "'wdth' 92"
  body:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.45
  control:
    fontFamily: "'Bricolage Grotesque Variable', 'Bricolage Grotesque', system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 650
    letterSpacing: "-0.01em"
  data:
    fontFamily: "'Martian Mono Variable', 'Martian Mono', ui-monospace, monospace"
    fontSize: "0.875rem"
    fontWeight: 350
    letterSpacing: "-0.02em"
    fontFeature: "'tnum' 1"
    fontVariation: "'wdth' 87.5"
  data-label:
    fontFamily: "'Martian Mono Variable', 'Martian Mono', ui-monospace, monospace"
    fontSize: "0.8125rem"
    fontWeight: 350
    letterSpacing: "-0.02em"
    fontFeature: "'tnum' 1"
    fontVariation: "'wdth' 87.5"
rounded:
  none: "0px"
spacing:
  cell-gap: "4px"
  cell: "14px"
  gutter: "2.5rem"
  gutter-compact: "1rem"
  row: "3.75rem"
  topbar: "3.5rem"
  control: "2.75rem"
  control-compact: "2.25rem"
  control-row: "2rem"
  section: "3rem"
components:
  topbar:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    height: "{spacing.topbar}"
    padding: "0 2.5rem"
  search-input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    height: "{spacing.control-compact}"
    padding: "0 2.5rem 0 2.4rem"
  button-primary:
    backgroundColor: "{colors.ultra}"
    textColor: "{colors.white}"
    typography: "{typography.control}"
    rounded: "{rounded.none}"
    height: "{spacing.control}"
    padding: "0 1.25rem"
  button-primary-hover:
    backgroundColor: "{colors.ultra-deep}"
    textColor: "{colors.white}"
  button-secondary:
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.none}"
    height: "{spacing.control}"
    padding: "0 1.25rem"
  button-secondary-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  button-download:
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    height: "{spacing.control-row}"
    padding: "0 0.75rem"
  button-download-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  icon-button:
    size: "2rem"
    rounded: "{rounded.none}"
  icon-button-hover:
    backgroundColor: "{colors.paper-sunk}"
  file-table-head:
    textColor: "{colors.grey}"
    typography: "{typography.data-label}"
    height: "2.25rem"
    padding: "0 1rem"
  file-table-row:
    height: "{spacing.row}"
    padding: "0 1rem"
  file-table-row-hover:
    backgroundColor: "{colors.paper-sunk}"
  file-name-pending:
    textColor: "{colors.ultra}"
    typography: "{typography.name-pending}"
  file-name-done:
    textColor: "{colors.ink}"
    typography: "{typography.name-done}"
  file-name-stuck:
    textColor: "{colors.verm-text}"
    typography: "{typography.name-stuck}"
  track-cell-todo:
    size: "{spacing.cell}"
    rounded: "{rounded.none}"
  track-cell-passed:
    backgroundColor: "{colors.ink}"
    size: "{spacing.cell}"
    rounded: "{rounded.none}"
  track-cell-current:
    backgroundColor: "{colors.ultra}"
    size: "{spacing.cell}"
    rounded: "{rounded.none}"
  track-cell-stuck:
    backgroundColor: "{colors.verm}"
    size: "{spacing.cell}"
    rounded: "{rounded.none}"
  tray:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.none}"
    width: "24rem"
  tray-head:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
    height: "2.5rem"
    padding: "0 0.3rem 0 0.9rem"
  drop-overlay:
    backgroundColor: "{colors.ultra}"
    textColor: "{colors.white}"
    typography: "{typography.display-drop}"
    padding: "{spacing.gutter}"
  notice-error:
    textColor: "{colors.verm-text}"
    rounded: "{rounded.none}"
    padding: "0.9rem 1rem"
  badge-off:
    textColor: "{colors.grey}"
    typography: "{typography.data-label}"
    rounded: "{rounded.none}"
    padding: "0.1rem 0.5rem"
---

# Design System: DocShare

## Overview

**Creative North Star: "Le spécimen"**

DocShare se lit comme une planche de spécimen de fonte variable posée sur un gestionnaire de fichiers. La structure reste celle du canon (barre fine, titre de vue, tableau, panneau d'envois en bas à droite), mais l'identité ne vient ni d'une couleur de marque ni d'une carte : elle vient de la typographie. Le nom d'un fichier change de graisse, de largeur et de couleur selon son état : fin, étroit et outremer quand il est en route, plein et noir quand il est disponible, barré de vermillon quand il cale. Un titre de vue à l'échelle d'une affiche (jusqu'à 132 px) installe ce registre dès le premier écran.

Le monde est fait de papier blanc cassé, d'encre presque noire et de filets d'encre de 1 px, sans rayon et sans ombre. Deux voix typographiques se partagent strictement le travail : Bricolage Grotesque pour tout ce qui se lit et se manipule, Martian Mono pour les seules données (tailles, dates, états, légendes). Les changements d'état sont des bascules nettes, sans demi-teinte : les cases du trajet clignotent en deux temps, les squelettes aussi. Le système est clair seul, dense, pensé pour la salle éclairée et le vidéoprojecteur.

**Key Characteristics:**
- La graisse, la largeur et la couleur du nom portent l'état du fichier.
- Rayon 0 partout ; des filets d'encre de 1 px comme seule structure.
- Un seul accent, l'outremer, pour l'action principale et ce qui est en mouvement ; le vermillon pour ce qui cale.
- Titre de vue en display 800 très serré, interlignage 0.8.
- Martian Mono étroite et tabulaire pour les données, jamais pour la prose ni les commandes.
- Aplats sans ombre, sauf le panneau des envois qui flotte.
- Bascules nettes (`steps(2)`) plutôt que fondus.

## Colors

Un noir et blanc d'imprimeur, traversé par un outremer électrique et, pour la seule panne, un vermillon.

### Primary
- **Outremer** (`ultra`) : l'action principale de la vue (« Déposer des fichiers »), tout ce qui est en route (nom en traitement, case courante du trajet, texte d'état, compte « en traitement » de la synthèse), l'anneau de focus, la bordure de la recherche au focus, la sélection de texte, `accent-color`, le voile de dépôt plein cadre et la lettre du favicon.
- **Outremer profond** (`ultra-deep`) : survol du bouton principal, rien d'autre.

### Secondary
- **Vermillon** (`verm`) : la couleur de la panne en aplat ou en trait : case bloquée du trajet, trait qui barre un nom bloqué ou un envoi échoué, filet de l'avis d'erreur.
- **Vermillon texte** (`verm-text`) : la même panne quand elle s'écrit : nom bloqué, texte « Bloqué en traitement », compte « bloqués », nom et icône d'un envoi échoué, texte de l'avis d'erreur. Le vermillon plein (`verm`) n'atteint pas 4.5:1 sur le papier ; le texte passe toujours par `verm-text`.

### Neutral
- **Papier** (`paper`) : fond de page, de la barre, du panneau des envois ; aussi la barre blanche qui raye la case bloquée.
- **Papier enfoncé** (`paper-sunk`) : survol de ligne, survol de bouton-icône, lignes squelettes.
- **Encre** (`ink`) : texte, filets (`--rule` est un alias de l'encre), cases franchies du trajet, en-tête inversé du panneau, survol plein des boutons secondaires.
- **Gris** (`grey`) : en-têtes de colonnes, pied de tableau, textes d'aide, placeholder, lien de retour, unités et badge inactif.
- **Blanc** (`white`) : fond des champs (recherche, pupitre), texte sur outremer et sur encre.

### Named Rules
**La règle de l'outremer unique.** Une seule commande outremer par vue. Ailleurs, l'outremer ne dit qu'une chose : « en mouvement » (fichier en traitement, envoi en cours, focus, dépôt). Au pupitre, « Appliquer » est rétrogradé en bouton à filet pour ne pas concurrencer l'action de la vue.

**La règle du vermillon qui cale.** Le vermillon ne sert qu'à la panne et à l'échec. Il est toujours doublé d'une forme (trait qui barre, case rayée, triangle d'alerte) et d'un libellé, pour rester lisible en niveaux de gris et au projecteur.

## Typography

**Display Font:** Bricolage Grotesque Variable (auto-hébergée, axes `opsz`, `wdth`, `wght`), repli `system-ui`
**Body Font:** la même
**Label/Mono Font:** Martian Mono Variable (auto-hébergée, axes `wdth`, `wght`), repli `ui-monospace`

**Character:** une grotesque à axes larges, capable du très gras serré comme du maigre étroit, mise en scène comme un spécimen ; face à elle une mono étroite et légère qui tient les chiffres en colonnes. Le contraste vient des axes de la fonte, pas d'une palette.

### Hierarchy
- **Display** (800, `display`, interlignage 0.8, `opsz` 96) : titre de vue « Mes fichiers ». 3.75rem sous 48rem. Variante `display-results` pour « « requête » » en recherche, coupable n'importe où ; variante `display-drop` pour « Lâchez pour déposer. » plein cadre.
- **Headline** (300, `headline`, largeur 85 %, outremer) : titre d'état vide qui invite au dépôt ; il prend la voix du fichier en route. En état vide « calme » (recherche sans résultat), il passe en 750, largeur 100 %, encre.
- **Title** (750, `title`) : titre du pupitre. La marque « DocShare » (`brand`, 800, largeur 75 %) se tient dans la barre.
- **Nom de fichier** (`name-pending` / `name-done` / `name-stuck`, 1.3125rem) : la signature, voir Components. Le build pilote la largeur par `font-stretch` (85 %, 100 %, 92 %).
- **Body** (400, `body`, 1.0625rem soit 17 px, interlignage 1.45) : texte courant. Textes d'aide à 0.9375rem, plafonnés à 38rem.
- **Commandes** (650, `control`) : boutons ; « Télécharger » à 0.875rem. Les liens-boutons sont en 600, 0.9375rem.
- **Données** (Martian Mono 350, largeur 87.5 %, `tabular-nums`) : `data` (0.875rem) pour synthèse, tailles, dates, états du trajet ; `data-label` (0.8125rem) pour en-têtes de colonnes, pied de tableau, légendes, badges, détail du panneau.

### Named Rules
**La règle des deux voix.** Martian Mono pour les données uniquement (taille, date, état, compte, légende, nom de panne) ; jamais pour la prose ni pour une commande. Tout le reste est en Bricolage Grotesque.

**La règle du poids qui avance.** L'état d'un fichier s'exprime d'abord par les axes de la fonte : maigre et étroit en route, gras et plein une fois disponible. La transition entre les deux dure 300 ms sur la courbe `ease`.

**La règle de la casse normale.** Aucun texte en capitales espacées, aucun surtitre : en-têtes et légendes restent en casse de phrase, en mono grise.

## Layout

Pleine largeur, sans colonne centrée : tout s'aligne sur une gouttière (`gutter`, 2.5rem ; 1rem sous 48rem) et les filets courent d'un bord à l'autre. La barre du haut, collante et haute de 3.5rem, est une grille à trois colonnes : marque à gauche, recherche jusqu'à 40rem au centre, colonne vide symétrique. Les blocs de la zone de travail sont séparés de 3rem (`section`).

L'en-tête de vue est une grille à deux colonnes calée en bas : titre display à gauche, bouton outremer à droite posé sur la ligne de base (0.4rem au-dessus), synthèse mono sur toute la largeur dessous, filet d'encre pour finir. Le tableau suit immédiatement, sans marge latérale : le nom prend toute la place, les colonnes Trajet, Taille, Déposé et Action se limitent à leur contenu ; lignes de 3.75rem (`row`), en-têtes de 2.25rem, 1rem de remplissage, gouttière en première et dernière cellule.

Le panneau des envois est fixé à une gouttière du bord droit et à 2rem du bas, largeur min(24rem, 100vw − 2rem) ; la page réserve sa hauteur via `--tray-space`. Le pupitre `?admin` se place sous la vue, encadré, à une gouttière des bords.

**Sous 48rem :** la barre passe sur une colonne, le titre tombe à 3.75rem, le bouton principal prend toute la largeur. Le tableau devient une pile de lignes en grille (nom puis trajet sur toute la largeur, taille et date en gris en dessous), en-têtes masqués, « Télécharger » seulement pour les fichiers disponibles. Le pupitre empile ses cellules.

## Elevation & Depth

Système plat. Rien ne se distingue par une ombre ou une teinte de surface : la structure est faite de filets d'encre de 1 px et d'aplats. Les seules surfaces inversées (en-tête du panneau en encre, voile de dépôt en outremer) sont des aplats, pas des élévations. Une seule ombre existe, sous le panneau des envois, parce qu'il flotte au-dessus du tableau.

### Shadow Vocabulary
- **Flottant** (`box-shadow: 0 12px 32px -8px rgb(14 14 14 / 0.3)`) : panneau des envois uniquement.

### Named Rules
**La règle du flottant seul.** Seul le panneau des envois porte une ombre. Toute autre surface reste à plat, cernée ou séparée par un filet d'encre.

## Shapes

Rayon 0 partout, imposé à la racine (`* { border-radius: 0 }`) : boutons, champs, panneau, badges, cases du trajet, focus. Les bordures sont des filets d'encre pleins de 1 px ; le filet est la seule ligne du système, sans pointillé ni double trait. Le focus est un contour outremer de 2 px décalé de 2 px ; la recherche au focus double son filet en outremer à l'intérieur. La seule diagonale du système est la rayure de papier à −45° qui barre une case bloquée, écho du trait vermillon qui barre le nom. Le favicon reprend le langage : un carré de papier cerné d'encre portant un D outremer.

## Components

### Buttons
Carrés, francs, à aplat ou à filet ; transitions de couleur de 120 ms linéaires, sans effet de relief.
- **Shape:** angles vifs (0), icône Lucide à gauche espacée de 0.6rem, graisse 650.
- **Primary:** aplat outremer, texte blanc, 2.75rem de haut, 0 1.25rem ; survol outremer profond. Désactivé à 40 % d'opacité.
- **Secondary:** transparent, filet d'encre, texte encre ; au survol il s'inverse (aplat encre, texte papier). Sert à « Choisir sur mon ordinateur » et « Couper ».
- **Télécharger:** même inversion au survol, plus bas (2rem), 0.875rem ; action de ligne.
- **Lien-bouton:** texte souligné de 1 px (2 px au survol), 600 ; « Vérifier à nouveau », « Effacer l'historique », « Actualiser ». Le retour depuis une recherche est un lien-bouton gris sans soulignement, qui passe à l'encre au survol.
- **Bouton-icône:** carré de 2rem sans fond ; papier enfoncé au survol, blanc à 14 % sur l'en-tête encre.
- **Focus:** contour outremer de 2 px décalé de 2 px partout ; blanc sur l'en-tête encre.

### Chips
- **Badges du pupitre :** rectangle à angles vifs, mono `data-label`. Inactive (« Coupée ») : texte et filet gris. Active : le build pose un texte blanc sur aplat vermillon, couple à 4,3:1, sous le seuil AA pour ce corps ; c'est un défaut à corriger, pas un modèle à reproduire.

### Cards / Containers
- **Corner Style:** 0.
- **Background:** papier, comme la page ; aucune carte ne se détache par la couleur.
- **Shadow Strategy:** aucune, sauf le panneau des envois (voir Elevation & Depth).
- **Border:** filet d'encre de 1 px (pupitre, panneau, avis d'erreur) ou filets de séparation seuls (tableau, en-tête de vue, état vide).
- **Internal Padding:** gouttière en latéral pour ce qui touche le bord, 1rem à l'intérieur du pupitre.

### Inputs / Fields
- **Recherche :** fond blanc, filet d'encre, 2.25rem de haut, loupe Lucide à gauche, bouton d'effacement à droite ; au focus le filet passe à l'outremer et se double à l'intérieur (`inset 0 0 0 1px`), sans contour externe.
- **Champs du pupitre :** blanc, filet d'encre, 2.25rem × 6rem, valeur en mono, unité en mono grise à côté.

### Navigation
- **Barre du haut :** papier, filet d'encre en bas, collante. Marque typographique seule (pas de pictogramme) à gauche, recherche au centre. Aucune autre navigation ; le retour depuis une recherche est un lien-bouton gris avec flèche.

### Nom de fichier (signature)
Le nom en 1.3125rem dit l'état par les axes de la fonte et la couleur ; la coupure garde l'extension visible.
- **En traitement :** 300, largeur 85 %, outremer. Non cliquable.
- **Disponible :** 750, largeur 100 %, encre ; lien de téléchargement, souligné de 1 px au survol.
- **Bloqué :** 500, largeur 92 %, vermillon texte, barré d'un trait vermillon de 2 px.
- **Mouvement :** graisse, largeur et couleur glissent en 300 ms sur `cubic-bezier(0.16, 1, 0.3, 1)`.

### Trajet d'un fichier
Trois cases carrées de 14 px espacées de 4 px (Envoyé, Traitement, Disponible), suivies de l'état en mono. Case à venir : vide, filet d'encre. Franchie : aplat encre. Courante : aplat outremer qui clignote en deux temps avec le papier (1.6 s, `steps(2)`). Bloquée : aplat vermillon rayé d'une barre de papier à −45°, suivie d'un lien « Vérifier à nouveau ». La légende de colonne « Envoyé · Traitement · Disponible » nomme les cases.

### Panneau des envois
Rectangle papier cerné d'encre, ombre « flottant », en bas à droite. En-tête inversé (aplat encre, texte blanc) avec titre en 650, détail en mono maigre, boutons replier et fermer. Liste plafonnée à 15rem, entrées séparées par un filet : icône d'état (spinner outremer, triangle vermillon texte), nom en 600, erreur grise ; un envoi échoué a son nom barré de vermillon et porte Réessayer et Retirer.

### Voile de dépôt
Le seul moment plein cadre : glisser un fichier n'importe où couvre l'écran d'un aplat outremer, avec « Lâchez pour déposer. » en `display-drop` blanc calé en bas à gauche et une ligne d'aide en dessous.

### États vides et chargement
- **Vide (dépôt) :** pas de carte ni d'icône : une ligne `headline` outremer, le bouton secondaire à droite, un texte d'aide gris, une légende mono, un filet d'encre.
- **Vide (calme) :** même grille, titre en 750 encre, sans bouton.
- **Chargement :** lignes squelettes de 3.75rem en papier enfoncé, qui basculent en deux temps avec le papier (1.2 s, `steps(2)`).
- **Avis d'erreur :** filet vermillon de 1 px, texte vermillon texte en 600, sans fond.

## Do's and Don'ts

### Do:
- **Do** exprimer l'état d'un fichier par la graisse, la largeur et la couleur de son nom, doublées des cases du trajet et d'un libellé mono.
- **Do** garder une seule commande outremer par vue ; l'outremer dit sinon « en mouvement ».
- **Do** construire avec des filets d'encre de 1 px et des aplats, à rayon 0.
- **Do** écrire le vermillon en `verm-text` dès qu'il porte du texte ; garder `verm` pour les traits et les aplats.
- **Do** mettre toute donnée (taille, date, compte, état, légende) en Martian Mono tabulaire, étroite, en 350.
- **Do** préférer les bascules nettes (`steps(2)`) aux fondus pour les états qui clignotent.
- **Do** respecter `prefers-reduced-motion` : animations et transitions coupées.

### Don't:
- **Don't** arrondir un angle, ni ajouter de carte, de pastille ou de rembourrage SaaS confortable.
- **Don't** poser d'ombre ailleurs que sous le panneau des envois.
- **Don't** utiliser Martian Mono pour la prose ou les commandes, ni une sans-serif générique à la place de Bricolage Grotesque.
- **Don't** utiliser le vermillon hors de la panne et de l'échec, ni l'outremer en décoration.
- **Don't** utiliser de texte en capitales espacées, de surtitres au-dessus des titres, ni de glyphes typographiques en guise d'icônes.
- **Don't** ajouter de thème sombre : le monde est clair seul, pour la salle éclairée et le projecteur.
- **Don't** emprunter les logos, couleurs, la police Marianne ou le DSFR des produits de référence.
