## ADDED Requirements

### Requirement: Une pile DocShare par namespace
Le chart `charts/docshare` SHALL déployer dans un namespace une pile complète : Deployments `api`, `worker`, `notifier`, StatefulSets Redis et Postgres d'une réplique avec PVC, Services, et un `PodMonitor` couvrant les trois rôles.

#### Scenario: Installation d'une équipe
- **WHEN** l'animateur installe le chart dans `team-a`
- **THEN** tous les pods sont prêts en quelques minutes, sans ordre de démarrage imposé, et un upload de test passe `done`

#### Scenario: Isolation des données et des pannes
- **WHEN** une panne est activée dans `team-a`
- **THEN** le hash `faults`, la file et la base de `team-b` ne sont pas affectés

### Requirement: Capacité fixe
Le chart SHALL déployer le worker avec exactement 1 réplique et `WORKER_CONCURRENCY=4`, et MUST NOT créer d'autoscaler (HPA, KEDA ou autre).

#### Scenario: Panne de lenteur non absorbée
- **WHEN** `worker_slow=10` est active
- **THEN** le nombre de réplicas du worker reste 1 et la file s'engorge

### Requirement: Sondes
Le chart SHALL configurer les sondes de l'API sur `/healthz` et celles du worker et du notifier sur leur port `metrics`.

#### Scenario: Aucune boucle de redémarrage sous panne
- **WHEN** `upload_latency=2.0` est active pendant 15 min
- **THEN** aucun pod API n'est redémarré

### Requirement: Isolation des ressources et des droits
Chaque namespace d'équipe SHALL avoir un `ResourceQuota` et un `LimitRange`, et un ServiceAccount lié au ClusterRole `edit` par un RoleBinding limité au namespace.

#### Scenario: Accès refusé hors du namespace
- **WHEN** une équipe utilise son kubeconfig pour lister les pods de `team-b` ou de `monitoring`
- **THEN** l'API Kubernetes refuse la requête

#### Scenario: Port-forward vers l'API de l'équipe
- **WHEN** une équipe lance `kubectl port-forward svc/api 8000:80 -n team-a`
- **THEN** elle peut appeler `POST /admin/faults` sur sa propre pile

### Requirement: Installation en une commande
`scripts/setup.sh [-y] <cible> a [b ...]` SHALL installer la pile de monitoring si elle est absente, puis pour chaque équipe créer le namespace, les quotas, les droits, la release Helm, et écrire un kubeconfig dans `out/kubeconfigs/<équipe>.yaml`. Le script MUST être idempotent, MUST passer explicitement le contexte kubectl à chaque commande, et MUST demander confirmation hors du k3s local sauf avec `-y`. Les scripts MUST fonctionner avec le bash 3.2 de macOS.

#### Scenario: Session de 4 équipes
- **WHEN** l'animateur lance `scripts/setup.sh gke a b c d` sur un cluster vierge
- **THEN** les 4 piles et le monitoring sont opérationnels et 4 kubeconfigs sont générés, sans autre action manuelle

#### Scenario: Relance
- **WHEN** le script est relancé avec les mêmes arguments
- **THEN** il termine sans erreur et sans recréer les ressources existantes

### Requirement: Kubeconfigs à durée limitée
Les kubeconfigs d'équipe SHALL utiliser un jeton de ServiceAccount obtenu par `kubectl create token` avec une durée de 8 h, sans plugin d'authentification propre au fournisseur.

#### Scenario: Utilisation sans outil cloud
- **WHEN** un participant sans `gcloud` ni `aws` utilise son kubeconfig
- **THEN** `kubectl get pods` fonctionne dans son namespace

### Requirement: Suppression
`scripts/teardown.sh` SHALL supprimer une équipe donnée (namespace et tout son contenu) ou, avec `--all`, toutes les équipes et le monitoring.

#### Scenario: Repartir avec un budget vierge
- **WHEN** une équipe est supprimée puis recréée sous un nouveau nom
- **THEN** ses SLI et son budget ne contiennent aucun historique
