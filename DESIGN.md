---
name: DocShare
description: Gestionnaire de fichiers crédible dont chaque ligne raconte le trajet du fichier, comme un suivi de colis.
colors:
  navy: "#14213d"
  navy-soft: "#24345a"
  saffron: "#f5b700"
  saffron-hover: "#ffc72c"
  saffron-edge: "#d29c00"
  ground: "#eef1f5"
  surface: "#ffffff"
  surface-sunk: "#f6f8fb"
  line: "#d3d9e3"
  line-strong: "#aab4c4"
  ink: "#141c2e"
  muted: "#4b566b"
  progress: "#1d5bd0"
  progress-bg: "#e5edfc"
  ok: "#10704d"
  ok-bg: "#def3e9"
  alert: "#bd2318"
  alert-bg: "#fdebe9"
  idle: "#c3cad6"
typography:
  display:
    fontFamily: "'Atkinson Hyperlegible Next Variable', 'Atkinson Hyperlegible', system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "'Atkinson Hyperlegible Next Variable', 'Atkinson Hyperlegible', system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.5
  title:
    fontFamily: "'Atkinson Hyperlegible Next Variable', 'Atkinson Hyperlegible', system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.5
  body:
    fontFamily: "'Atkinson Hyperlegible Next Variable', 'Atkinson Hyperlegible', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  body-strong:
    fontFamily: "'Atkinson Hyperlegible Next Variable', 'Atkinson Hyperlegible', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.5
  label:
    fontFamily: "'Atkinson Hyperlegible Next Variable', 'Atkinson Hyperlegible', system-ui, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 700
    lineHeight: 1.5
  mono:
    fontFamily: "ui-monospace, 'SF Mono', Menlo, monospace"
    fontSize: "0.875em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  overlay: "1.25rem"
  pill: "999px"
spacing:
  xs: "0.5rem"
  sm: "0.75rem"
  md: "1.1rem"
  lg: "1.5rem"
  xl: "2.5rem"
  step: "1.5rem"
  step-gap: "3.6rem"
  page: "76rem"
components:
  topbar:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.surface}"
    padding: "0.75rem 1.5rem"
  search-input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "2.75rem"
    padding: "0 2.75rem 0 2.9rem"
  button-primary:
    backgroundColor: "{colors.saffron}"
    textColor: "{colors.navy}"
    rounded: "{rounded.md}"
    height: "2.75rem"
    padding: "0 1.15rem"
  button-primary-hover:
    backgroundColor: "{colors.saffron-hover}"
    textColor: "{colors.navy}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.navy}"
    rounded: "{rounded.md}"
    height: "2.75rem"
    padding: "0 1.15rem"
  button-secondary-hover:
    backgroundColor: "{colors.surface-sunk}"
  button-ghost:
    textColor: "{colors.navy}"
    rounded: "{rounded.md}"
    height: "2.4rem"
    padding: "0 0.8rem"
  button-ghost-hover:
    backgroundColor: "{colors.surface-sunk}"
  file-table:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0.95rem 1.1rem"
  file-table-head:
    backgroundColor: "{colors.surface-sunk}"
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    padding: "0.7rem 1.1rem"
  file-table-row-stuck:
    backgroundColor: "{colors.alert-bg}"
  track-step-idle:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    size: "{spacing.step}"
  track-step-pending:
    backgroundColor: "{colors.progress}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    size: "{spacing.step}"
  track-step-done:
    backgroundColor: "{colors.ok}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    size: "{spacing.step}"
  track-step-stuck:
    backgroundColor: "{colors.alert}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    size: "{spacing.step}"
  tray:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    width: "24rem"
  tray-head:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.surface}"
    padding: "0.55rem 0.6rem 0.55rem 1.1rem"
  tray-head-failed:
    backgroundColor: "{colors.alert}"
    textColor: "{colors.surface}"
  notice-error:
    backgroundColor: "{colors.alert-bg}"
    textColor: "{colors.alert}"
    rounded: "{rounded.md}"
    padding: "0.9rem 1.1rem"
  badge-active:
    backgroundColor: "{colors.alert}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    padding: "0.1rem 0.55rem"
  badge-off:
    backgroundColor: "{colors.surface-sunk}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: "0.1rem 0.55rem"
