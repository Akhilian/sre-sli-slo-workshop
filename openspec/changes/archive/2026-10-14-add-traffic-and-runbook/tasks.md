## 1. Script k6

- [x] 1.1 Écrire `deploy/helm/docshare/k6/traffic.js` : petit corpus, jeton unique, parcours upload → suivi du statut → recherche du jeton une fois `done`
- [x] 1.2 Scénarios `constant-arrival-rate` avec débits paramétrables par variables d'environnement et `preAllocatedVUs` dimensionnés pour 2 s de latence
- [x] 1.3 Vérifier en local qu'en régime nominal 100 % des recherches renvoient au moins un résultat, et que le débit d'upload tient sous `worker_slow` et `upload_latency`

## 2. Intégration au chart

- [x] 2.1 ConfigMap du script et Job k6 (image `grafana/k6` figée, 3 h, cible `http://api`), débits en valeurs du chart
- [x] 2.2 Ajuster requêtes, limites et quotas pour inclure k6
- [x] 2.3 Vérifier qu'aucune série `k6_*` n'arrive dans Prometheus

## 3. README

Le README existe déjà pour l'application (change `add-docshare-app`) : ces tâches le complètent, sans réécrire les sections existantes.


- [x] 3.1 Prérequis et création du cluster pour EKS (Terraform, EBS CSI) et k3s local (colima) ; GKE abandonné
- [x] 3.2 Installation, distribution des kubeconfigs, accès à Grafana, délai de 15 min de trafic sain
- [x] 3.3 Enrichir les fiches de pannes existantes : commandes via `port-forward`, temps de réaction des SLO et alertes, message pédagogique
- [x] 3.4 Déroulé de la séance de 2 h, remise à zéro, relance du Job k6

## 4. Vérification de bout en bout

- [x] 4.1 Installer deux équipes sur le k3s local avec les solutions SLO appliquées, attendre 15 min de trafic sain
- [x] 4.2 Pour chaque panne, l'activer dans `team-a` seulement : vérifier le SLI dégradé, les SLI intacts et l'absence d'effet sur `team-b`, mesurer le temps de réaction
- [x] 4.3 (prouvé par rejeu `promtool test rules` des règles Sloth générées, séries synthétiques à 1 upload/s ; voir observability.md) `upload_error_rate=0.02` pendant 25 min : burn rate ≈ 4, aucune alerte ; `0.5` : page en moins de 10 min, budget restant entre 0 et 100 %
- [x] 4.4 Consigner les temps mesurés dans le README
- [x] 4.5 (remise à plus tard — infra EKS) Répétition générale sur EKS avec 4 équipes en suivant uniquement le README. Partielle le 2026-10-14 : installation de 4 équipes par `setup.sh` (après correction du NLB interne et du passage de Grafana en `Recreate`), `stale_index` et `worker_slow` repérés dans deux équipes, alertes déclenchées, deux autres équipes intactes. Non couvert sur EKS : les autres pannes et les temps de réaction chronométrés ; les temps mesurés sur le k3s local restent la référence
