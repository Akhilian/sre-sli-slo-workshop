# Fait de « DocShare · Démarrage » la page d'accueil de l'organisation Grafana.
#
# Lancé par deploy/scripts/setup.sh dans le conteneur grafana-sc-dashboard, qui a Python
# et les identifiants admin (REQ_USERNAME, REQ_PASSWORD) :
#   kubectl exec -i -n monitoring deploy/kps-grafana -c grafana-sc-dashboard -- python - < deploy/monitoring/grafana-home.py
#
# default_home_dashboard_path ne convient pas : Grafana 13 en fait une copie sans droits,
# illisible pour les visiteurs anonymes. La préférence vit dans la base de Grafana, sur
# son volume persistant.
import base64, json, os, time, urllib.error, urllib.request

UID = "docshare-demarrage"
auth = base64.b64encode(f"{os.environ['REQ_USERNAME']}:{os.environ['REQ_PASSWORD']}".encode()).decode()
headers = {"Authorization": "Basic " + auth, "Content-Type": "application/json"}

def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("http://localhost:3000" + path, data=data, method=method, headers=headers)
    return urllib.request.urlopen(req, timeout=10).read()

# Le sidecar écrit le dashboard peu après la ConfigMap : attendre qu'il soit provisionné.
for _ in range(30):
    try:
        call("GET", f"/api/dashboards/uid/{UID}")
        break
    except (urllib.error.URLError, OSError):
        time.sleep(2)
else:
    raise SystemExit(f"dashboard {UID} introuvable après 60 s")

call("PATCH", "/api/org/preferences", {"homeDashboardUID": UID})
print(f"page d'accueil : {UID}")
