# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Participants d'un atelier SLI / SLO de 2 h** : des développeurs sans connaissance SRE, répartis en équipes (jusqu'à 4 par session, un namespace Kubernetes chacune). Ils ouvrent l'interface sur leur portable (`kubectl port-forward svc/web`), déposent et cherchent des fichiers, et vivent les pannes comme des utilisateurs avant de les retrouver dans leurs SLI et dans Grafana.
- **Animateur** : il pilote les pannes depuis le pupitre (`?admin`) et projette l'interface au vidéoprojecteur pour montrer ce que voit un utilisateur pendant une panne.

## Product Purpose

DocShare est un service fictif de partage de documents, support du workshop : on dépose un fichier, il est traité (OCR simulé, indexation), il devient recherchable et téléchargeable, et une notification part. L'interface rend ce système concret et donne un point de vue utilisateur sur chaque panne, à confronter ensuite aux mesures côté serveur.

Succès : un participant comprend en quelques secondes ce que vit l'utilisateur (dépôt en échec, document bloqué en traitement, recherche vide), et l'animateur déclenche et coupe une panne sans hésiter.

## Positioning

Face aux participants, DocShare doit se présenter comme un vrai produit crédible : ils se mettent dans la peau de ses utilisateurs et des équipes qui l'exploitent. Le pupitre des pannes est la seule partie qui assume d'être un outil d'animation.

## Operating Context

- Salle de formation : portables des participants et vidéoprojecteur de l'animateur, vus en même temps que Grafana.
- Trafic de fond généré par k6 (1 upload par seconde et par équipe) : la liste « Mes documents » ne montre que les dépôts du navigateur, pas ce trafic.
- Mode `standalone` pour une démo sur un poste, sans cluster.
- Langue de l'interface et du workshop : français.

## Capabilities and Constraints

- Parcours : dépôt de fichiers par glisser-déposer ou sélecteur (plusieurs à la fois, 5 Mio au plus chacun), suivi du statut (`pending`, `done`, bloqué après 60 s), recherche (texte des fichiers texte, titre des autres), téléchargement, pupitre des cinq pannes derrière `?admin`.
- Angles morts voulus, à ne jamais corriger dans l'interface : une recherche en échec s'affiche comme « Aucun résultat » ; un document non indexé (`stale_index`) apparaît traité comme les autres ; aucun état de notification n'est montré ; aucune métrique ni télémétrie côté navigateur.
- Le pupitre n'est pas une sécurité : il est seulement masqué sans `?admin`.
- Stack : Vue 3 + Vite, JavaScript, sans bibliothèque de composants ; servi par nginx qui relaie `/api/` vers l'API.

## Brand Commitments

DocShare est fictif, sans logo, couleurs ni charte imposés.

Préférence de l'utilisateur (2026-10-13) : l'interface doit ressembler à un vrai outil de partage de fichiers, au niveau de finition de Google Drive, WeTransfer et La Suite numérique (Fichiers), avec la structure d'un gestionnaire de fichiers. Ces produits fixent le niveau d'exigence, pas une identité à copier : ni leurs logos, ni leurs couleurs, ni la police Marianne ou le DSFR, réservés à l'État.

## Evidence on Hand

Aucune donnée réelle d'utilisateurs, aucun témoignage ni client : rien de cela ne doit être inventé dans l'interface.

## Product Principles

1. L'utilisateur voit ce qu'un utilisateur verrait : l'interface ne révèle jamais ce que le serveur masque.
2. Chaque état d'un fichier (envoi, échec, en traitement, bloqué, traité) se lit d'un coup d'œil, y compris projeté.
3. Une panne se voit comme une gêne d'usage, pas comme un message technique.
4. Crédible avant d'être démonstratif : rien ne trahit l'atelier dans la vue participant.

## Accessibility & Inclusion

- Lisible au vidéoprojecteur : contrastes francs et tailles de texte suffisantes pour une lecture à distance.
- Utilisable au clavier : le sélecteur de fichiers remplace le glisser-déposer.
