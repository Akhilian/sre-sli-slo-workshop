#!/usr/bin/env bash
# Installe le monitoring partagé (si absent) puis une pile DocShare par équipe.
#
#   scripts/setup.sh [-y] <local|gke|eks> <équipe> [<équipe> ...]
#
# Variables :
#   KUBE_CONTEXT           contexte kubectl à utiliser (défaut : contexte courant)
#   GRAFANA_SOURCE_RANGES  plages autorisées vers Grafana, séparées par des virgules
#                          (obligatoire pour gke et eks, ex. 203.0.113.10/32)
#   TOKEN_DURATION         durée de validité des kubeconfigs d'équipe (défaut : 8h)
set -euo pipefail

KPS_VERSION=92.3.0
ROOT=$(cd "$(dirname "$0")/.." && pwd)

usage() { echo "usage : $0 [-y] <local|gke|eks> <équipe> [<équipe> ...]" >&2; exit 1; }
fail() { echo "erreur : $*" >&2; exit 1; }

YES=false
if [[ ${1:-} == -y ]]; then YES=true; shift; fi
[[ $# -ge 2 ]] || usage
TARGET=$1; shift
TEAMS=("$@")
[[ -d $ROOT/values/$TARGET ]] || fail "cible inconnue : $TARGET (local, gke ou eks)"

for tool in kubectl helm; do
  command -v "$tool" >/dev/null || fail "$tool est introuvable"
done

CONTEXT=${KUBE_CONTEXT:-$(kubectl config current-context)}
k() { kubectl --context "$CONTEXT" "$@"; }
h() { helm --kube-context "$CONTEXT" "$@"; }

for team in "${TEAMS[@]}"; do
  [[ $team =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] || fail "nom d'équipe invalide : $team (minuscules, chiffres, tirets)"
done

# --- Vérifications préalables ------------------------------------------------

echo "Contexte : $CONTEXT"
echo "Cible    : $TARGET"
echo "Équipes  : ${TEAMS[*]}"
if [[ $TARGET != local || $CONTEXT != colima ]] && ! $YES; then
  read -r -p "Installer sur ce cluster ? [o/N] " answer
  [[ $answer == [oOyY] ]] || exit 1
fi

if ! k get storageclass -o jsonpath='{.items[*].metadata.annotations.storageclass\.kubernetes\.io/is-default-class}' | grep -q true; then
  fail "aucune classe de stockage par défaut. Sur EKS, installez l'add-on EBS CSI et marquez gp3 par défaut."
fi

SOURCE_RANGES=()
if [[ $TARGET != local ]]; then
  [[ -n ${GRAFANA_SOURCE_RANGES:-} ]] || fail "GRAFANA_SOURCE_RANGES est obligatoire pour $TARGET : Grafana serait ouvert à tout internet."
  SOURCE_RANGES=(--set "grafana.service.loadBalancerSourceRanges={$GRAFANA_SOURCE_RANGES}")
fi

if [[ $TARGET != local ]] && grep -q OWNER "$ROOT/values/$TARGET/docshare.yaml"; then
  fail "renseignez le compte ghcr.io de l'image dans values/$TARGET/docshare.yaml"
fi

# --- Monitoring partagé ------------------------------------------------------

echo "==> Monitoring (kube-prometheus-stack $KPS_VERSION)"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update >/dev/null
h upgrade --install kps prometheus-community/kube-prometheus-stack \
  --version "$KPS_VERSION" \
  --namespace monitoring --create-namespace \
  -f "$ROOT/monitoring/values.yaml" \
  -f "$ROOT/values/$TARGET/monitoring.yaml" \
  ${SOURCE_RANGES[@]+"${SOURCE_RANGES[@]}"} \
  --wait --timeout 10m >/dev/null

# --- Équipes -----------------------------------------------------------------

SERVER=$(k config view --minify --raw -o jsonpath="{.clusters[0].cluster.server}")
CA_DATA=$(k config view --minify --raw -o jsonpath="{.clusters[0].cluster.certificate-authority-data}")
mkdir -p "$ROOT/out/kubeconfigs"

for team in "${TEAMS[@]}"; do
  ns=team-$team
  echo "==> Équipe $team (namespace $ns)"
  k create namespace "$ns" --dry-run=client -o yaml | k apply -f - >/dev/null
  k label namespace "$ns" docshare.workshop/team="$team" --overwrite >/dev/null
  h upgrade --install docshare "$ROOT/charts/docshare" \
    --namespace "$ns" \
    -f "$ROOT/values/$TARGET/docshare.yaml" \
    --set team="$team" \
    --wait --timeout 5m >/dev/null

  token=$(k create token team --namespace "$ns" --duration "${TOKEN_DURATION:-8h}")
  kubeconfig=$ROOT/out/kubeconfigs/$team.yaml
  cat > "$kubeconfig" <<KUBECONFIG
apiVersion: v1
kind: Config
clusters:
  - name: docshare
    cluster:
      server: $SERVER
      certificate-authority-data: $CA_DATA
users:
  - name: $team
    user:
      token: $token
contexts:
  - name: $team
    context:
      cluster: docshare
      user: $team
      namespace: $ns
current-context: $team
KUBECONFIG
  chmod 600 "$kubeconfig"
  echo "    kubeconfig : out/kubeconfigs/$team.yaml"
done

# --- Accès -------------------------------------------------------------------

grafana=$(k get service kps-grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}{.status.loadBalancer.ingress[0].hostname}')
echo
echo "Grafana : http://${grafana:-<adresse en attente, relancer : kubectl get svc kps-grafana -n monitoring>}:3000"
echo "API d'une équipe : KUBECONFIG=out/kubeconfigs/<équipe>.yaml kubectl port-forward svc/api 8000:80"
