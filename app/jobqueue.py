"""Files Redis : `jobs` (api -> worker) et `notifications` (worker -> notifier)."""
import json
import logging
import os
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

JOBS = "jobs"
NOTIFICATIONS = "notifications"

log = logging.getLogger("queue")

client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def wait_until_ready():
    while True:
        try:
            client.ping()
            return
        except redis.RedisError as exc:
            log.warning("Redis indisponible, nouvel essai dans 2 s : %s", exc)
            time.sleep(2)


def push(queue, message):
    client.lpush(queue, json.dumps(message))


def pop(queue, timeout=5):
    """Attend un message au plus `timeout` secondes. Renvoie None si la file reste vide."""
    item = client.brpop(queue, timeout=timeout)
    return json.loads(item[1]) if item else None


def length(queue):
    return client.llen(queue)
