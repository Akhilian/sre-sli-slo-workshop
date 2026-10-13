"""Pannes injectées. Chacune est un décorateur posé sur un port : le domaine n'en sait rien.

| Panne               | Port décoré                       | SLI dégradé   |
| ------------------- | --------------------------------- | ------------- |
| upload_latency      | DocumentRepository.add            | latence       |
| upload_error_rate   | DocumentRepository.add            | disponibilité |
| worker_slow         | Ocr.extract                       | fraîcheur     |
| stale_index         | Indexer.index                     | qualité       |
| notifier_drop       | file des notifications (pop)      | couverture    |

Les pannes actives sont relues à chaque appel : elles s'activent et se coupent à chaud.
"""
import random
import time
from typing import Protocol

NAMES = {"upload_latency", "upload_error_rate", "worker_slow", "stale_index", "notifier_drop"}


class FaultStore(Protocol):
    def current(self) -> dict[str, float]:
        """Pannes actives. Une panne absente vaut 0."""
        ...

    def set(self, name: str, value: float) -> None:
        """Active une panne, ou la coupe avec la valeur 0."""
        ...


class InjectedFault(Exception):
    """Erreur simulée, rendue en 500 par l'API."""


class FaultyDocumentRepository:
    """upload_latency et upload_error_rate, appliquées avant l'INSERT : pas de document fantôme."""

    def __init__(self, inner, faults, sleep=time.sleep, chance=random.random):
        self.inner = inner
        self.faults = faults
        self.sleep = sleep
        self.chance = chance

    def add(self, title, file):
        active = self.faults.current()
        if active.get("upload_latency"):
            self.sleep(active["upload_latency"])
        if self.chance() < active.get("upload_error_rate", 0):
            raise InjectedFault("Erreur interne simulée")
        return self.inner.add(title, file)

    def get(self, document_id):
        return self.inner.get(document_id)

    def get_file(self, document_id):
        return self.inner.get_file(document_id)

    def mark_done(self, document_id):
        self.inner.mark_done(document_id)


class SlowOcr:
    """worker_slow : l'OCR dure `facteur` fois plus longtemps."""

    def __init__(self, inner, faults, sleep=time.sleep, clock=time.monotonic):
        self.inner = inner
        self.faults = faults
        self.sleep = sleep
        self.clock = clock

    def extract(self, file):
        start = self.clock()
        text = self.inner.extract(file)
        factor = self.faults.current().get("worker_slow", 0)
        if factor > 1:
            self.sleep((factor - 1) * (self.clock() - start))
        return text


class StaleIndexer:
    """stale_index : le document n'est pas indexé, mais le traitement continue comme si de rien n'était."""

    def __init__(self, inner, faults):
        self.inner = inner
        self.faults = faults

    def index(self, document_id, text):
        if self.faults.current().get("stale_index"):
            return
        self.inner.index(document_id, text)


class LossyQueue:
    """notifier_drop : le message est retiré de la file puis oublié, sans erreur, sans log, sans compteur."""

    def __init__(self, inner, faults, chance=random.random):
        self.inner = inner
        self.faults = faults
        self.chance = chance

    def push(self, message):
        self.inner.push(message)

    def pop(self, timeout):
        message = self.inner.pop(timeout)
        if message is not None and self.chance() < self.faults.current().get("notifier_drop", 0):
            return None
        return message

    def length(self):
        return self.inner.length()
