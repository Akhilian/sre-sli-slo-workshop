"""Rôle notifier : « envoie » les notifications (simulé)."""
import logging
import os
import random
import time

import redis
from prometheus_client import Counter, Histogram, start_http_server

import faults
import jobqueue

log = logging.getLogger("notifier")

NOTIFICATIONS_SENT = Counter("notifications_sent_total", "Notifications envoyées", ["status"])
NOTIFICATION_DELAY = Histogram(
    "notification_delay_seconds", "Délai entre la mise en file et l'envoi",
    buckets=(1, 5, 30, 120),
)


def send(message):
    time.sleep(0.05)  # appel au fournisseur d'e-mails, simulé


def run():
    start_http_server(int(os.environ.get("METRICS_PORT", "9100")))
    jobqueue.wait_until_ready()
    log.info("Notifier démarré")
    while True:
        try:
            message = jobqueue.pop(jobqueue.NOTIFICATIONS)
        except redis.RedisError as exc:
            log.warning("Redis indisponible : %s", exc)
            time.sleep(1)
            continue
        if message is None:
            continue

        # Panne : la notification disparaît, sans erreur, sans log, sans compteur.
        if random.random() < faults.current().get("notifier_drop", 0):
            continue

        try:
            send(message)
            NOTIFICATIONS_SENT.labels("ok").inc()
        except Exception:
            log.exception("Échec de l'envoi de la notification %s", message["id"])
            NOTIFICATIONS_SENT.labels("failed").inc()
            continue
        NOTIFICATION_DELAY.observe(time.time() - message["enqueued_at"])
