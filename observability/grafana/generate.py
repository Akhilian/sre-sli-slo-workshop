# Génère les dashboards JSON de ce dossier : python3 observability/grafana/generate.py observability/grafana
# Modifier ce script plutôt que les JSON, pour garder les requêtes cohérentes entre panneaux.
import json, sys
from urllib.parse import quote
OUT = sys.argv[1]
DS = {"type": "prometheus", "uid": "prometheus"}
NS = 'namespace="$namespace"'

def target(expr, legend="", instant=False, fmt=None, ref="A"):
    t = {"datasource": DS, "expr": expr, "legendFormat": legend, "refId": ref}
    if instant: t.update(instant=True, range=False)
    if fmt: t["format"] = fmt
    return t

def ts(title, targets, x, y, w=12, h=8, unit="short", desc="", minv=None, maxv=None, thresholds=None):
    d = {"unit": unit, "custom": {"lineWidth": 2, "fillOpacity": 5}}
    if minv is not None: d["min"] = minv
    if maxv is not None: d["max"] = maxv
    if thresholds:
        d["thresholds"] = {"mode": "absolute", "steps": [{"color": "green", "value": None}] + thresholds}
        d["custom"]["thresholdsStyle"] = {"mode": "line+area"}
    return {"type": "timeseries", "title": title, "description": desc, "datasource": DS,
            "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": targets,
            "fieldConfig": {"defaults": d, "overrides": []},
            "options": {"legend": {"displayMode": "list", "placement": "bottom"}, "tooltip": {"mode": "multi"}}}

def heatmap(title, expr, x, y, w=12, h=8, unit="short", desc=""):
    """Histogramme Prometheus brut : un compte par tranche, sans seuil ni ratio."""
    t = target(expr, "{{le}}", fmt="heatmap")
    return {"type": "heatmap", "title": title, "description": desc, "datasource": DS,
            "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": [t],
            "fieldConfig": {"defaults": {}, "overrides": []},
            "options": {"calculate": False, "cellGap": 1, "yAxis": {"unit": unit},
                        "color": {"mode": "scheme", "scheme": "Oranges", "steps": 64},
                        "rowsFrame": {"layout": "auto"}, "tooltip": {"mode": "single", "yHistogram": True},
                        "legend": {"show": True}}}

def stat(title, expr, x, y, w=6, h=5, unit="short", desc="", decimals=None, no_value="", steps=None):
    d = {"unit": unit, "noValue": no_value}
    if decimals is not None: d["decimals"] = decimals
    if steps: d["thresholds"] = {"mode": "absolute", "steps": steps}
    return {"type": "stat", "title": title, "description": desc, "datasource": DS,
            "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": [target(expr, instant=True)],
            "fieldConfig": {"defaults": d, "overrides": []},
            "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value", "graphMode": "none"}}

def row(title, y):
    return {"type": "row", "title": title, "collapsed": False, "gridPos": {"x": 0, "y": y, "w": 24, "h": 1}, "panels": []}

