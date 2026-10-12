# Génère les dashboards JSON de ce dossier : python3 grafana/generate.py grafana
# Modifier ce script plutôt que les JSON, pour garder les requêtes cohérentes entre panneaux.
import json, sys
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
p.append(ts("Part des uploads sous les seuils de durée", [
    target(f'sum({r(f"http_request_duration_seconds_bucket{{{UP},le=\"0.3\"}}")}) / sum({r(f"http_request_duration_seconds_count{{{UP}}}")})', "< 0,3 s", ref="A"),
    target(f'sum({r(f"http_request_duration_seconds_bucket{{{UP},le=\"1.0\"}}")}) / sum({r(f"http_request_duration_seconds_count{{{UP}}}")})', "< 1 s", ref="B"),
], 12, y, unit="percentunit", minv=0, maxv=1)); y += 8
p.append(row("Traitement", y)); y += 1
p.append(ts("Jobs en attente", [target(f'max(queue_depth{{{NS}}})', "file")], 0, y, w=8,
            desc="Taille de la file. Une file pleine gêne-t-elle l'utilisateur ? Pas toujours : ce n'est pas un SLI."))
p.append(ts("Part des documents traités sous les seuils de délai", [
    target(f'sum({r(f"document_processing_delay_seconds_bucket{{{NS},le=\"60.0\"}}", "2m")}) / sum({r(f"document_processing_delay_seconds_count{{{NS}}}", "2m")})', "< 60 s", ref="A"),
    target(f'sum({r(f"document_processing_delay_seconds_bucket{{{NS},le=\"300.0\"}}", "2m")}) / sum({r(f"document_processing_delay_seconds_count{{{NS}}}", "2m")})', "< 300 s", ref="B"),
], 8, y, w=8, unit="percentunit", minv=0, maxv=1,
    desc="Délai entre l'upload et la fin du traitement, mesuré à la fin du job : un document bloqué n'apparaît qu'une fois traité."))
p.append(ts("Jobs traités par statut", [target(f'sum by (status) ({r(f"jobs_processed_total{{{NS}}}")})', "{{status}}")], 16, y, w=8, unit="ops")); y += 8
p.append(row("Recherche", y)); y += 1
p.append(ts("Recherches par statut", [target(f'sum by (status) ({r(f"search_requests_total{{{NS}}}")})', "{{status}}")], 0, y, w=8, unit="reqps"))
p.append(ts("Part des recherches sans résultat", [
    target(f'sum({r(f"search_results_count_bucket{{{NS},le=\"0.0\"}}")}) / sum({r(f"search_results_count_count{{{NS}}}")})', "0 résultat")],
    8, y, w=8, unit="percentunit", minv=0, maxv=1, desc="Les équipes ne cherchent que des documents existants : une recherche vide est anormale."))
p.append(ts("Recherches en repli", [target(f'sum({r(f"search_fallback_total{{{NS}}}")}) or vector(0)', "replis")], 16, y, w=8, unit="reqps",
            desc="Erreurs Postgres masquées derrière un 200 avec une liste vide.")); y += 8
p.append(row("Notifications", y)); y += 1
p.append(ts("Notifications demandées et envoyées", [
    target(f'sum({r(f"notifications_enqueued_total{{{NS}}}")})', "demandées (worker)", ref="A"),
    target(f'sum({r(f"notifications_sent_total{{{NS},status=\"ok\"}}")})', "envoyées (notifier)", ref="B"),
], 0, y, unit="ops"))
p.append(ts("Part des notifications envoyées en moins de 5 s", [
    target(f'sum({r(f"notification_delay_seconds_bucket{{{NS},le=\"5.0\"}}")}) / sum({r(f"notification_delay_seconds_count{{{NS}}}")})', "< 5 s")],
    12, y, unit="percentunit", minv=0, maxv=1))
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

for name, d in (("parcours.json", parcours), ("burn-rate.json", burnrate)):
    with open(f"{OUT}/{name}", "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2); f.write("\n")
