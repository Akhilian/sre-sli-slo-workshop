"""Mode standalone : API, worker et notifier dans un seul processus, sans Redis ni Postgres."""
import logging

from entrypoints import http, notifier, worker

log = logging.getLogger("standalone")


def run(app, port):
    """Démarre les threads du worker et du notifier, puis l'API au premier plan."""
    worker.start(app.process, app.jobs, app.concurrency)
    notifier.start(app.send, app.notifications)
    log.info("Mode standalone : données en mémoire, perdues à l'arrêt")
    http.run(app.api, port)
