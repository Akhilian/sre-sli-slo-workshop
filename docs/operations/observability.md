# Observabilité et parcours de démonstration

## SLO et dashboards

### Écrire un SLO (équipes)

Les SLO sont des ressources Sloth (`PrometheusServiceLevel`). Le contrôleur Sloth du namespace `monitoring` les transforme en règles Prometheus : enregistrement des SLI sur plusieurs fenêtres et alertes multi-fenêtres (page 1 h + 5 min à un burn rate de 14,4, page 6 h + 30 min à 6, ticket 1 j + 2 h à 3, ticket 3 j + 6 h à 1).

| Fichier | État |
| --- | --- |
| `observability/sloth/upload-availability.yaml` | complet, installé dans chaque équipe par `deploy/scripts/setup.sh` : c'est l'exemple de référence |
| `observability/sloth/upload-latency.yaml` | squelette à compléter |
| `observability/sloth/processing-freshness.yaml` | squelette à compléter |
| `observability/sloth/search-quality.yaml` | squelette à compléter |
| `observability/sloth/notification-coverage.yaml` | squelette à compléter |

Chaque squelette rappelle les métriques disponibles. Les requêtes s'écrivent **sans filtre de namespace** : Prometheus ajoute lui-même `namespace="team-<nom>"` à chaque règle d'une équipe, qui ne voit donc que ses propres métriques.

```bash
export KUBECONFIG=out/kubeconfigs/a.yaml
kubectl apply -f observability/sloth/search-quality.yaml
kubectl get prometheusservicelevels     # GEN OK = true : les règles sont générées
```

| Symptôme | Cause |
| --- | --- |
| `kubectl apply` refusé : `objective ... must be of type number` | l'objectif est encore `TODO` |
| `GEN OK` à `false` | une requête est invalide ou encore `TODO` ; l'animateur lit la cause avec `kubectl logs -n monitoring deploy/sloth` |
| Burn rate absent au lieu de 0 | la requête d'erreurs ne renvoie rien tant qu'aucune erreur n'a eu lieu : ajouter `or vector(0)` (voir le SLO d'upload) |

Solutions pour l'animateur : `observability/sloth/solutions/` (`kubectl apply -n team-a -f observability/sloth/solutions/`).

### Grafana

Accès anonyme en lecture, à l'adresse affichée par `setup.sh` (port 3000).

- **DocShare · Démarrage** : page d'accueil de Grafana. Navigation pour débutants (dashboards, *Drilldown › Metrics*, Explore), catalogue des métriques avec un lien ▶ vers l'Explore prérempli pour chacune, et PromQL en 4 étapes sur l'exemple du SLI d'upload.
- **DocShare · Parcours** : métriques brutes de chaque parcours pour l'équipe choisie : débits par statut, file d'attente, et les histogrammes en heatmaps. Aucun ratio de SLI : ce serait la solution de la séquence « SLI mesurable ».
- **DocShare · Burn rate et budget** : pour un SLO de l'équipe, burn rate sur 5 min, 30 min et 1 h avec les seuils 6 et 14,4, SLI et objectif, budget restant sur 30 jours, temps avant épuisement, alertes actives.
- **Explore** : ouvert aux visiteurs pour écrire des requêtes PromQL (séquence « SLI mesurable »). Les dashboards ne peuvent pas être enregistrés.

Le budget restant suppose que **la période non observée est parfaite** : il intègre le taux d'erreur sur la plage affichée (3 h par défaut) et le rapporte au budget de 30 jours. On n'utilise pas `slo:period_error_budget_remaining:ratio` de Sloth, qui ferait la moyenne sur le seul historique disponible et compterait 30 min de panne comme un quart du mois.

Avec un historique de quelques heures, les fenêtres longues réagissent fort : après une grosse panne, l'alerte page 6 h + 30 min peut sonner encore une vingtaine de minutes après la coupure. Attendez que les burn rates repassent sous 1 avant la panne suivante.

La page d'accueil est une préférence de l'organisation Grafana, posée par `setup.sh` et conservée dans la base de Grafana (volume persistant de 1 Gi). Si l'accueil redevient la page standard (volume recréé, par exemple), pour la remettre sans relancer les équipes :

```bash
kubectl exec -i -n monitoring deploy/kps-grafana -c grafana-sc-dashboard -- python - < deploy/monitoring/grafana-home.py
```

Les dashboards sont produits par `observability/grafana/generate.py` (modifier le script, puis `python3 observability/grafana/generate.py observability/grafana` et relancer `deploy/scripts/setup.sh`).

## Utiliser l'API

