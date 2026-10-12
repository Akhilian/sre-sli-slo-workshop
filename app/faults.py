"""Pannes injectées, stockées dans le hash Redis `faults` et relues à chaque traitement."""
from jobqueue import client

KEY = "faults"

NAMES = {"upload_latency", "upload_error_rate", "worker_slow", "stale_index", "notifier_drop"}


def current():
    """Pannes actives, en nombres. Une panne absente vaut 0."""
    return {name: float(value) for name, value in client.hgetall(KEY).items()}


def set_fault(name, value):
    if value == 0:
        client.hdel(KEY, name)
    else:
        client.hset(KEY, name, value)
