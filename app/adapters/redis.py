"""Adaptateur Redis : files `jobs` et `notifications`, hash `faults`."""
import dataclasses
import json
import logging
import time

import redis

log = logging.getLogger("redis")


def connect(url):
    return redis.Redis.from_url(url, decode_responses=True)


def wait_until_ready(client):
    while True:
        try:
            client.ping()
            return
        except redis.RedisError as exc:
            log.warning("Redis indisponible, nouvel essai dans 2 s : %s", exc)
            time.sleep(2)


class RedisQueue:
    """File Redis de messages JSON. Les clés JSON sont les champs du message (`id`, `uploaded_at`...)."""

    def __init__(self, client, name, message_type):
        self.client = client
        self.name = name
        self.message_type = message_type

    def push(self, message):
        self.client.lpush(self.name, json.dumps(dataclasses.asdict(message)))

    def pop(self, timeout):
        item = self.client.brpop(self.name, timeout=timeout)
        return self.message_type(**json.loads(item[1])) if item else None

    def length(self):
        return self.client.llen(self.name)


class RedisFaultStore:
    """Pannes actives dans le hash `faults`, partagé par les trois rôles d'une équipe."""

    KEY = "faults"

    def __init__(self, client):
        self.client = client

    def current(self):
        return {name: float(value) for name, value in self.client.hgetall(self.KEY).items()}

    def set(self, name, value):
        if value == 0:
            self.client.hdel(self.KEY, name)
        else:
            self.client.hset(self.KEY, name, value)
