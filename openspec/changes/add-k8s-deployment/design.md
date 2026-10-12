## Context

L'application (change `add-docshare-app`) existe sous forme d'image publiée. Il faut la déployer pour 1 à 4 équipes sur un cluster partagé dont le fournisseur varie selon les sessions : GKE le plus souvent, parfois EKS, k3d pour le développement et les répétitions. L'animateur prépare le cluster ; les participants n'ont que `kubectl` et un kubeconfig.

## Goals / Non-Goals

**Goals:**
- Une commande pour installer monitoring + N équipes, idempotente.
- Isolation stricte entre équipes (pannes, données, droits), monitoring commun.
- Même chart sur les trois cibles.

**Non-Goals:**
- Création des clusters (pas de Terraform ; commandes `gcloud`, `eksctl`, `k3d` documentées).
- Haute disponibilité de Redis, Postgres ou Prometheus.
- Sloth, SLO et dashboards (change `add-slo-and-dashboards`), k6 (change `add-traffic-and-runbook`).
- Authentification fine de Grafana (lecture anonyme suffit).

## Decisions

**Helm plutôt que Kustomize.** Une release par équipe, paramétrée par le nom d'équipe et la cible ; `helm upgrade --install` rend le script idempotent sans effort.
Alternative écartée : Kustomize avec un overlay par équipe. Duplication à chaque session et pas de notion de release.

**Redis et Postgres en StatefulSets maison.** Images officielles, une réplique, PVC, quelques lignes de template.
Alternative écartée : charts Bitnami. Dépendance lourde, conditions de distribution des images devenues incertaines, beaucoup de configuration pour un besoin trivial.

**kube-prometheus-stack.** Fournit Prometheus Operator (nécessaire aux CRD `PodMonitor` / `PrometheusRule` et au contrôleur Sloth du change suivant), Grafana avec sidecar de dashboards, kube-state-metrics et node-exporter (métriques CPU / mémoire qui servent de pièges). Valeurs clés : `podMonitorSelectorNilUsesHelmValues: false`, `ruleSelectorNilUsesHelmValues: false`, sélecteurs de namespaces vides, `scrapeInterval: 5s`, `evaluationInterval: 15s`, `alertmanager.enabled: false`, rétention 2 j, PVC 10 Gi.

**`PodMonitor` dans le chart d'équipe.** Chaque équipe apporte sa propre collecte ; le label `namespace` est ajouté automatiquement par l'opérateur.
Alternative écartée : un seul `PodMonitor` dans `monitoring` avec `namespaceSelector: any`. Fonctionne, mais une équipe supprimée laisse moins de traces si sa collecte vit dans son namespace.

**Droits.** RoleBinding vers le ClusterRole `edit` dans le namespace de l'équipe. Kubeconfig généré par `kubectl create token <sa> --duration=8h` et l'adresse du serveur API extraite du contexte courant de l'animateur. Fonctionne à l'identique sur les trois cibles.
Alternative écartée : identités cloud (IAM GKE / EKS). Imposerait des comptes cloud aux participants.

**Accès à Grafana par LoadBalancer.** Les équipes n'ont aucun droit dans `monitoring`, donc pas de `port-forward` possible. Le Service `LoadBalancer` est supporté nativement sur GKE, EKS et k3s (servicelb) ; `loadBalancerSourceRanges` limite l'accès à l'IP de la salle.
Alternative écartée : Ingress pour Grafana. Contrôleur différent par cible, et souvent absent sur un cluster neuf.

**Quotas.** Calés sur la pile d'une équipe (~0.6 vCPU, ~1 Gi de requêtes, Job k6 compris) avec 50 % de marge. Requêtes et limites définies sur chaque conteneur du chart.

**Script de setup.** Bash + `kubectl` + `helm`, vérifications préalables (outils présents, contexte courant affiché, classe de stockage par défaut existante, confirmation si le contexte n'est pas k3d).

## Risks / Trade-offs

- [Kubeconfig à jeton : expiration à 8 h] → suffisant pour une séance ; le script peut les régénérer.
- [Grafana exposé sur internet] → `loadBalancerSourceRanges` obligatoire hors local ; le script refuse de continuer si la valeur est vide sur GKE / EKS.
- [EKS : add-on EBS CSI absent] → détection de l'absence de classe de stockage par défaut avant l'installation.
- [GKE Autopilot] → non supporté (node-exporter refusé) ; documenté et vérifié par le script si possible.
- [Prometheus partagé : un namespace supprimé garde son historique] → recréer une équipe sous un nouveau nom pour un budget vierge.
- [Version de kube-prometheus-stack] → version du chart figée dans le script.

## Migration Plan

Premier déploiement, pas de migration. Retour arrière : `scripts/teardown.sh --all`.

## Open Questions

- Plage d'IP de la salle à renseigner à chaque session : fournie par l'animateur, ou ouverture large assumée pour les répétitions ?
