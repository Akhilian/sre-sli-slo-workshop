"""Mode standalone : toute l'application dans un processus, boucles démarrées."""
import time

from fastapi.testclient import TestClient

from entrypoints import notifier, worker
from entrypoints.http import create_app
from helpers import sample


def wait_for(condition, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.02)
    return False


def test_parcours_complet_sans_infrastructure(standalone):
    worker.start(standalone.process, standalone.jobs, standalone.concurrency)
    notifier.start(standalone.send, standalone.notifications)
    client = TestClient(create_app(standalone.api))
    sent_before = sample("notifications_sent_total", status="ok")

    document_id = client.post("/documents", json={"title": "Rapport", "content": "doc-1a2b3c4d"}).json()["id"]

    assert wait_for(lambda: client.get(f"/documents/{document_id}").json()["status"] == "done")
    assert client.get("/search", params={"q": "doc-1a2b3c4d"}).json() == {
        "results": [{"id": document_id, "title": "Rapport"}]
    }
    assert wait_for(lambda: sample("notifications_sent_total", status="ok") == sent_before + 1)

    exposed = client.get("/metrics").text
    for name in ("http_requests_total", "queue_depth", "search_results_count", "notifications_sent_total"):
        assert name in exposed
