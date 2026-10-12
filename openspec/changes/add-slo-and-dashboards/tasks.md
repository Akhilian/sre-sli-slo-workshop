## 1. Contrôleur Sloth et isolation

- [ ] 1.1 Ajouter l'installation du contrôleur Sloth (chart officiel, version figée) à `scripts/setup.sh`
- [ ] 1.2 Activer `enforcedNamespaceLabel: namespace` et exclure les règles de `monitoring` dans `monitoring/values.yaml`
- [ ] 1.3 Valider sur le k3s local avec deux namespaces : même SLO d'upload appliqué dans les deux, panne dans un seul, burn rates distincts ; sinon basculer sur le repli décrit dans le design
- [ ] 1.4 Vérifier qu'aucune règle de kube-prometheus-stack n'est cassée (page `/rules` sans erreur)

## 2. Définitions de SLO

- [ ] 2.1 Écrire `sloth/upload-availability.yaml` et l'intégrer au chart (installé par défaut dans chaque équipe)
- [ ] 2.2 Écrire les squelettes guidés : `upload-latency.yaml`, `processing-freshness.yaml`, `search-quality.yaml`, `notification-coverage.yaml`
- [ ] 2.3 Écrire les solutions dans `sloth/solutions/`
- [ ] 2.4 Vérifier qu'un squelette en `TODO` appliqué n'affecte ni les autres SLO ni les autres équipes, et que l'erreur est lisible pour un débutant

## 3. Dashboards

- [ ] 3.1 Dashboard par parcours (`grafana/parcours.json`), variable `namespace`, `queue_depth` en `max()`
- [ ] 3.2 Dashboard burn rate (`grafana/burn-rate.json`) : variables `namespace` et SLO, burn rates 5 min / 30 min / 1 h, seuils 14.4 et 6, panneau `ALERTS`
- [ ] 3.3 Panneaux budget restant et temps avant épuisement avec le calcul pour historique court et le texte d'hypothèse ; plage par défaut 3 h
- [ ] 3.4 Empaqueter les JSON en ConfigMaps `grafana_dashboard` (dans le chart du monitoring ou via `setup.sh`)

## 4. Vérification

- [ ] 4.1 Sur le k3s local, avec les solutions appliquées et un trafic minimal (boucle `curl`), vérifier que chaque SLO produit des séries et qu'une panne fait monter le bon burn rate
- [ ] 4.2 Vérifier les dashboards avec deux namespaces : la variable `namespace` isole bien chaque équipe
Les vérifications chronométrées (page en moins de 10 min, petite fuite sans alerte, budget cohérent) sont faites avec le trafic k6 dans le change `add-traffic-and-runbook`