---

# Design System: DocShare

## Overview

**Creative North Star: "Le suivi de colis"**

DocShare se présente comme un vrai gestionnaire de fichiers, au niveau de finition de Drive ou de La Suite Fichiers, sans en emprunter l'identité. La structure est celle du canon : une barre du haut bleu nuit qui porte le nom et une recherche large, un fond gris froid, un tableau blanc à lignes généreuses, une action principale safran. Ce qui lui est propre tient dans une seule pièce : chaque ligne montre le trajet du fichier en trois étapes (Envoyé, Traitement, Disponible), comme un suivi de livraison. Pendant une panne, le trajet cale visiblement sur l'étape de traitement.

Le système est pensé pour être lu à distance : base typographique à 17 px, Atkinson Hyperlegible Next, contrastes francs, trois couleurs d'état qui ne servent qu'à dire l'état. Il est volontairement dense mais aéré, plat, et clair uniquement : l'écran est vu dans une salle éclairée et au vidéoprojecteur. La profondeur est réservée à ce qui flotte au-dessus du travail (panneau des envois, voile de dépôt).

**Key Characteristics:**
- Barre bleu nuit pleine largeur, collante, avec la recherche au centre.
- Une seule action safran par vue, texte bleu nuit.
- Trois états codés couleur et forme : bleu en cours, vert disponible, rouge bloqué ou en échec.
- Le trajet en trois pastilles reliées, signature de chaque ligne.
- Surfaces plates bordées d'un filet ; seule l'interface flottante porte une ombre.
- Icônes Lucide à trait unique, jamais de glyphes typographiques.

## Colors

Une palette de bureau froide (bleu nuit, gris bleutés) traversée par un seul accent chaud, le safran, et par trois couleurs d'état strictement sémantiques.

### Primary
- **Bleu nuit** (`navy`) : barre du haut, en-tête du panneau des envois, texte des boutons, fond de la marque dans le favicon. C'est la couleur de la structure, pas de l'action.
- **Bleu nuit adouci** (`navy-soft`) : icônes de type de fichier et icône des états vides, un cran sous le bleu nuit pour ne pas concurrencer le texte.

### Secondary
- **Safran** (`saffron`) : l'action principale (« Déposer des fichiers »), le pictogramme de la marque, le cadre pointillé et l'icône du voile de dépôt, l'anneau de focus et la bordure de focus de la recherche sur fond bleu nuit, la sélection de texte (à 45 %).
- **Safran clair** (`saffron-hover`) : survol du bouton principal.
- **Arête safran** (`saffron-edge`) : filet d'1 px qui détoure le bouton principal sur fond clair.

### Tertiary (états)
- **Bleu traitement** (`progress`, fond `progress-bg`) : fichier en cours, étapes franchies d'un trajet en cours, synthèse « en traitement », anneau de focus par défaut et `accent-color`.
- **Vert disponible** (`ok`, fond `ok-bg`) : trajet complet, synthèse « disponibles », envoi réussi.
- **Rouge bloqué** (`alert`, fond `alert-bg`) : trajet calé, ligne bloquée teintée, envoi en échec, en-tête du panneau en échec, panne active au pupitre, message d'erreur.
- **Gris en attente** (`idle`) : pastilles et segments du trajet pas encore atteints.

### Neutral
- **Fond de page** (`ground`) : gris froid clair derrière tout le contenu.
- **Surface** (`surface`) : tableau, panneau des envois, état vide, pupitre, champ de recherche.
- **Surface enfoncée** (`surface-sunk`) : en-tête du tableau, survol de ligne et de bouton fantôme, badge inactif.
- **Filet** (`line`) : bordures de tableau et séparateurs de lignes. **Filet appuyé** (`line-strong`) : pointillé de l'état vide, champs du pupitre.
- **Encre** (`ink`) : texte courant. **Texte atténué** (`muted`) : en-têtes de colonnes, métadonnées (taille, date), textes d'aide, placeholder.

