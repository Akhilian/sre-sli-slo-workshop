"""Chaque panne dégrade son SLI, et uniquement le sien."""
import itertools

import pytest

from adapters.faults import FaultyDocumentRepository, InjectedFault, LossyQueue, SlowOcr, StaleIndexer
from adapters.memory import InMemoryDocuments, InMemoryFaultStore, InMemoryQueue
from domain.models import Notification, ProcessingJob
from domain.services import ProcessDocument, SearchDocuments, SendNotification, UploadDocument
from entrypoints import notifier
from helpers import FakeClock, sample

TOKEN = "doc-1a2b3c4d"


class OcrTwoSeconds:
    def __init__(self, clock):
        self.clock = clock

    def extract(self, document_id):
        self.clock.sleep(2)


class NoEmail:
    def send(self, notification):
        pass


def journey(active):
    """Parcours complet (upload, traitement, recherche, notification) et SLI dégradés observés.

    Le tirage aléatoire est remplacé : le premier upload tombe sous n'importe quel taux d'erreur,
    le second y échappe. Une notification tombe sous n'importe quel taux de perte.
    """
    store = InMemoryFaultStore()
    for name, value in active.items():
        store.set(name, value)
    clock = FakeClock()
    documents, jobs, notifications = InMemoryDocuments(), InMemoryQueue(), InMemoryQueue()
    upload_draws = itertools.cycle([0.0, 0.99])

    upload = UploadDocument(
        FaultyDocumentRepository(documents, store, sleep=clock.sleep, chance=lambda: next(upload_draws)), jobs)
    process = ProcessDocument(
        SlowOcr(OcrTwoSeconds(clock), store, sleep=clock.sleep, clock=clock),
        StaleIndexer(documents, store), documents, notifications, clock=clock)
    inbox = LossyQueue(notifications, store, chance=lambda: 0.0)

    degraded = set()
    for _ in range(2):
        start = clock()
        try:
            upload.execute("Rapport", TOKEN)
        except InjectedFault:
            degraded.add("disponibilité")
        if clock() - start > 0.3:
            degraded.add("latence")

    job = jobs.pop(timeout=0)
    if process.execute(job) > 60:
        degraded.add("fraîcheur")
    if not SearchDocuments(documents).execute(TOKEN):
        degraded.add("qualité")
    notification = inbox.pop(timeout=0)
    if notification is None:
        degraded.add("couverture")
    else:
        SendNotification(NoEmail(), clock=clock).execute(notification)
    return degraded


def test_sans_panne_aucun_sli_degrade():
    assert journey({}) == set()


@pytest.mark.parametrize("name, value, sli", [
    ("upload_latency", 2, "latence"),
    ("upload_error_rate", 0.5, "disponibilité"),
    ("worker_slow", 40, "fraîcheur"),
    ("stale_index", 1, "qualité"),
    ("notifier_drop", 0.5, "couverture"),
])
def test_chaque_panne_ne_degrade_que_son_sli(name, value, sli):
    assert journey({name: value}) == {sli}


def test_erreur_d_upload_sans_document_fantome():
    store = InMemoryFaultStore()
    store.set("upload_error_rate", 1)
    documents, jobs = InMemoryDocuments(), InMemoryQueue()
    upload = UploadDocument(FaultyDocumentRepository(documents, store), jobs)

    with pytest.raises(InjectedFault):
        upload.execute("Rapport", TOKEN)

    assert documents.get(1) is None
    assert jobs.length() == 0


def test_index_perime_document_done_mais_introuvable():
    store = InMemoryFaultStore()
    store.set("stale_index", 1)
    documents, notifications = InMemoryDocuments(), InMemoryQueue()
    document = documents.add("Rapport", TOKEN)

    ProcessDocument(OcrTwoSeconds(FakeClock()), StaleIndexer(documents, store), documents, notifications).execute(
        ProcessingJob(document.id, document.uploaded_at.timestamp()))

    assert documents.get(document.id).status == "done"
    assert documents.search(TOKEN, 20) == []


def test_perte_de_notification_invisible(caplog):
    store = InMemoryFaultStore()
    store.set("notifier_drop", 1)
    notifications = InMemoryQueue()
    notifications.push(Notification(1, 0.0))
    sent_before = sample("notifications_sent_total", status="ok")

    notifier.handle_next(SendNotification(NoEmail()), LossyQueue(notifications, store))

    assert notifications.length() == 0
    assert sample("notifications_sent_total", status="ok") == sent_before
    assert caplog.records == []


def test_panne_coupee_a_chaud():
    store = InMemoryFaultStore()
    documents, jobs = InMemoryDocuments(), InMemoryQueue()
    upload = UploadDocument(FaultyDocumentRepository(documents, store), jobs)

    store.set("upload_error_rate", 1)
    with pytest.raises(InjectedFault):
        upload.execute("Rapport", TOKEN)
    store.set("upload_error_rate", 0)

    assert upload.execute("Rapport", TOKEN).id == 1
    assert store.current() == {}
