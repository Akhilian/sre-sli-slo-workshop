## ADDED Requirements

### Requirement: Chart indépendant du fournisseur
Le chart et la configuration du monitoring SHALL fonctionner sur EKS et un k3s local (colima). Les différences MUST être limitées aux fichiers `deploy/environments/<cible>/monitoring.yaml` et `deploy/environments/<cible>/docshare.yaml` (cibles `local`, `eks`).

#### Scenario: Même chart, deux cibles
- **WHEN** `deploy/scripts/setup.sh` est lancé sur chacune des deux cibles avec son fichier de valeurs
- **THEN** l'installation réussit sans modification des templates

### Requirement: Stockage par défaut du cluster
Les PVC SHALL utiliser la classe de stockage par défaut du cluster, sans `storageClassName` codé en dur.

#### Scenario: EKS avec EBS CSI
- **WHEN** le chart est installé sur EKS avec l'add-on EBS CSI
- **THEN** les PVC de Postgres, Redis et Prometheus sont liés

#### Scenario: Prérequis manquant détecté
- **WHEN** `deploy/scripts/setup.sh eks` est lancé sur un cluster sans classe de stockage par défaut
- **THEN** le script s'arrête avant l'installation avec un message qui nomme le prérequis

### Requirement: Ingress optionnel
Le chart SHALL permettre d'activer un Ingress par équipe avec un `ingressClassName` configurable, désactivé par défaut. Le parcours nominal MUST fonctionner sans Ingress.

#### Scenario: Cluster sans contrôleur d'Ingress
- **WHEN** le chart est installé avec les valeurs par défaut sur un cluster sans contrôleur d'Ingress
- **THEN** les équipes accèdent à leur API par `port-forward`

### Requirement: Dimensionnement documenté
Le projet SHALL documenter les ressources demandées pour 4 équipes (environ 4 vCPU et 7 Gi) et la taille de cluster recommandée par cible, et MUST donner la commande `colima` qui crée un k3s local capable d'héberger 4 équipes.

#### Scenario: 4 équipes sur le cluster recommandé
- **WHEN** 4 équipes sont installées sur 3 nœuds `e2-standard-4`
- **THEN** aucun pod ne reste en `Pending` et aucun quota n'est dépassé sous le trafic k6
