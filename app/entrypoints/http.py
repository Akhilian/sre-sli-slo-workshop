"""API HTTP : upload, consultation, recherche, pilotage des pannes."""
import logging
import time
from dataclasses import asdict, dataclass
from typing import Annotated
from urllib.parse import quote

import uvicorn
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from adapters import faults
from adapters.metrics import HTTP_DURATION, HTTP_REQUESTS, SEARCH_FALLBACK, SEARCH_REQUESTS, SEARCH_RESULTS
from domain.errors import DocumentNotFound, SearchUnavailable
from domain.models import StoredFile
from domain.services import DownloadDocument, GetDocument, SearchDocuments, UploadDocument

log = logging.getLogger("api")

NOT_INSTRUMENTED = {"/metrics", "/healthz", "/admin/faults"}

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@dataclass
class ApiServices:
    upload: UploadDocument
    get_document: GetDocument
    download: DownloadDocument
    search: SearchDocuments
    faults: faults.FaultStore


def get_services(request: Request) -> ApiServices:
    return request.app.state.services


Services = Annotated[ApiServices, Depends(get_services)]


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


class FaultIn(BaseModel):
    name: str
    value: float = Field(ge=0)


def create_app(services: ApiServices, max_upload_bytes: int = MAX_UPLOAD_BYTES) -> FastAPI:
    app = FastAPI(title="DocShare")
    app.state.services = services
    app.add_middleware(MetricsMiddleware)

    @app.exception_handler(faults.InjectedFault)
    def injected_fault(request, exc):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    # --- Parcours upload -------------------------------------------------------

    @app.post("/documents", status_code=202)
    def upload(services: Services, file: UploadFile, title: Annotated[str | None, Form()] = None):
        data = file.file.read(max_upload_bytes + 1)
        if len(data) > max_upload_bytes:
            raise HTTPException(status_code=413, detail=f"Fichier trop volumineux ({max_upload_bytes // 1024 // 1024} Mio au plus)")
        if not data:
            raise HTTPException(status_code=422, detail="Fichier vide")
        stored = StoredFile(file.filename or "document", file.content_type or "application/octet-stream", data)
        document = services.upload.execute(stored, title)
        return {"id": document.id}

    @app.get("/documents/{id}")
    def get_document(id: int, services: Services):
        try:
            return asdict(services.get_document.execute(id))
        except DocumentNotFound:
            raise HTTPException(status_code=404, detail="Document inconnu")

    @app.get("/documents/{id}/file")
    def download(id: int, services: Services):
        try:
            file = services.download.execute(id)
        except DocumentNotFound:
            raise HTTPException(status_code=404, detail="Fichier inconnu")
        # attachment : le navigateur télécharge le fichier au lieu de l'afficher.
        disposition = f"attachment; filename*=UTF-8''{quote(file.filename)}"
        return Response(file.data, media_type=file.content_type, headers={"Content-Disposition": disposition})

    # --- Parcours recherche ----------------------------------------------------

    @app.get("/search")
    def search(services: Services, q: str = Query(min_length=1)):
        try:
            documents = services.search.execute(q)
        except SearchUnavailable as exc:
            # Dégradation « gracieuse » : l'erreur disparaît derrière un 200 vide.
            log.warning("Recherche en échec, réponse vide : %s", exc)
            SEARCH_FALLBACK.inc()
            SEARCH_REQUESTS.labels("fallback").inc()
            return {"results": []}

        SEARCH_REQUESTS.labels("ok").inc()
        SEARCH_RESULTS.observe(len(documents))
        return {"results": [{"id": doc.id, "title": doc.title} for doc in documents]}

    # --- Pilotage des pannes ---------------------------------------------------

    @app.get("/admin/faults")
    def list_faults(services: Services):
        return services.faults.current()

    @app.post("/admin/faults")
    def set_fault(fault: FaultIn, services: Services):
        if fault.name not in faults.NAMES:
            raise HTTPException(status_code=422, detail=f"Panne inconnue, valeurs possibles : {sorted(faults.NAMES)}")
        services.faults.set(fault.name, fault.value)
        return services.faults.current()

    # --- Exploitation ----------------------------------------------------------

    @app.get("/healthz")
    def healthz():
        # Ne lit pas les pannes : une panne de latence ne doit pas faire redémarrer le pod.
        return {"status": "ok"}

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


def run(services: ApiServices, port: int, max_upload_bytes: int = MAX_UPLOAD_BYTES):
    # Un seul processus uvicorn : prometheus_client n'a pas besoin du mode multiprocess.
    uvicorn.run(create_app(services, max_upload_bytes), host="0.0.0.0", port=port, workers=1)
