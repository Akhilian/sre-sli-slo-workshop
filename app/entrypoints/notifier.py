"""Boucle du notifier : dépile les notifications et les « envoie »."""
import logging
import threading
import time

from adapters.metrics import NOTIFICATION_DELAY, NOTIFICATIONS_SENT

log = logging.getLogger("notifier")


def handle_next(send, notifications):
    """Envoie au plus une notification. Renvoie False si la file est restée vide."""
    try:
        notification = notifications.pop(timeout=5)
    except Exception as exc:
        log.warning("File des notifications indisponible : %s", exc)
        time.sleep(1)
        return False
    if notification is None:
        return False

    try:
        delay = send.execute(notification)
    except Exception:
        log.exception("Échec de l'envoi de la notification %s", notification.id)
        NOTIFICATIONS_SENT.labels("failed").inc()
        return True

    NOTIFICATIONS_SENT.labels("ok").inc()
    NOTIFICATION_DELAY.observe(delay)
    return True


def start(send, notifications):
    """Lance le thread d'envoi et le renvoie."""

    def loop():
        while True:
            handle_next(send, notifications)

    thread = threading.Thread(target=loop, daemon=True, name="notifier")
    thread.start()
    log.info("Notifier démarré")
    return thread
