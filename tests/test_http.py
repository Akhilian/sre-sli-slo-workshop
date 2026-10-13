"""API FastAPI sur adaptateurs en mémoire : réponses et instrumentation."""
import pytest
from fastapi.testclient import TestClient

from domain.errors import SearchUnavailable
from domain.services import SearchDocuments
from entrypoints.http import create_app
from helpers import sample


@pytest.fixture
def client(standalone):
    return TestClient(create_app(standalone.api))


def upload(client, content="contenu doc-1a2b3c4d"):
    return client.post("/documents", json={"title": "Rapport", "content": content})


def test_upload_202_puis_consultation(client, standalone):
    before = sample("http_requests_total", route="/documents", status="202")

    response = upload(client)

    assert response.status_code == 202
    document_id = response.json()["id"]
    body = client.get(f"/documents/{document_id}").json()
    assert body["status"] == "pending"
    assert set(body) == {"id", "title", "status", "uploaded_at", "processed_at"}
    assert standalone.jobs.length() == 1
    assert sample("http_requests_total", route="/documents", status="202") == before + 1


def test_upload_invalide_422_sans_document(client, standalone):
    response = client.post("/documents", json={"title": "Rapport", "content": ""})

    assert response.status_code == 422
    assert standalone.jobs.length() == 0


def test_document_inconnu_404(client):
    assert client.get("/documents/999").status_code == 404


def test_label_route_est_le_modele_de_route(client):
    before = sample("http_requests_total", route="/documents/{id}", status="200")
    ids = [upload(client).json()["id"] for _ in range(3)]

    for document_id in ids:
        client.get(f"/documents/{document_id}")

    assert sample("http_requests_total", route="/documents/{id}", status="200") == before + 3
    assert sample("http_requests_total", route=f"/documents/{ids[0]}", status="200") == 0


@pytest.mark.parametrize("path", ["/healthz", "/metrics", "/admin/faults", "/inconnue"])
def test_routes_non_instrumentees(client, path):
    client.get(path)

    for status in ("200", "404"):
        assert sample("http_requests_total", route=path, status=status) == 0


def test_panne_inconnue_422(client):
    response = client.post("/admin/faults", json={"name": "inconnue", "value": 1})

    assert response.status_code == 422


def test_panne_d_erreur_rendue_en_500(client):
    before = sample("http_requests_total", route="/documents", status="500")
    client.post("/admin/faults", json={"name": "upload_error_rate", "value": 1})

    response = upload(client)

    assert response.status_code == 500
    assert response.json() == {"detail": "Erreur interne simulée"}
    assert sample("http_requests_total", route="/documents", status="500") == before + 1

    assert client.post("/admin/faults", json={"name": "upload_error_rate", "value": 0}).json() == {}
    assert upload(client).status_code == 202


def test_recherche_en_echec_masquee_par_un_200_vide(standalone):
    class BrokenIndex:
        def search(self, query, limit):
            raise SearchUnavailable("délai dépassé")

    standalone.api.search = SearchDocuments(BrokenIndex())
    client = TestClient(create_app(standalone.api))
    fallback_before = sample("search_fallback_total")
    status_before = sample("search_requests_total", status="fallback")

    response = client.get("/search", params={"q": "budget"})

    assert response.status_code == 200
    assert response.json() == {"results": []}
    assert sample("search_fallback_total") == fallback_before + 1
    assert sample("search_requests_total", status="fallback") == status_before + 1