### Named Rules
**La règle du safran unique.** Le safran signale l'action principale de la vue, et une seule à la fois ; ailleurs il ne sert qu'à la marque, au dépôt et au focus sur fond bleu nuit. Les actions secondaires sont blanches bordées de bleu nuit ou fantômes.

**La règle des états dédiés.** Bleu, vert et rouge ne servent qu'à dire l'état d'un fichier, d'un envoi ou d'une panne. Jamais en décoration, jamais en couleur de section. Chaque état est aussi porté par une forme (coche, triangle d'alerte, point pulsé) et un libellé, pour rester lisible en niveaux de gris et au projecteur.

## Typography

**Display Font:** Atkinson Hyperlegible Next (variable, auto-hébergée via `@fontsource-variable`), repli Atkinson Hyperlegible puis `system-ui`
**Body Font:** la même
**Label/Mono Font:** pile monospace système (`ui-monospace`, SF Mono, Menlo) pour le seul `code`

**Character:** une seule famille, conçue pour la lisibilité basse vision : formes de lettres très distinctes, chiffres sans ambiguïté, idéale pour un écran projeté. La hiérarchie vient de la taille et de la graisse, pas d'un contraste de familles.

### Hierarchy
- **Display** (700, `display`) : titre de vue (« Mes fichiers », « Résultats pour… »). Interlettrage légèrement resserré.
- **Headline** (700, `headline`) : message du voile de dépôt plein écran.
- **Title** (700, `title`) : titre de l'état vide, titre du pupitre. La marque dans la barre se situe juste au-dessus (1.3rem, 700).
- **Body** (400, `body`) : texte courant, métadonnées. La racine est à 106,25 % (17 px). Longueur de ligne des textes d'aide limitée à 34rem.
- **Body strong** (600) : noms de fichiers, synthèse des états, boutons fantômes et liens-boutons, libellés d'état. Les boutons pleins et les libellés du trajet passent à 700.
- **Label** (700, `label`) : en-têtes de colonnes et légende du trajet, en `muted`, casse normale. Le pied de tableau, les erreurs et les aides utilisent la même taille (0.9rem) en 400.

### Named Rules
**La règle des chiffres alignés.** Tout ce qui se compte ou se compare (synthèse, durées du trajet, tailles, dates) est en chiffres tabulaires (`font-variant-numeric: tabular-nums`), aligné à droite dans le tableau.

**La règle de la casse normale.** Aucun texte en capitales ni espacé : les en-têtes et légendes restent en casse de phrase, en graisse 700 et couleur atténuée.

## Layout

