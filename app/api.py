"""Rôle api : upload, consultation, recherche, pilotage des pannes."""
import logging
import os
import random
import time

import psycopg
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

import db
import faults
import jobqueue

log = logging.getLogger("api")

# --- Métriques -------------------------------------------------------------

HTTP_REQUESTS = Counter("http_requests_total", "Requêtes HTTP traitées", ["route", "status"])
HTTP_DURATION = Histogram(
    "http_request_duration_seconds", "Durée des requêtes HTTP", ["route"],
    buckets=(0.1, 0.3, 1, 3),
)
SEARCH_REQUESTS = Counter("search_requests_total", "Recherches traitées", ["status"])
SEARCH_RESULTS = Histogram("search_results_count", "Nombre de résultats par recherche", buckets=(0, 1, 5, 20))
SEARCH_FALLBACK = Counter("search_fallback_total", "Recherches en échec masquées par une réponse vide")

NOT_INSTRUMENTED = {"/metrics", "/healthz", "/admin/faults"}


class MetricsMiddleware:
    """Mesure chaque requête avec le modèle de route (/documents/{id}), jamais le chemin réel."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        status = 500
        start = time.perf_counter()

        async def send_and_capture(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_and_capture)
        finally:
            route = scope.get("route")
            # Les URL sans route (404) ne sont pas mesurées : pas d'explosion de cardinalité.
            if route is not None and route.path not in NOT_INSTRUMENTED:
                HTTP_REQUESTS.labels(route.path, str(status)).inc()
                HTTP_DURATION.labels(route.path).observe(time.perf_counter() - start)


app = FastAPI(title="DocShare")
app.add_middleware(MetricsMiddleware)


# --- Parcours upload -------------------------------------------------------

class DocumentIn(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


@app.post("/documents", status_code=202)
def upload(doc: DocumentIn):
    active = faults.current()
    time.sleep(active.get("upload_latency", 0))
    # L'erreur arrive avant l'INSERT : pas de document fantôme dans le pipeline.
    if random.random() < active.get("upload_error_rate", 0):
        raise HTTPException(status_code=500, detail="Erreur interne simulée")

    with db.connect() as conn:
        row = conn.execute(
            "INSERT INTO documents (title, content) VALUES (%s, %s) RETURNING id, uploaded_at",
            (doc.title, doc.content),
        ).fetchone()
    doc_id, uploaded_at = row
    jobqueue.push(jobqueue.JOBS, {"id": doc_id, "uploaded_at": uploaded_at.timestamp()})
    return {"id": doc_id}


@app.get("/documents/{id}")
def get_document(id: int):
    with db.connect() as conn:
        row = conn.execute(
            "SELECT id, title, status, uploaded_at, processed_at FROM documents WHERE id = %s",
            (id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Document inconnu")
    return dict(zip(("id", "title", "status", "uploaded_at", "processed_at"), row))


# --- Parcours recherche ----------------------------------------------------

@app.get("/search")
def search(q: str = Query(min_length=1)):
    try:
        with db.connect(statement_timeout_ms=2000) as conn:
            rows = conn.execute(
                "SELECT id, title FROM documents"
                " WHERE search_vector @@ plainto_tsquery('simple', %s) LIMIT 20",
                (q,),
            ).fetchall()
    except psycopg.Error as exc:
        # Dégradation « gracieuse » : l'erreur disparaît derrière un 200 vide.
        log.warning("Recherche en échec, réponse vide : %s", exc)
        SEARCH_FALLBACK.inc()
        SEARCH_REQUESTS.labels("fallback").inc()
        return {"results": []}

    SEARCH_REQUESTS.labels("ok").inc()
    SEARCH_RESULTS.observe(len(rows))
    return {"results": [{"id": doc_id, "title": title} for doc_id, title in rows]}


# --- Pilotage des pannes ---------------------------------------------------

class FaultIn(BaseModel):
    name: str
    value: float = Field(ge=0)


@app.get("/admin/faults")
def list_faults():
    return faults.current()


@app.post("/admin/faults")
def set_fault(fault: FaultIn):
    if fault.name not in faults.NAMES:
        raise HTTPException(status_code=422, detail=f"Panne inconnue, valeurs possibles : {sorted(faults.NAMES)}")
    faults.set_fault(fault.name, fault.value)
    return faults.current()


# --- Exploitation ----------------------------------------------------------

@app.get("/healthz")
def healthz():
    # Ne lit pas les pannes : une panne de latence ne doit pas faire redémarrer le pod.
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def run():
    jobqueue.wait_until_ready()
    db.wait_until_ready()
    db.create_schema()
    # Un seul processus uvicorn : prometheus_client n'a pas besoin du mode multiprocess.
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), workers=1)
