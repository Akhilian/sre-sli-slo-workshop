# Déroulé de la séance (2 h)

Guide de l'animateur : préparation, enchaînement des cinq séquences, pannes en direct, remise à zéro. Les détails techniques sont dans [Déploiement et exécution](deployment.md) et [Observabilité](observability.md) (fiches de pannes).

## Avant la séance

| Quand | Action |
| --- | --- |
| La veille ou le matin | Créer le cluster (`deployment.md`, « Prérequis »), vérifier que les images `akhilian/docshare` et `akhilian/docshare-web` sont publiées sur Docker Hub. |
| Au moins 15 min avant | `deploy/scripts/setup.sh <cible> a b c d` (`GRAFANA_SOURCE_RANGES=<IP de la salle>/32` sur EKS). Les fenêtres d'une heure des alertes ont besoin d'un historique sain. |
| Avant l'arrivée des équipes | Vérifier `kubectl get pods -A`, ouvrir Grafana (la page d'accueil doit être **DocShare · Démarrage**), distribuer `out/kubeconfigs/<équipe>.yaml`, tester `port-forward svc/web` d'une équipe. |

Côté participants : `kubectl` installé, un kubeconfig, un navigateur.

## Enchaînement

| Durée | Séquence | Ce que font les équipes | Ce que fait l'animateur |
| --- | --- | --- | --- |
| 10 min | Mise en situation | `kubectl port-forward svc/web 8080:80`, dépôt de fichiers et recherche dans l'interface | Présente DocShare et le parcours utilisateur |
| 25 min | SLI fonctionnel | Listent ce qui compte pour un utilisateur (déposer, retrouver, être notifié) | Guide vers un SLI par parcours |
| 25 min | SLI mesurable | Partent de la page d'accueil de Grafana (catalogue des métriques), puis écrivent leurs requêtes PromQL dans l'Explore | Fait la démo de prise en main (5 min, ci-dessous), puis aide sur les buckets (`le="1.0"`) |
| 25 min | SLO, budget, burn rate | Complètent un fichier `observability/sloth/*.yaml` et l'appliquent | Lit `kubectl logs -n monitoring deploy/sloth` en cas d'erreur |
| 25 min | Pannes en direct | Observent l'interface et le dashboard burn rate | Active une panne à la fois (voir plus bas) |
| 10 min | Débrief | Comparent ce qu'a vu l'utilisateur et ce qu'ont vu les SLI | Montre les angles morts (`stale_index`, `notifier_drop`) |

## Prise en main de Grafana (5 min)

Au début de « SLI mesurable », à l'écran partagé, sans supposer que les participants connaissent Grafana ni PromQL. Grafana s'ouvre sur **DocShare · Démarrage**, qui reprend ces étapes pour ceux qui décrochent.

1. **Choisir son équipe** dans la liste *Équipe* en haut à gauche : tous les liens de la page suivent.
2. **Parcourir** : menu ☰ → *Drilldown* → *Metrics*, filtre `namespace = team-a`, recherche `http_`. Montrer qu'une métrique a des labels (`route`, `status`).
3. **Interroger** : dans le catalogue de la page d'accueil, cliquer ▶ sur `http_requests_total`. L'Explore s'ouvre sur la requête ; montrer le bouton *Builder* / *Code* et **Shift + Entrée**.
4. **Dérouler les 4 étapes PromQL** de la page d'accueil sur le SLI d'upload déjà fourni : filtrer, `rate`, `sum by`, diviser. C'est le modèle à reproduire pour les autres parcours.
5. **Laisser chercher** : les histogrammes (`_bucket`, `_count`) sont expliqués sous le catalogue ; le dashboard *Parcours* montre les distributions brutes, jamais les ratios.

Le dashboard *Parcours* ne contient volontairement aucun SLI : construire le ratio « bons événements / tous les événements » est l'exercice.

## Pannes en direct

Une seule panne à la fois par équipe, coupée avant la suivante. Chaque équipe peut avoir une panne différente : une panne ne touche que l'équipe où elle est activée.

Ordre conseillé :

1. `upload_error_rate=0.02` : une petite fuite se voit sur le burn rate et ne réveille personne ; à laisser en route pendant l'explication.
2. `upload_error_rate=0.5` : l'alerte page sonne.
3. `upload_latency=2` : l'utilisateur attend, rien n'échoue.
4. `worker_slow=10` : l'upload répond, les documents restent « Bloqué en traitement » dans l'interface.
5. `stale_index=1` : `done`, mais « Aucun résultat » : un SLI de disponibilité reste vert.
6. `notifier_drop=0.2` : rien de visible côté interface ; seul le SLI de couverture le montre.

Activation depuis le pupitre (`http://localhost:8080/?admin`) ou par `curl` sur `localhost:8000/admin/faults` après `port-forward svc/api 8000:80` (voir les fiches).

## Remise à zéro

```bash
# Couper toutes les pannes d'une équipe
for f in upload_latency upload_error_rate worker_slow stale_index notifier_drop; do
  curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' -d "{\"name\": \"$f\", \"value\": 0}"
done
curl -s localhost:8000/admin/faults     # doit répondre {}

# Attendre que la file soit vide après worker_slow
kubectl -n team-a exec sts/redis -- redis-cli llen jobs

# Relancer le trafic k6 pour 3 h (remplace le Job)
deploy/scripts/setup.sh <cible> a
```

Pour repartir avec un budget d'erreur vierge entre deux séances, recréez les équipes sous d'autres noms (`teardown.sh a b c d`, puis `setup.sh <cible> e f g h`) : l'historique de Prometheus garde les séries des anciens namespaces. Après la séance, `deploy/scripts/teardown.sh --all` supprime tout.
