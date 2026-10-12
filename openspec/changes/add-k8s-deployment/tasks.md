## 1. Cluster local

- [ ] 1.1 Écrire `infra/k3d.yaml` (3 agents, ressources suffisantes pour 4 équipes, servicelb actif)
- [ ] 1.2 Documenter les commandes de création de cluster de référence pour GKE Standard et EKS (avec add-on EBS CSI)

## 2. Chart DocShare

- [ ] 2.1 Créer `charts/docshare` : valeurs (image, équipe, ressources, Ingress optionnel)
- [ ] 2.2 StatefulSets Redis et Postgres (une réplique, PVC sans `storageClassName`), Services
- [ ] 2.3 Deployments `api`, `worker` (1 réplique, `WORKER_CONCURRENCY=4`), `notifier`, avec ports nommés `http` / `metrics`, sondes, requêtes et limites
- [ ] 2.4 `PodMonitor` couvrant les trois rôles
- [ ] 2.5 Ingress optionnel avec `ingressClassName` configurable
- [ ] 2.6 Installer sur k3d dans un namespace et vérifier qu'un upload passe `done`

## 3. Monitoring

- [ ] 3.1 `monitoring/values.yaml` : sélecteurs ouverts, scrape 5 s, évaluation 15 s, sans Alertmanager, rétention 2 j, PVC 10 Gi
- [ ] 3.2 Grafana : sidecar de dashboards, accès anonyme lecture seule, Service `LoadBalancer` avec `loadBalancerSourceRanges`
- [ ] 3.3 `values-gke.yaml` et `values-eks.yaml` : désactivation de la collecte du plan de contrôle ; `values-local.yaml`
- [ ] 3.4 Vérifier sur k3d : métriques de l'équipe visibles avec le label `namespace`, aucune alerte active au repos, historique conservé après redémarrage de Prometheus

## 4. Équipes et scripts

- [ ] 4.1 Template par équipe : namespace, `ResourceQuota`, `LimitRange`, ServiceAccount, RoleBinding `edit`
- [ ] 4.2 `scripts/setup.sh` : vérifications préalables, installation du monitoring si absent, `helm upgrade --install` par équipe, génération des kubeconfigs dans `out/kubeconfigs/`
- [ ] 4.3 `scripts/teardown.sh` : suppression d'une équipe ou `--all`
- [ ] 4.4 Ajouter `out/` au `.gitignore`
- [ ] 4.5 Vérifier sur k3d avec 2 équipes : idempotence du script, accès refusé hors du namespace, `port-forward` fonctionnel, isolation des pannes

## 5. Validation sur les cibles managées

- [ ] 5.1 Installer 4 équipes sur GKE Standard (3 × `e2-standard-4`) et relever la consommation réelle par rapport au dimensionnement
- [ ] 5.2 Installer sur EKS (au moins une équipe) et vérifier stockage, LoadBalancer de Grafana et absence d'alertes parasites
