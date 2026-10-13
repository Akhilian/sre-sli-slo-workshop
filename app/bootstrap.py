"""Câblage : construit les adaptateurs de chaque rôle, pose les pannes et branche les cas d'usage.

C'est le seul endroit qui connaît à la fois le domaine et les adaptateurs concrets.
"""
import os
from dataclasses import dataclass

from prometheus_client import start_http_server

from adapters import faults, metrics
from adapters.memory import InMemoryDocuments, InMemoryFaultStore, InMemoryQueue
from adapters.simulated import SimulatedEmailSender, SimulatedOcr
from domain.models import Notification, ProcessingJob
from domain.services import GetDocument, ProcessDocument, SearchDocuments, SendNotification, UploadDocument
from entrypoints import http, notifier, standalone, worker

PORT = int(os.environ.get("PORT", "8000"))
METRICS_PORT = int(os.environ.get("METRICS_PORT", "9100"))
WORKER_CONCURRENCY = int(os.environ.get("WORKER_CONCURRENCY", "4"))


def api_services(documents, jobs, fault_store):
    return http.ApiServices(
        upload=UploadDocument(faults.FaultyDocumentRepository(documents, fault_store), jobs),
        get_document=GetDocument(documents),
        search=SearchDocuments(documents),
        faults=fault_store,
    )


def process_document(documents, notifications, fault_store, ocr):
    return ProcessDocument(
        ocr=faults.SlowOcr(ocr, fault_store),
        indexer=faults.StaleIndexer(documents, fault_store),
        documents=documents,
        notifications=notifications,
    )


@dataclass
class StandaloneApp:
    api: http.ApiServices
    process: ProcessDocument
    send: SendNotification
    jobs: InMemoryQueue
    notifications: faults.LossyQueue
    concurrency: int


def build_standalone(ocr=None, email=None, concurrency=WORKER_CONCURRENCY):
    """Toute l'application sur des adaptateurs en mémoire, partagés par l'API, le worker et le notifier."""
    documents = InMemoryDocuments()
    jobs = InMemoryQueue()
    notifications = InMemoryQueue()
    fault_store = InMemoryFaultStore()
    metrics.watch_queue_depth(jobs)
    return StandaloneApp(
        api=api_services(documents, jobs, fault_store),
        process=process_document(documents, notifications, fault_store, ocr or SimulatedOcr()),
        send=SendNotification(email or SimulatedEmailSender()),
        jobs=jobs,
        notifications=faults.LossyQueue(notifications, fault_store),
        concurrency=concurrency,
    )


def run(role):
    if role == "standalone":
        standalone.run(build_standalone(), PORT)
        return

    # Mode distribué : imports ici, pour que le mode standalone n'ait besoin ni de Redis ni de Postgres.
    from adapters import redis
    from adapters.postgres import PostgresDocuments

    if role in ("worker", "notifier"):
        # Port de métriques ouvert d'abord : il sert aussi de sonde pendant l'attente des dépendances.
        start_http_server(METRICS_PORT)

    client = redis.connect(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    redis.wait_until_ready(client)
    fault_store = redis.RedisFaultStore(client)
    jobs = redis.RedisQueue(client, "jobs", ProcessingJob)
    notifications = redis.RedisQueue(client, "notifications", Notification)

    if role == "notifier":
        thread = notifier.start(SendNotification(SimulatedEmailSender()), faults.LossyQueue(notifications, fault_store))
        thread.join()
        return

    documents = PostgresDocuments(os.environ.get("DATABASE_URL", "postgresql://docshare:docshare@localhost:5432/docshare"))
    documents.wait_until_ready()

    if role == "api":
        documents.create_schema()
        http.run(api_services(documents, jobs, fault_store), PORT)
    else:
        metrics.watch_queue_depth(jobs)
        threads = worker.start(process_document(documents, notifications, fault_store, SimulatedOcr()), jobs, WORKER_CONCURRENCY)
        for thread in threads:
            thread.join()