| Endpoint | Rôle |
| --- | --- |
| `POST /documents` | upload d'un fichier en `multipart/form-data` (champ `file`, titre optionnel `title`, par défaut le nom du fichier), répond 202 avec l'`id` ; 422 si le fichier manque ou est vide, 413 au-delà de 5 Mio (`MAX_UPLOAD_BYTES`) |
| `GET /documents/{id}` | statut (`pending` / `done`) et métadonnées (titre, nom, type et taille du fichier), 404 si inconnu |
| `GET /documents/{id}/file` | téléchargement du fichier d'origine, 404 si inconnu |
| `GET /search?q=` | recherche plein texte, 20 résultats au plus |
| `GET /admin/faults` | pannes actives |
| `POST /admin/faults` | active ou coupe une panne |
| `GET /healthz` | sonde, insensible aux pannes |
| `GET /metrics` | métriques Prometheus de l'API |

```bash
# Upload d'un fichier
echo "facture électricité doc-abc12345" > facture.txt
curl -s -F file=@facture.txt localhost:8000/documents
# {"id":1}
curl -s -F file=@photo.png -F title="Photo du chantier" localhost:8000/documents

# Statut : pending, puis done après 1 à 3 s
curl -s localhost:8000/documents/1

# Recherche : le document n'est trouvé qu'une fois traité par le worker
curl -s 'localhost:8000/search?q=doc-abc12345'

# Téléchargement
curl -s -OJ localhost:8000/documents/1/file
```

Le worker simule un OCR : il lit le texte des fichiers texte (`text/*`, `.txt`, `.md`, `.csv`, `.json`), qui deviennent recherchables par leur contenu. Les autres fichiers (PDF, images...) ne sont recherchables que par leur titre.

Si Postgres ne répond pas pendant une recherche, l'API renvoie quand même 200 avec une liste vide et incrémente `search_fallback_total`. C'est volontaire : un 200 n'est pas forcément un succès.

## Métriques

| Rôle | URL | Métriques |
| --- | --- | --- |
| api | `localhost:8000/metrics` | `http_requests_total{route,status}`, `http_request_duration_seconds{route}`, `search_requests_total{status}`, `search_results_count`, `search_fallback_total` |
| worker | `localhost:9100/metrics` | `jobs_processed_total{status}`, `queue_depth`, `document_processing_delay_seconds`, `notifications_enqueued_total` |
| notifier | `localhost:9101/metrics` | `notifications_sent_total{status}`, `notification_delay_seconds` |

Buckets des histogrammes, alignés sur les seuils de l'exercice :

| Histogramme | Buckets |
| --- | --- |
| `http_request_duration_seconds` | 0.1, 0.3, 1, 3 s |
| `document_processing_delay_seconds` | 10, 60, 300, 900 s |
| `search_results_count` | 0, 1, 5, 20 |
| `notification_delay_seconds` | 1, 5, 30, 120 s |

Points d'attention pour écrire les requêtes PromQL :
- Les bornes sont écrites au format flottant : `le="0.0"`, `le="0.3"`, `le="1.0"`, `le="60.0"`. Une requête sur `le="0"` ou `le="60"` ne renvoie rien.
- Le label `route` contient le modèle de route (`/documents/{id}`), jamais l'identifiant réel.
- `/metrics`, `/healthz`, `/admin/faults` et les URL inconnues ne sont pas mesurés.
- Il n'y a volontairement ni métrique côté client, ni métrique de diagnostic supplémentaire : leur absence fait partie de l'exercice.

## Pannes

Les pannes sont stockées dans le hash Redis `faults` (en mémoire en mode standalone) et relues à chaque requête ou job : elles s'appliquent immédiatement, sans redémarrage. Leur code est dans `app/adapters/faults.py`.

```bash
# Activer
curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' \
  -d '{"name": "worker_slow", "value": 10}'
# Couper (valeur 0)
curl -s -X POST localhost:8000/admin/faults -H 'content-type: application/json' \
  -d '{"name": "worker_slow", "value": 0}'
# Lister les pannes actives
curl -s localhost:8000/admin/faults
```

| Panne | Valeur | Effet | SLI dégradé | SLI intacts |
| --- | --- | --- | --- | --- |
| `upload_latency` | secondes, ex. `2.0` | délai ajouté à chaque upload | latence | disponibilité, fraîcheur, qualité, couverture |
| `upload_error_rate` | proportion, `0.02` puis `0.5` | uploads en 500, avant toute écriture (aucun document fantôme) | disponibilité | latence, fraîcheur, qualité, couverture |
| `worker_slow` | facteur, ex. `10` | traitement 10 fois plus lent, la file s'engorge | fraîcheur | disponibilité, latence, qualité |
| `stale_index` | `1` | documents marqués `done` sans être indexés : recherche en 200 avec 0 résultat | qualité | disponibilité, latence, fraîcheur |
| `notifier_drop` | proportion, ex. `0.2` | notifications perdues sans erreur, sans log, sans compteur | couverture | disponibilité, latence, fraîcheur, qualité |

Effets mesurés en local :

