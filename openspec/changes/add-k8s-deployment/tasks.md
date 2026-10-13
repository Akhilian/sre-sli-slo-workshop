## 1. Cluster local

- [x] 1.1 Vérifier le k3s local de colima (stockage `local-path` par défaut, servicelb, images Docker locales visibles par k3s) et documenter la commande `colima start --kubernetes` adaptée à 4 équipes
- [x] 1.2 Documenter les commandes de création de cluster de référence pour GKE Standard et EKS (avec add-on EBS CSI)

## 2. Chart DocShare

- [x] 2.1 Créer `deploy/helm/docshare` : valeurs (image, équipe, ressources, Ingress optionnel)
- [x] 2.2 StatefulSets Redis et Postgres (une réplique, PVC sans `storageClassName`), Services
- [x] 2.3 Deployments `api`, `worker` (1 réplique, `WORKER_CONCURRENCY=4`), `notifier`, avec ports nommés `http` / `metrics`, sondes, requêtes et limites
- [x] 2.4 `PodMonitor` couvrant les trois rôles
- [x] 2.5 Ingress optionnel avec `ingressClassName` configurable
- [x] 2.6 Installer sur le k3s local dans un namespace et vérifier qu'un upload passe `done`

## 3. Monitoring

- [x] 3.1 `deploy/monitoring/values.yaml` : sélecteurs ouverts, scrape 5 s, évaluation 15 s, sans Alertmanager, rétention 2 j, PVC 10 Gi
- [x] 3.2 Grafana : sidecar de dashboards, accès anonyme lecture seule, Service `LoadBalancer` avec `loadBalancerSourceRanges`
- [x] 3.3 `values-gke.yaml` et `values-eks.yaml` : désactivation de la collecte du plan de contrôle ; `values-local.yaml`
- [x] 3.4 Vérifier sur le k3s local : métriques de l'équipe visibles avec le label `namespace`, aucune alerte active au repos, historique conservé après redémarrage de Prometheus

## 4. Équipes et scripts

- [x] 4.1 Template par équipe : namespace, `ResourceQuota`, `LimitRange`, ServiceAccount, RoleBinding `edit`
- [x] 4.2 `deploy/scripts/setup.sh` : vérifications préalables, installation du monitoring si absent, `helm upgrade --install` par équipe, génération des kubeconfigs dans `out/kubeconfigs/`
- [x] 4.3 `deploy/scripts/teardown.sh` : suppression d'une équipe ou `--all`
- [x] 4.4 Ajouter `out/` au `.gitignore`
- [x] 4.5 Vérifier sur le k3s local avec 2 équipes : idempotence du script, accès refusé hors du namespace, `port-forward` fonctionnel, isolation des pannes

## 5. Validation sur les cibles managées

- [ ] 5.1 (remise à plus tard — infra GKE) Installer 4 équipes sur GKE Standard (3 × `e2-standard-4`) et relever la consommation réelle par rapport au dimensionnement
- [ ] 5.2 (remise à plus tard — infra EKS) Installer sur EKS (au moins une équipe) et vérifier stockage, LoadBalancer de Grafana et absence d'alertes parasites
