"""Rôle worker : simule l'OCR, indexe le document, demande la notification."""
import logging
import os
import random
import threading
import time

import redis
from prometheus_client import Counter, Gauge, Histogram, start_http_server

import db
import faults
import jobqueue

log = logging.getLogger("worker")

CONCURRENCY = int(os.environ.get("WORKER_CONCURRENCY", "4"))

JOBS_PROCESSED = Counter("jobs_processed_total", "Jobs traités", ["status"])
QUEUE_DEPTH = Gauge("queue_depth", "Jobs en attente dans la file")
PROCESSING_DELAY = Histogram(
    "document_processing_delay_seconds", "Délai entre l'upload et la fin du traitement",
    buckets=(10, 60, 300, 900),
)
NOTIFICATIONS_ENQUEUED = Counter("notifications_enqueued_total", "Notifications mises en file")


def queue_depth():
    try:
        return jobqueue.length(jobqueue.JOBS)
    except redis.RedisError:
        return float("nan")


# Lue à chaque scrape : une seule source pour la taille de la file.
QUEUE_DEPTH.set_function(queue_depth)


def process(job):
    active = faults.current()
    # Simulation de l'OCR, multipliée par worker_slow quand la panne est active.
    time.sleep(random.uniform(1, 3) * (active.get("worker_slow") or 1))

    with db.connect() as conn:
        if active.get("stale_index"):
            # Panne : le document est marqué traité sans être indexé.
            conn.execute(
                "UPDATE documents SET status = 'done', processed_at = now() WHERE id = %s",
                (job["id"],),
            )
        else:
            conn.execute(
                "UPDATE documents SET status = 'done', processed_at = now(),"
                " search_vector = to_tsvector('simple', title || ' ' || content) WHERE id = %s",
                (job["id"],),
            )

    PROCESSING_DELAY.observe(time.time() - job["uploaded_at"])
    jobqueue.push(jobqueue.NOTIFICATIONS, {"id": job["id"], "enqueued_at": time.time()})
    NOTIFICATIONS_ENQUEUED.inc()


def loop():
    while True:
        try:
            job = jobqueue.pop(jobqueue.JOBS)
        except redis.RedisError as exc:
            log.warning("Redis indisponible : %s", exc)
            time.sleep(1)
            continue
        if job is None:
            continue
        try:
            process(job)
            JOBS_PROCESSED.labels("done").inc()
        except Exception:
            log.exception("Échec du traitement du document %s", job["id"])
            JOBS_PROCESSED.labels("failed").inc()


def run():
    start_http_server(int(os.environ.get("METRICS_PORT", "9100")))
    jobqueue.wait_until_ready()
    db.wait_until_ready()
    log.info("Worker démarré avec %d threads", CONCURRENCY)
    threads = [threading.Thread(target=loop, daemon=True) for _ in range(CONCURRENCY)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