| Panne | Mesure |
| --- | --- |
| `upload_latency=2.0` | upload en 2,01 s ; `/healthz` en 2 ms |
| `upload_error_rate=0.5` | 93 erreurs sur 200 uploads, aucun document créé pour ces requêtes |
| `worker_slow=10` à 1 upload/s | uploads toujours en 202 ; au bout de 2 min, file à 92 jobs et premiers documents traités en plus de 60 s |
| `stale_index=1` | document `done` mais introuvable ; de nouveau trouvable après la coupure |
| `notifier_drop=0.2` | 18,7 % de notifications perdues sur 300, aucune ligne de log |

Effets mesurés sur le k3s local avec le trafic k6, panne dans `team-a` seulement (`team-b` reste nominale à chaque fois) :

| Panne | Mesure |
| --- | --- |
| `worker_slow=10` | uploads maintenus à 60/min ; file à 138 jobs après 4 min ; 83 % des documents traités en plus de 60 s ; 0 % de recherches vides |
| `stale_index=1` | 100 % de recherches vides, toutes en 200 ; aucun upload en erreur ; fraîcheur intacte |
| `upload_latency=2` | débit d'upload maintenu à 1/s ; 100 % des uploads au-delà de 1 s ; qualité intacte |

Burn rate sur 5 min de chaque SLO (solutions de `observability/sloth/solutions/`), mesuré sur le k3s local après 2 min 30 de panne, deux pannes différentes en parallèle dans `team-a` et `team-b`. Chaque panne ne fait monter qu'un SLO, et seulement dans son équipe :

| Panne | Disponibilité | Latence | Fraîcheur | Qualité | Couverture |
| --- | --- | --- | --- | --- | --- |
| `upload_error_rate=0.5` | **44,7** | 0 | 0 | 0 | 0 |
| `upload_latency=2` | 0 | **45,1** | 0 | 0 | 0,7 (bruit) |
| `worker_slow=10` | 0 | 0 | **1,4** | 0 | 0 |
| `stale_index=1` | 0 | 0 | 0 | **45,0** | 0 |
| `notifier_drop=0.2` | 0 | 0 | 0 | 0 | **21,7** |

La fraîcheur réagit lentement : un document n'est compté en retard qu'une fois traité, plus de 60 s après son upload. Comptez environ 5 min de `worker_slow` pour un effet net (83 % des documents en retard après 4 min).

Une panne à la fois. Après `worker_slow`, la file met du temps à se vider (environ 1 min pour 100 jobs en attente). Attendez que `queue_depth` revienne à 0 avant la panne suivante, sinon le retard hérité fausse ce qu'elle montre.

### Temps de réaction mesurés (k3s local)

Panne activée dans une équipe, trafic k6 nominal, une panne à la fois ; l'autre équipe porte une autre panne. Temps comptés depuis l'activation, échantillonnés toutes les 15 s.

| Panne | Burn rate 5 min > 1 | > 6 | Alerte ticket | Alerte page |
| --- | --- | --- | --- | --- |
| `upload_error_rate=0.5` | 15 s | 30 s | — | 105 s |
| `upload_latency=2` | 15 s | 30 s | 45 s | 75 s |
| `stale_index=1` | 15 s | 30 s | 15 s | 90 s |
| `notifier_drop=0.2` | 45 s | 90 s | 90 s | pas de page en 3 min |
| `worker_slow=10` | 135 s | pas atteint en 4 min (≈ 4,6, file à 181 jobs) | aucune en 4 min | aucune en 4 min |

À lire avec prudence :
- Les alertes se déclenchent bien plus vite que les « 9 min » du calibrage théorique : l'historique des essais ne dépassait pas 25 min, les fenêtres de 1 h et de 6 h se comportent alors comme des fenêtres courtes. Avec 1 h de trafic sain, comptez plutôt plusieurs minutes pour la page de `upload_error_rate=0.5`.
- `upload_error_rate=0.02` (burn rate attendu ≈ 4) n'a été tenu que 8 min en réel ; la preuve complète est faite par rejeu (ci-dessous).
- Les pannes ont été enchaînées avec 30 s de pause : les alertes longues d'une panne précédente restent actives (`DocshareUploadLatency`, `DocshareSearchQuality`). Laissez les burn rates repasser sous 1 avant la panne suivante.
- Aucune panne n'a fait monter un SLI d'une autre famille de plus de 1,4 dans l'équipe voisine, hors résidus d'une panne précédente.

### Preuve rapide par rejeu des règles (`promtool test rules`)

Les règles générées par Sloth (`PrometheusRule` de `docshare-upload-availability`) sont rejouées sur des séries synthétiques (1 upload/s, pas de 30 s), en quelques secondes :
- 3 jours de trafic sain puis `0.02` pendant 25 min : burn rate 5 min = 4,0 à +10 min et +25 min, **aucune alerte**.
- 1 h de trafic sain puis `0.5` : la **page** (`severity=page`) est active 5 min après le début de la panne (< 10 min).
- Avec seulement 1 h 25 d'historique, le ticket 3j/6h (burn 1) s'allume à 4 : artefact d'historique court, absent avec 3 jours d'historique sain.