Une colonne de travail centrée, plafonnée à `page` (76rem), sous une barre collante pleine largeur. La barre est une grille à trois colonnes (marque à gauche, recherche jusqu'à 44rem au centre, colonne vide symétrique à droite). La zone de travail a une marge de 1.5rem et sépare ses blocs de 2.5rem ; l'en-tête de vue aligne titre et synthèse à gauche, action safran à droite, sur une même ligne de base basse.

Le tableau des fichiers est le cœur : le nom prend toute la place restante, les colonnes Trajet, Taille, Déposé et Action se limitent à leur contenu. Cellules à 0.95rem × 1.1rem, en-têtes à 0.7rem × 1.1rem. Le trajet utilise ses propres mesures : pastille `step` (1.5rem), segment `step-gap` (3.6rem) ; la légende de l'en-tête est une grille calée sur le pas du trajet pour centrer chaque libellé au-dessus de sa pastille.

Le panneau des envois est fixé en bas à droite (1.5rem du bord, largeur min(24rem, 100vw − 2rem)) ; la zone de travail réserve sa hauteur en marge basse via `--tray-space`. Le pupitre `?admin` se place sous la vue, jamais par-dessus.

**Sous 48rem :** la barre passe sur une colonne (marque puis recherche), la marge tombe à 1rem, le bouton principal prend toute la largeur. Le tableau devient une liste de cartes-lignes : en-tête masqué, nom puis trajet sur toute la largeur, taille et date masquées, « Télécharger » seulement pour les fichiers disponibles. La légende passe en une phrase au-dessus de la liste et le trajet se resserre (pastilles 1.25rem, segments 1rem).

## Elevation & Depth

Système plat par défaut. Les surfaces posées sur la page (tableau, état vide, pupitre) se distinguent du fond par le blanc et un filet de 1 px, pas par une ombre. La profondeur est réservée à ce qui flotte au-dessus du travail.

### Shadow Vocabulary
- **Flottant** (`box-shadow: 0 10px 28px -6px rgb(20 33 61 / 0.28), 0 2px 6px rgb(20 33 61 / 0.12)`) : panneau des envois, seul élément ancré au-dessus du contenu.
- **Appui** (`box-shadow: 0 1px 2px rgb(20 33 61 / 0.18)`) : sous le bouton safran au repos, retiré à l'appui.
- **Voile** (fond `rgb(20 33 61 / 0.78)`) : voile de dépôt plein écran, teinté bleu nuit plutôt qu'ombré.

### Named Rules
**La règle du flottant seul.** Seul ce qui flotte (panneau, voile) porte une ombre ou un voile. Une surface posée dans le flux reste plate et bordée. Les ombres sont teintées bleu nuit, jamais noires.

## Shapes

Angles doucement arrondis et constants : 8 px (`md`) pour tout ce qui se manipule (boutons, champ de recherche, avis, champs), 12 px (`lg`) pour les conteneurs (tableau, panneau, état vide, pupitre), 1.25rem pour le cadre du voile de dépôt. Le cercle est réservé aux pastilles du trajet, aux points de synthèse et aux boutons-icônes ; la pilule aux badges du pupitre. Les bordures sont des filets fins (1 à 2 px) ; le pointillé n'existe que pour une cible de dépôt (2 px `line-strong` dans l'état vide, 3 px safran dans le voile). La marque est une feuille au coin plié, safran, portant une flèche montante bleu nuit.

## Components

### Buttons
Francs et calmes : grande cible (2.75rem), graisse 700, transitions de couleur de 150 ms.
- **Shape:** arrondi doux (8 px), icône Lucide à gauche, espacée de 0.55rem.
- **Primary:** fond safran, texte bleu nuit, filet `saffron-edge`, ombre d'appui ; survol safran clair, ombre retirée à l'appui. Désactivé à 45 % d'opacité.
- **Secondary:** fond blanc, bordure bleu nuit de 1.5 px, texte bleu nuit ; survol `surface-sunk`. Sert d'action dans l'état vide (« Choisir sur mon ordinateur »).
- **Ghost:** plus bas (2.4rem), sans fond, graisse 600 ; au survol un fond `surface-sunk` et un filet apparaissent. Action de ligne (« Télécharger »).
- **Lien-bouton:** texte bleu nuit souligné de 1 px, 2 px au survol ; actions discrètes (« Vérifier à nouveau », « Effacer l'historique »).
- **Bouton-icône:** cercle de 2.25rem, sans fond ; voile bleu nuit à 8 % au survol, blanc à 12 % sur fond bleu nuit.
- **Focus:** anneau de 3 px `progress` décalé de 2 px partout ; safran sur fond bleu nuit.

### Chips
- **Badges du pupitre :** pilule 0.9rem / 700. Panne active : rouge plein, texte blanc. Inactive : `surface-sunk`, texte atténué, filet.
- **Synthèse des états :** point coloré de 0.7rem suivi du compte, dans la couleur de l'état, graisse 600.

### Cards / Containers
- **Corner Style:** 12 px.
- **Background:** blanc sur fond `ground`.
- **Shadow Strategy:** aucune (voir Elevation & Depth), sauf le panneau des envois.
- **Border:** filet `line` de 1 px.
- **Internal Padding:** 1.1rem latéral dans le tableau, 1.25rem au pupitre, 3.5rem × 1.5rem pour l'état vide.

### Inputs / Fields
- **Recherche :** champ blanc de 2.75rem dans la barre bleu nuit, arrondi 8 px, loupe atténuée à gauche, bouton d'effacement à droite ; bordure transparente de 2 px qui devient safran au focus (pas d'anneau).
- **Champs du pupitre :** 2.4rem, filet `line-strong`, arrondi 8 px, unité atténuée à 0.85rem à côté.

