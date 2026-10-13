"""Toutes les métriques exposées par DocShare. Ce sont les seules matières premières des SLI.

Noms, labels et buckets sont le contrat des SLO Sloth et des dashboards : ne pas les changer.
"""
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram

# Pas de séries *_created : elles encombrent /metrics sans servir l'exercice.
prometheus_client.disable_created_metrics()

# --- Upload (api) ------------------------------------------------------------
HTTP_REQUESTS = Counter("http_requests_total", "Requêtes HTTP traitées", ["route", "status"])
HTTP_DURATION = Histogram(
    "http_request_duration_seconds", "Durée des requêtes HTTP", ["route"],
    buckets=(0.1, 0.3, 1, 3),
)

# --- Recherche (api) ---------------------------------------------------------
SEARCH_REQUESTS = Counter("search_requests_total", "Recherches traitées", ["status"])
SEARCH_RESULTS = Histogram("search_results_count", "Nombre de résultats par recherche", buckets=(0, 1, 5, 20))
SEARCH_FALLBACK = Counter("search_fallback_total", "Recherches en échec masquées par une réponse vide")

# --- Traitement (worker) -----------------------------------------------------
JOBS_PROCESSED = Counter("jobs_processed_total", "Jobs traités", ["status"])
QUEUE_DEPTH = Gauge("queue_depth", "Jobs en attente dans la file")
PROCESSING_DELAY = Histogram(
    "document_processing_delay_seconds", "Délai entre l'upload et la fin du traitement",
    buckets=(10, 60, 300, 900),
)

# --- Notifications (worker puis notifier) ------------------------------------
NOTIFICATIONS_ENQUEUED = Counter("notifications_enqueued_total", "Notifications mises en file")
NOTIFICATIONS_SENT = Counter("notifications_sent_total", "Notifications envoyées", ["status"])
NOTIFICATION_DELAY = Histogram(
    "notification_delay_seconds", "Délai entre la mise en file et l'envoi",
    buckets=(1, 5, 30, 120),
)


# Métriques propres à chaque rôle distribué (spec service-metrics) ; standalone les expose toutes.
ROLE_METRICS = {
    "api": (HTTP_REQUESTS, HTTP_DURATION, SEARCH_REQUESTS, SEARCH_RESULTS, SEARCH_FALLBACK),
    "worker": (JOBS_PROCESSED, QUEUE_DEPTH, PROCESSING_DELAY, NOTIFICATIONS_ENQUEUED),
    "notifier": (NOTIFICATIONS_SENT, NOTIFICATION_DELAY),
}


def expose_only(role):
    """Retire du registre les métriques des autres rôles : elles n'afficheraient que des zéros."""
    for collectors in (c for r, c in ROLE_METRICS.items() if r != role):
        for collector in collectors:
            prometheus_client.REGISTRY.unregister(collector)


def watch_queue_depth(jobs):
    """`queue_depth` est lue dans la file à chaque scrape : une seule source pour sa taille."""

    def depth():
        try:
            return jobs.length()
        except Exception:
            return float("nan")

    QUEUE_DEPTH.set_function(depth)
