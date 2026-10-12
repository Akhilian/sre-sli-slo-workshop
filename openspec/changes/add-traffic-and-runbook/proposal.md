## Why

Sans trafic, aucun SLI ne bouge et aucune panne n'est visible ; sans procédure écrite, l'animateur ne peut ni préparer une séance ni savoir si chaque panne montre ce qu'elle doit montrer. Ce dernier change rend le workshop jouable : un trafic réaliste et constant dans chaque namespace, un README complet, et une vérification de bout en bout du critère de réussite.

## What Changes

- Job k6 par namespace d'équipe, installé par le chart, en `constant-arrival-rate` (1 upload/s, 2 consultations/s, 2 recherches/s) pendant 3 h.
- Scénario de recherche fiable : chaque upload porte un jeton unique, recherché uniquement une fois le document `done`. Un résultat vide est donc toujours anormal, et `worker_slow` ne dégrade pas la qualité.
- `README.md` (déjà créé pour l'application, enrichi ici) : création du cluster par cible, installation, distribution des kubeconfigs, accès à Grafana, déclenchement de chaque panne, ce qu'elle doit montrer et en combien de temps, remise à zéro, déroulé de la séance.
- Vérification de bout en bout : chaque panne n'est visible que par le SLI attendu et uniquement dans son namespace, avec les temps de réaction mesurés.

## Capabilities

### New Capabilities
- `load-generation` : trafic k6 par équipe, débits, scénario de recherche après `done`.
- `workshop-runbook` : documentation de l'animateur et procédure de vérification des pannes.

### Modified Capabilities

Aucune.

## Impact

- Nouveaux fichiers : `k6/traffic.js`, template du Job et de la ConfigMap k6 dans `charts/docshare`, `README.md`.
- Ajuste les quotas du chart pour inclure k6 (déjà prévus dans le dimensionnement).
- Dépend des trois changes précédents ; c'est ici que sont faites les vérifications chronométrées des pannes et des alertes.