def text(title, content, x, y, w, h):
    return {"type": "text", "title": title, "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "options": {"mode": "markdown", "content": content}}

def var_namespace():
    return {"name": "namespace", "label": "Équipe", "type": "query", "datasource": DS,
            "query": {"query": 'label_values(http_requests_total, namespace)', "refId": "ns"},
            "definition": 'label_values(http_requests_total, namespace)', "refresh": 2, "sort": 1}

def dashboard(uid, title, panels, variables, desc):
    for i, p in enumerate(panels): p["id"] = i + 1
    return {"uid": uid, "title": title, "description": desc, "tags": ["docshare"], "timezone": "browser",
            "schemaVersion": 39, "editable": False, "refresh": "10s",
            "time": {"from": "now-3h", "to": "now"},
            "templating": {"list": variables}, "panels": panels}

# --- Vue par parcours -------------------------------------------------------------
def r(m, w="1m"): return f"rate({m}[{w}])"
UP = f'route="/documents",{NS}'
p = []
y = 0
p.append(row("Upload", y)); y += 1
p.append(ts("Uploads par statut HTTP", [target(f'sum by (status) ({r(f"http_requests_total{{{UP}}}")})', "{{status}}")], 0, y, unit="reqps"))
p.append(heatmap("Durée des uploads", f'sum by (le) ({r(f"http_request_duration_seconds_bucket{{{UP}}}")})', 12, y, unit="s",
                 desc="Nombre d'uploads par tranche de durée (bornes 0,1 / 0,3 / 1 / 3 s).")); y += 8
p.append(row("Traitement", y)); y += 1
p.append(ts("Jobs en attente", [target(f'max(queue_depth{{{NS}}})', "file")], 0, y, w=8,
            desc="Taille de la file. Une file pleine gêne-t-elle l'utilisateur ? Pas toujours : ce n'est pas un SLI."))
p.append(heatmap("Délai de traitement des documents", f'sum by (le) ({r(f"document_processing_delay_seconds_bucket{{{NS}}}", "2m")})', 8, y, w=8, unit="s",
                 desc="Délai entre l'upload et la fin du traitement, mesuré à la fin du job : un document bloqué n'apparaît qu'une fois traité."))
p.append(ts("Jobs traités par statut", [target(f'sum by (status) ({r(f"jobs_processed_total{{{NS}}}")})', "{{status}}")], 16, y, w=8, unit="ops")); y += 8
p.append(row("Recherche", y)); y += 1
p.append(ts("Recherches par statut", [target(f'sum by (status) ({r(f"search_requests_total{{{NS}}}")})', "{{status}}")], 0, y, w=8, unit="reqps"))
p.append(heatmap("Résultats par recherche", f'sum by (le) ({r(f"search_results_count_bucket{{{NS}}}")})', 8, y, w=8,
                 desc="Nombre de recherches par tranche de nombre de résultats (bornes 0 / 1 / 5 / 20)."))
p.append(ts("Recherches en repli", [target(f'sum({r(f"search_fallback_total{{{NS}}}")}) or vector(0)', "replis")], 16, y, w=8, unit="reqps",
            desc="Erreurs Postgres masquées derrière un 200 avec une liste vide.")); y += 8
p.append(row("Notifications", y)); y += 1
p.append(ts("Notifications demandées et envoyées", [
    target(f'sum({r(f"notifications_enqueued_total{{{NS}}}")})', "demandées (worker)", ref="A"),
    target(f'sum({r(f"notifications_sent_total{{{NS},status=\"ok\"}}")})', "envoyées (notifier)", ref="B"),
], 0, y, unit="ops"))
p.append(heatmap("Délai d'envoi des notifications", f'sum by (le) ({r(f"notification_delay_seconds_bucket{{{NS}}}")})', 12, y, unit="s",
                 desc="Délai entre la demande et l'envoi (bornes 1 / 5 / 30 / 120 s)."))
# Pas de ratio « bons / total » ici : construire les SLI est l'exercice des équipes.
parcours = dashboard("docshare-parcours", "DocShare · Parcours", p, [var_namespace()],
                     "Métriques brutes de chaque parcours, pour l'équipe choisie.")

# --- Burn rate et budget -----------------------------------------------------------
SEL = f'{NS},sloth_id="$slo"'
BUDGET = f'max(slo:error_budget:ratio{{{SEL}}})'
def burn(w): return f'max(slo:sli_error:ratio_rate{w}{{{SEL}}}) / {BUDGET}'
# Fraction du budget de 30 j consommée depuis le début de la plage affichée.
# Chaque échantillon du ratio 5 min est enregistré toutes les 15 s (evaluationInterval) :
# somme × 15 s ≈ intégrale du taux d'erreur sur la période observée. La période non
# observée est supposée parfaite.
CONSUMED = f'(sum(sum_over_time(slo:sli_error:ratio_rate5m{{{SEL}}}[$__range])) * 15) / ({BUDGET} * 30 * 86400)'
REMAINING = f'1 - {CONSUMED}'
b = []
b.append(ts("Burn rate", [target(burn("5m"), "5 min", ref="A"), target(burn("30m"), "30 min", ref="B"), target(burn("1h"), "1 h", ref="C")],
            0, 0, w=16, h=10, minv=0, thresholds=[{"color": "orange", "value": 6}, {"color": "red", "value": 14.4}],
            desc="Vitesse de consommation du budget. 1 = le budget est épuisé en exactement 30 jours. Page si 1 h et 5 min dépassent 14,4, ou si 6 h et 30 min dépassent 6."))
b.append(stat("Burn rate actuel (1 h)", burn("1h"), 16, 0, w=8, h=5, decimals=1,
              steps=[{"color": "green", "value": None}, {"color": "orange", "value": 6}, {"color": "red", "value": 14.4}]))
b.append(stat("SLI sur 1 h", f'1 - max(slo:sli_error:ratio_rate1h{{{SEL}}})', 16, 5, w=4, h=5, unit="percentunit", decimals=2))
b.append(stat("Objectif", f'max(slo:objective:ratio{{{SEL}}})', 20, 5, w=4, h=5, unit="percentunit", decimals=2))
b.append(stat("Budget restant (30 j)", f'clamp_min({REMAINING}, 0)', 0, 10, w=6, h=6, unit="percentunit", decimals=1,
              steps=[{"color": "red", "value": None}, {"color": "orange", "value": 0.25}, {"color": "green", "value": 0.5}],
              desc="Part du budget d'erreur mensuel encore disponible."))
b.append(stat("Temps avant épuisement", f'clamp_min({REMAINING}, 0) * 30 * 86400 / ({burn("1h")} > 0)', 6, 10, w=6, h=6, unit="s",
              no_value="∞ (aucune erreur)", desc="Au rythme du burn rate sur 1 h."))
b.append(text("Hypothèse de calcul",
              "Le budget est calculé sur **30 jours**, mais l'historique ne couvre que la plage affichée (3 h par défaut).\n\n"
              "**La période non observée est supposée parfaite** : seules les erreurs visibles ici entament le budget.\n\n"
              "Ne pas lire `slo:period_error_budget_remaining:ratio` de Sloth : c'est une moyenne sur l'historique disponible, "
              "qui compterait 30 min de panne comme un quart du mois.", 12, 10, 12, 6))
b.append({"type": "table", "title": "Alertes actives de l'équipe", "datasource": DS, "gridPos": {"x": 0, "y": 16, "w": 24, "h": 6},
          "targets": [target(f'ALERTS{{{NS},alertstate="firing"}}', instant=True, fmt="table")],
          "fieldConfig": {"defaults": {"noValue": "Aucune alerte"}, "overrides": []},
          "transformations": [{"id": "organize", "options": {
              "excludeByName": {"Time": True, "Value": True, "__name__": True, "alertstate": True, "namespace": True, "sloth_id": True},
              "renameByName": {"alertname": "Alerte", "severity": "Sévérité", "sloth_service": "Service", "sloth_slo": "SLO"}}}]})
slo_var = {"name": "slo", "label": "SLO", "type": "query", "datasource": DS,
           "query": {"query": 'label_values(slo:objective:ratio{namespace="$namespace"}, sloth_id)', "refId": "slo"},
           "definition": 'label_values(slo:objective:ratio{namespace="$namespace"}, sloth_id)', "refresh": 2, "sort": 1}
ns_var = var_namespace(); ns_var["query"]["query"] = ns_var["definition"] = "label_values(slo:objective:ratio, namespace)"
burnrate = dashboard("docshare-burn-rate", "DocShare · Burn rate et budget", b, [ns_var, slo_var],
                     "Burn rate, alertes et budget d'erreur d'un SLO de l'équipe choisie.")

# --- Démarrage ---------------------------------------------------------------------
# Page d'accueil de Grafana (préférence posée par deploy/monitoring/grafana-home.py) : prise en main pour des
# participants qui n'ont jamais utilisé Grafana. Liens vers l'Explore prérempli avec des
# requêtes brutes : jamais de ratio de SLI, hormis l'exemple d'upload déjà fourni.
def explore(expr):
    pane = {"a": {"datasource": DS["uid"], "range": {"from": "now-1h", "to": "now"},
                  "queries": [{"refId": "A", "expr": expr, "editorMode": "code", "datasource": DS}]}}
    url = "/explore?schemaVersion=1&orgId=1&panes=" + quote(json.dumps(pane, separators=(",", ":")), safe="")
    # La variable reste lisible pour que le panneau texte la remplace par l'équipe choisie.
    return url.replace("%24namespace", "$namespace")

def ex(expr, label="▶ Explore"): return f"[{label}]({explore(expr)})"

T = 'namespace="$namespace"'
CATALOG = [
    ("Upload", "http_requests_total", "compteur", "`route`, `status`", "requêtes HTTP de l'API, par route et code de réponse",
     f'sum by (route, status) (rate(http_requests_total{{{T}}}[5m]))'),
    ("Upload", "http_request_duration_seconds", "histogramme", "`route`, `le`", "durée des requêtes HTTP (bornes 0,1 / 0,3 / 1 / 3 s)",
     f'sum by (le) (rate(http_request_duration_seconds_bucket{{{T},route="/documents"}}[5m]))'),
    ("Traitement", "jobs_processed_total", "compteur", "`status`", "documents traités par le worker",
     f'sum by (status) (rate(jobs_processed_total{{{T}}}[5m]))'),
    ("Traitement", "queue_depth", "jauge", "", "documents en attente de traitement",
     f'max(queue_depth{{{T}}})'),
    ("Traitement", "document_processing_delay_seconds", "histogramme", "`le`", "délai entre l'upload et la fin du traitement (bornes 10 / 60 / 300 / 900 s)",
     f'sum by (le) (rate(document_processing_delay_seconds_bucket{{{T}}}[5m]))'),
    ("Recherche", "search_requests_total", "compteur", "`status`", "recherches reçues par l'API",
     f'sum by (status) (rate(search_requests_total{{{T}}}[5m]))'),
    ("Recherche", "search_results_count", "histogramme", "`le`", "nombre de résultats renvoyés (bornes 0 / 1 / 5 / 20)",
     f'sum by (le) (rate(search_results_count_bucket{{{T}}}[5m]))'),
    ("Recherche", "search_fallback_total", "compteur", "", "recherches servies en mode dégradé",
     f'sum(rate(search_fallback_total{{{T}}}[5m]))'),
    ("Notifications", "notifications_enqueued_total", "compteur", "", "notifications demandées par le worker",
     f'sum(rate(notifications_enqueued_total{{{T}}}[5m]))'),
    ("Notifications", "notifications_sent_total", "compteur", "`status`", "notifications envoyées par le notifier",
     f'sum by (status) (rate(notifications_sent_total{{{T}}}[5m]))'),
    ("Notifications", "notification_delay_seconds", "histogramme", "`le`", "délai entre la demande et l'envoi (bornes 1 / 5 / 30 / 120 s)",
     f'sum by (le) (rate(notification_delay_seconds_bucket{{{T}}}[5m]))'),
]
catalog = ("Chaque lien ouvre l'**Explore** sur une requête de départ, déjà filtrée sur votre équipe. "
           "À vous de la transformer en SLI.\n\n"
           "| Parcours | Métrique | Type | Labels | Ce qu'elle compte | |\n| --- | --- | --- | --- | --- | --- |\n"
           + "\n".join(f"| {j} | `{m}` | {k} | {l} | {d} | {ex(q)} |" for j, m, k, l, d, q in CATALOG)
           + "\n\nUn histogramme se lit à travers trois séries : `<nom>_bucket{le=\"…\"}` (événements **inférieurs ou égaux** à la borne, "
             "cumulés), `<nom>_count` (tous les événements) et `<nom>_sum` (somme des valeurs).")

UP_ERR = f'sum(rate(http_requests_total{{{T},route="/documents",status=~"5.."}}[5m]))'
UP_TOT = f'sum(rate(http_requests_total{{{T},route="/documents",status!~"4.."}}[5m]))'
promql = ("Exemple fil rouge : le SLI de disponibilité de l'upload, déjà installé (`observability/sloth/upload-availability.yaml`).\n\n"
          f"1. **Choisir une métrique et filtrer** : `http_requests_total{{{T},route=\"/documents\"}}`. "
          "Les accolades gardent les séries dont les labels correspondent ; `=~` accepte une expression régulière. "
          f"{ex(f'http_requests_total{{{T},route=\"/documents\"}}')}\n"
          "2. **Passer d'un compteur à un débit** : un compteur ne fait que monter, `rate(…[5m])` donne des événements par seconde. "
          f"{ex(f'rate(http_requests_total{{{T},route=\"/documents\"}}[5m])')}\n"
          "3. **Agréger** : `sum(…)` additionne les pods, `sum by (status) (…)` garde une série par code de réponse. "
          f"{ex(f'sum by (status) (rate(http_requests_total{{{T},route=\"/documents\"}}[5m]))')}\n"
          "4. **Diviser** : mauvais événements / événements pris en compte = taux d'erreur. "
          f"{ex(f'{UP_ERR} / {UP_TOT}')}\n\n"
          "**Pièges**\n"
          "- Les bornes d'histogramme s'écrivent en flottant : `le=\"1.0\"`, pas `le=\"1\"`.\n"
          "- Dans l'Explore, gardez le filtre `namespace` : Prometheus est partagé entre les équipes. "
          "Dans les fichiers Sloth, au contraire, **pas de filtre namespace** : il est ajouté automatiquement.\n"
          "- Une requête qui ne renvoie rien n'est pas forcément fausse : un compteur d'erreurs n'existe qu'après la première erreur "
          "(d'où le `or vector(0)` de l'exemple).")

welcome = ("**Choisissez votre équipe** dans la liste *Équipe*, en haut à gauche : tous les liens de cette page suivent ce choix.\n\n"
           "Trois façons de regarder les métriques de DocShare, de la plus simple à la plus libre :\n\n"
           "1. **Observer** : le dashboard [DocShare · Parcours](/d/docshare-parcours?var-namespace=$namespace) montre les métriques brutes "
           "de chaque parcours (upload, traitement, recherche, notifications).\n"
           "2. **Parcourir sans écrire de requête** : menu ☰ → **Drilldown** → **Metrics**. Ajoutez le filtre `namespace = $namespace`, "
           "puis cherchez `http_`, `jobs_`, `document_`, `search_` ou `notification`. Chaque carte est une métrique ; "
           "**Select** la détaille par label.\n"
           "3. **Écrire une requête** : menu ☰ → **Explore** (ou les liens ▶ ci-dessous). La source est déjà *Prometheus*. "
           "Le mode **Builder** propose les métriques et les labels dans des listes ; le mode **Code** accepte du PromQL. "
           "**Shift + Entrée** lance la requête ; la période se règle en haut à droite.\n\n"
           "Vous êtes en lecture seule : rien de ce que vous faites ici ne peut casser quoi que ce soit.")

dm = [text("Bienvenue dans le Grafana de DocShare", welcome, 0, 0, 24, 9),
      text("Les métriques de DocShare", catalog, 0, 9, 24, 15),
      text("PromQL en 4 étapes", promql, 0, 24, 24, 11)]
demarrage = dashboard("docshare-demarrage", "DocShare · Démarrage", dm, [var_namespace()],
                      "Prise en main de Grafana et catalogue des métriques de DocShare.")
demarrage["refresh"] = ""

for name, d in (("parcours.json", parcours), ("burn-rate.json", burnrate), ("demarrage.json", demarrage)):
    with open(f"{OUT}/{name}", "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2); f.write("\n")
