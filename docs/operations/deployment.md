# Déploiement et exécution

## Lancer l'application en local

### En un seul processus (mode standalone)

Sans Redis ni Postgres : l'API, le worker et le notifier tournent dans un seul processus, sur des adaptateurs en mémoire. Pratique pour découvrir l'application ou préparer une démo. Les données et les pannes actives sont perdues à l'arrêt.

```bash
docker build -t docshare:dev .
docker run --rm -p 8000:8000 -e ROLE=standalone docshare:dev

# ou sans Docker (Python 3.12)
pip install -r app/requirements.txt
ROLE=standalone python app/main.py
```

Tout fonctionne comme en mode distribué : routes, pannes (`/admin/faults`) et métriques. `GET /metrics` de l'API expose alors les métriques des trois rôles. Le trafic k6 peut viser ce mode (`k6 run -e API_URL=http://localhost:8000 -e DURATION=10m deploy/helm/docshare/k6/traffic.js`), mais il n'y a ni Prometheus ni Sloth : lisez `/metrics` directement.

### Pile distribuée avec Docker

Prérequis : Docker.

```bash
docker build -t docshare:dev .
docker network create docshare

docker run -d --name redis --network docshare redis:7.4-alpine
docker run -d --name postgres --network docshare \
  -e POSTGRES_USER=docshare -e POSTGRES_PASSWORD=docshare -e POSTGRES_DB=docshare \
  postgres:16-alpine

docker run -d --name api --network docshare -p 8000:8000 -e ROLE=api \
  -e REDIS_URL=redis://redis:6379/0 \
  -e DATABASE_URL=postgresql://docshare:docshare@postgres:5432/docshare \
  docshare:dev
docker run -d --name worker --network docshare -p 9100:9100 -e ROLE=worker \
  -e REDIS_URL=redis://redis:6379/0 \
  -e DATABASE_URL=postgresql://docshare:docshare@postgres:5432/docshare \
  docshare:dev
docker run -d --name notifier --network docshare -p 9101:9100 -e ROLE=notifier \
  -e REDIS_URL=redis://redis:6379/0 \
  docshare:dev
```

L'ordre de démarrage n'a pas d'importance : chaque rôle réessaie toutes les 2 s tant que Redis ou Postgres ne répond pas, et l'API crée le schéma au démarrage.

> Piège zsh : ne factorisez pas les options dans une variable (`E="-e A=1 -e B=2"; docker run $E ...`). zsh ne découpe pas la variable en mots et Docker reçoit une seule option mal formée. Écrivez les `-e` en entier comme ci-dessus.

Arrêt et nettoyage :

```bash
docker rm -f api worker notifier redis postgres && docker network rm docshare
```

### Configuration

| Variable | Rôles | Défaut | Rôle |
| --- | --- | --- | --- |
| `ROLE` | tous | (obligatoire) | `api`, `worker`, `notifier` ou `standalone` ; toute autre valeur arrête le processus |
| `REDIS_URL` | api, worker, notifier | `redis://localhost:6379/0` | files de jobs et hash des pannes |
| `DATABASE_URL` | api, worker | `postgresql://docshare:docshare@localhost:5432/docshare` | documents et index |
| `PORT` | api, standalone | `8000` | port HTTP de l'API (métriques comprises) |
| `METRICS_PORT` | worker, notifier | `9100` | port des métriques, utilisable aussi comme sonde |
| `WORKER_CONCURRENCY` | worker, standalone | `4` | jobs traités en parallèle (capacité ≈ 2 jobs/s) |
| `MAX_UPLOAD_BYTES` | api, standalone | `5242880` | taille maximale d'un fichier déposé (5 Mio), au-delà 413 |


## Déployer sur Kubernetes

Un cluster partagé, un namespace par équipe (`team-<nom>`) avec sa pile DocShare complète, et un monitoring commun dans `monitoring` (kube-prometheus-stack : Prometheus, Grafana, sans Alertmanager).

### Prérequis

Sur le poste de l'animateur : `kubectl` et `helm`. Les participants n'ont besoin que de `kubectl`.

| Cible | Création du cluster de référence | Prérequis |
| --- | --- | --- |
| Local | `colima start --kubernetes --cpu 6 --memory 10 --disk 60` | aucun ; l'image se construit localement (`docker build -t docshare:dev .`), le k3s de colima l'utilise sans registre |
| EKS | Terraform, `deploy/terraform/eks` (voir ci-dessous) | AWS CLI authentifié, `terraform` ≥ 1.6 ; crée VPC, cluster, 2 à 3 nœuds `m6i.xlarge` selon le nombre d'équipes, add-on EBS CSI, classe `gp3` par défaut et AWS Load Balancer Controller |