### Navigation
- **Barre du haut :** bleu nuit plein, collante, texte blanc. Marque (pictogramme safran 30 px + « DocShare » 1.3rem / 700) à gauche, recherche au centre. Pas d'autre navigation ; le retour depuis une recherche est un lien-bouton atténué avec flèche.

### Trajet d'un fichier (signature)
Trois pastilles de 1.5rem (Envoyé, Traitement, Disponible) reliées par des segments de 3 px, suivies d'un libellé d'état en 700 dans la couleur de l'état.
- **Attente :** pastille blanche, bordure `idle` de 2 px, segment `idle`.
- **En cours :** étape franchie pleine bleue avec coche ; l'étape de traitement a un anneau bleu et un point central qui pulse (1.4 s) ; libellé « En traitement · durée ».
- **Disponible :** tout le trajet vert, coches blanches ; libellé « Disponible en durée ».
- **Bloqué :** le trajet se colore en rouge jusqu'à l'étape de traitement, qui porte un triangle d'alerte ; la dernière reste en attente ; la ligne entière prend le fond `alert-bg` ; un lien « Vérifier à nouveau » suit le libellé.
- **Mouvement :** les segments se remplissent de gauche à droite (500 ms) et les pastilles changent de couleur (300 ms), courbe `ease` (`cubic-bezier(0.16, 1, 0.3, 1)`).

### Panneau des envois
Carte flottante en bas à droite : en-tête bleu nuit (rouge quand des envois ont échoué et qu'aucun n'est en cours) avec titre, détail atténué et boutons replier / fermer ; liste plafonnée à 16rem. Chaque envoi : icône d'état (spinner bleu, coche verte, triangle rouge), nom tronqué, erreur en rouge 0.9rem, boutons Réessayer et Retirer. Entrée en glissant de 1rem vers le haut (250 ms).

### Voile de dépôt
Glisser un fichier n'importe où affiche un voile bleu nuit à 78 % sur tout l'écran, avec un cadre pointillé safran de 3 px, une icône de nuage safran et un message blanc 1.5rem / 700.

### États vides et chargement
- **Vide (dépôt) :** carte blanche à pointillé `line-strong`, icône nuage 48 px en `navy-soft`, titre, texte d'aide atténué, bouton secondaire.
- **Vide (calme) :** même carte avec un filet plein, sans invitation au dépôt (recherche sans résultat).
- **Chargement :** lignes squelettes de 3.4rem avec un reflet horizontal (1.2 s).
- **Avis d'erreur :** bandeau `alert-bg`, texte rouge 600, arrondi 8 px.

## Do's and Don'ts

### Do:
- **Do** garder une seule action safran par vue, texte bleu nuit.
- **Do** exprimer chaque état par la couleur, une forme (coche, triangle, point pulsé) et un libellé.
- **Do** montrer la progression d'un fichier avec le trajet en trois étapes, et laisser un échec caler visiblement le trajet.
- **Do** garder les surfaces posées plates (blanc + filet `line` de 1 px, arrondi 12 px) et réserver l'ombre « flottant » à ce qui flotte.
- **Do** utiliser les icônes Lucide à trait unique (14 à 20 px dans l'interface, 48 px pour les états vides).
- **Do** mettre en chiffres tabulaires toute quantité, durée, taille ou date.
- **Do** respecter `prefers-reduced-motion` : animations et transitions coupées.

### Don't:
- **Don't** utiliser bleu, vert ou rouge hors de leur sens d'état.
- **Don't** ajouter de thème sombre : le monde est clair seul, pour la salle éclairée et le projecteur.
- **Don't** emprunter les logos, couleurs, la police Marianne ou le DSFR des produits de référence.
- **Don't** empiler des panneaux blancs ou des pastilles décoratives : un tableau, des lignes, un trajet.
- **Don't** utiliser de texte en capitales espacées, de surtitres au-dessus des titres, ni de glyphes typographiques en guise d'icônes.
- **Don't** utiliser le pointillé ailleurs que sur une cible de dépôt.
- **Don't** descendre la base sous 17 px ni un texte secondaire sous 0.85rem.
