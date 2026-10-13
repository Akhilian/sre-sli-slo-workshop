"""Boucle du worker : dépile les jobs, traite les documents, demande les notifications."""
import logging
import threading
import time

from adapters.metrics import JOBS_PROCESSED, NOTIFICATIONS_ENQUEUED, PROCESSING_DELAY

log = logging.getLogger("worker")


def handle_next(process, jobs):
    """Traite au plus un job. Renvoie False si la file est restée vide."""
    try:
        job = jobs.pop(timeout=5)
    except Exception as exc:
        log.warning("File des jobs indisponible : %s", exc)
        time.sleep(1)
        return False
    if job is None:
        return False

    try:
        delay = process.execute(job)
    except Exception:
        log.exception("Échec du traitement du document %s", job.id)
        JOBS_PROCESSED.labels("failed").inc()
        return True

    JOBS_PROCESSED.labels("done").inc()
    PROCESSING_DELAY.observe(delay)
    NOTIFICATIONS_ENQUEUED.inc()
    return True


def start(process, jobs, concurrency):
    """Lance `concurrency` threads de traitement et les renvoie."""

    def loop():
        while True:
            handle_next(process, jobs)

    threads = [threading.Thread(target=loop, daemon=True, name=f"worker-{i}") for i in range(concurrency)]
    for thread in threads:
        thread.start()
    log.info("Worker démarré avec %d threads", concurrency)
    return threads