Sur EKS, les images viennent de Docker Hub (`akhilian/docshare` et `akhilian/docshare-web`, dépôts publics pour que le cluster les tire sans identifiants). La CI les publie avec le secret GitHub `DOCKERHUB_TOKEN` (jeton d'accès Docker Hub en écriture) ; pour un autre compte, changez `DOCKERHUB_USER` dans `.github/workflows/image.yml` et `deploy/environments/eks/docshare.yaml`.

#### Provisionner EKS avec Terraform

```bash
cd deploy/terraform/eks
terraform init
terraform apply -var 'api_allowed_cidrs=["203.0.113.10/32"]'   # IP de la salle, 0.0.0.0/0 refusé
$(terraform output -raw kubeconfig_command)                    # contexte kubectl de l'animateur
```

Variables optionnelles : `region` (`eu-west-3`), `cluster_name` (`docshare`), `kubernetes_version`, `node_instance_type` (`m6i.xlarge`) ; `teams` (4) fixe le nombre de nœuds : `max(2, ⌈(1,5 + 0,6 × équipes) / 3⌉)` soit 2 nœuds jusqu'à 7 équipes (donc 2 pour 4) (3 vCPU utilisables par nœud). L'état Terraform reste local (`*.tfstate` est ignoré par git). Le cluster coûte tant qu'il existe : `terraform destroy` après la séance, une fois les équipes supprimées (`deploy/scripts/teardown.sh --all`) pour libérer les LoadBalancers créés par Kubernetes, sans quoi la suppression du VPC échoue.

Dimensionnement (ressources demandées) : ~0,6 vCPU et ~1 Gi par équipe, ~1,5 vCPU et ~3 Gi pour le monitoring, soit ~4 vCPU et ~7 Gi pour 4 équipes. En local, 4 vCPU suffisent pour 2 équipes ; prévoir 6 vCPU pour 4.

### Installation

```bash
# Local (contexte kubectl « colima »)
docker build -t docshare:dev .
deploy/scripts/setup.sh local a b

# EKS : l'accès à Grafana est restreint aux plages indiquées (IP de la salle)
GRAFANA_SOURCE_RANGES=203.0.113.10/32 deploy/scripts/setup.sh eks a b c d
```

Le script affiche le contexte kubectl et demande confirmation hors du k3s local (`-y` pour ne pas demander, `KUBE_CONTEXT=<contexte>` pour en choisir un autre que le contexte courant). Il est idempotent : le relancer met à jour sans recréer. Il installe ou met à jour le monitoring, puis pour chaque équipe :
- le namespace `team-<nom>`, un quota et des valeurs par défaut de ressources ;
- la pile DocShare (api, worker à 1 réplique sans autoscaling, notifier, Redis, Postgres) et sa collecte de métriques ;
- un ServiceAccount aux droits `edit` limités au namespace, et son kubeconfig dans `out/kubeconfigs/<nom>.yaml` (jeton valable 8 h, `TOKEN_DURATION` pour changer).

Lancez l'installation au moins 15 min avant la séance : les fenêtres d'une heure des alertes ont besoin d'un historique sain pour que les pannes réagissent dans les temps annoncés.

À la fin, il affiche l'adresse de Grafana (port 3000, lecture anonyme ; le mot de passe admin est dans le secret `kps-grafana` du namespace `monitoring`).

### Trafic

Chaque équipe reçoit un trafic constant, sans action de sa part : un Job k6 (`k6-<révision>`) démarre avec l'installation et tourne 3 h. Script : `deploy/helm/docshare/k6/traffic.js`.

Débits par défaut : 1 upload/s, ~1,5 consultation/s, 2 recherches/s. Chaque upload contient un jeton unique (`doc-xxxxxxxx`) ; k6 consulte le document jusqu'à ce qu'il soit `done` (60 s au plus), puis recherche ce jeton. On ne cherche donc que des documents traités : une recherche vide signale un index périmé (`stale_index`), jamais un simple retard (`worker_slow`).

Le débit d'upload ne baisse pas quand l'API ralentit (`constant-arrival-rate`). Les métriques de k6 ne sont exportées nulle part : les SLI se mesurent uniquement côté serveur.

```bash
kubectl get jobs -n team-a                 # Job en cours
deploy/scripts/setup.sh local a            # relancer le trafic pour 3 h (remplace le Job)
```

Réglages dans les valeurs du chart : `k6.uploadRate`, `k6.searchesPerDoc`, `k6.duration`, `k6.enabled`.

### Côté équipe

```bash
export KUBECONFIG=out/kubeconfigs/a.yaml
kubectl get pods
kubectl port-forward svc/api 8000:80
# l'API de l'équipe répond sur localhost:8000 (voir « Utiliser l'API » et « Pannes »)
```

Une équipe ne voit que son namespace : `kubectl get pods -n team-b` ou `-n monitoring` est refusé.

### Suppression

```bash
deploy/scripts/teardown.sh b        # supprime l'équipe b et son kubeconfig
deploy/scripts/teardown.sh --all    # supprime toutes les équipes et le monitoring
```

Pour repartir avec un budget d'erreur vierge, recréez l'équipe sous un autre nom : l'historique de Prometheus est partagé et garde les séries de l'ancien namespace.
