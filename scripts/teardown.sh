#!/usr/bin/env bash
# Supprime des équipes, ou tout ce que DocShare a installé.
#
#   scripts/teardown.sh <équipe> [<équipe> ...]
#   scripts/teardown.sh --all
#
# Pour repartir avec un budget vierge, recréez l'équipe sous un autre nom :
# l'historique de Prometheus est partagé et garde les séries de l'ancien namespace.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
[[ $# -ge 1 ]] || { echo "usage : $0 <équipe> [...] | --all" >&2; exit 1; }

CONTEXT=${KUBE_CONTEXT:-$(kubectl config current-context)}
k() { kubectl --context "$CONTEXT" "$@"; }

# Compatible avec le bash 3.2 de macOS : ni mapfile, ni tableau vide sous set -u.
namespaces=()
if [[ $1 == --all ]]; then
  while read -r ns; do namespaces+=("$ns"); done < <(k get namespaces -l docshare.workshop/team -o name)
else
  for team in "$@"; do namespaces+=("namespace/team-$team"); done
fi

echo "Contexte : $CONTEXT"
echo "À supprimer : ${namespaces[*]+${namespaces[*]}}$([[ $1 == --all ]] && echo ' + monitoring')"
read -r -p "Confirmer ? [o/N] " answer
[[ $answer == [oOyY] ]] || exit 1

for ns in ${namespaces[@]+"${namespaces[@]}"}; do
  k delete "$ns" --wait=false
  rm -f "$ROOT/out/kubeconfigs/${ns#namespace/team-}.yaml"
done

if [[ $1 == --all ]]; then
  helm --kube-context "$CONTEXT" uninstall kps --namespace monitoring --ignore-not-found
  k delete namespace monitoring --ignore-not-found --wait=false
  echo "Les CRD de Prometheus Operator (monitoring.coreos.com) sont conservées."
fi
