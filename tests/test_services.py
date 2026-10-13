"""Cas d'usage sur adaptateurs en mémoire."""
import pytest

from adapters.memory import InMemoryDocuments, InMemoryQueue
from domain.errors import DocumentNotFound
from domain.models import Notification, ProcessingJob
from domain.services import GetDocument, ProcessDocument, SearchDocuments, SendNotification, UploadDocument
from helpers import FakeClock


class NoOcr:
    def extract(self, document_id):
        pass


def test_upload_enregistre_puis_met_en_file():
    documents, jobs = InMemoryDocuments(), InMemoryQueue()

    document = UploadDocument(documents, jobs).execute("Rapport", "contenu")

    assert documents.get(document.id).status == "pending"
    job = jobs.pop(timeout=0)
    assert job == ProcessingJob(document.id, document.uploaded_at.timestamp())


def test_consultation_d_un_document_inconnu():
    with pytest.raises(DocumentNotFound):
        GetDocument(InMemoryDocuments()).execute(42)


def test_traitement_indexe_avant_de_passer_done():
    calls = []

    class Recorder(InMemoryDocuments):
        def index(self, document_id):
            calls.append("index")
            super().index(document_id)

        def mark_done(self, document_id):
            calls.append("done")
            super().mark_done(document_id)

    documents, notifications = Recorder(), InMemoryQueue()
    document = documents.add("Rapport", "doc-1a2b3c4d")
    clock = FakeClock()
    job = ProcessingJob(document.id, clock() - 12)

    delay = ProcessDocument(NoOcr(), documents, documents, notifications, clock=clock).execute(job)

    assert calls == ["index", "done"]
    assert delay == 12
    assert documents.get(document.id).status == "done"
    assert notifications.pop(timeout=0) == Notification(document.id, clock())


def test_recherche_par_mot_et_limite():
    documents = InMemoryDocuments()
    for i in range(25):
        documents.index(documents.add(f"Rapport {i}", "budget doc-1a2b3c4d").id)
    documents.add("Non indexé", "budget")

    search = SearchDocuments(documents)

    assert len(search.execute("budget")) == 20
    assert [doc.title for doc in search.execute("rapport 7")] == ["Rapport 7"]
    assert len(search.execute("doc-1a2b3c4d")) == 20
    assert search.execute("absent") == []


def test_envoi_renvoie_le_delai_depuis_la_mise_en_file():
    sent = []

    class Email:
        def send(self, notification):
            sent.append(notification)

    clock = FakeClock()
    notification = Notification(1, clock() - 3)

    assert SendNotification(Email(), clock=clock).execute(notification) == 3
    assert sent == [notification]
