"""Outils partagés par les tests."""
import time

from prometheus_client import REGISTRY


def no_sleep(seconds):
    pass


class FakeClock:
    """Horloge qui n'avance que quand on dort : les tests ne dorment jamais vraiment."""

    def __init__(self):
        self.now = time.time()

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def sample(name, **labels):
    """Valeur actuelle d'une série Prometheus, 0 si elle n'existe pas encore."""
    return REGISTRY.get_sample_value(name, labels) or 0.0
