"""Cas d'usage sur adaptateurs en mémoire."""
import pytest

from adapters.memory import InMemoryDocuments, InMemoryQueue
from domain.errors import DocumentNotFound
from domain.models import Notification, ProcessingJob
from domain.services import DownloadDocument, GetDocument, ProcessDocument, SearchDocuments, SendNotification, UploadDocument
from helpers import FakeClock, text_file


class NoOcr:
    def extract(self, file):
        return file.data.decode()


def test_upload_enregistre_puis_met_en_file():
    documents, jobs = InMemoryDocuments(), InMemoryQueue()

    document = UploadDocument(documents, jobs).execute(text_file("contenu"), "Rapport")

    assert documents.get(document.id).status == "pending"
    assert documents.get_file(document.id).data == b"contenu"
    job = jobs.pop(timeout=0)
    assert job == ProcessingJob(document.id, document.uploaded_at.timestamp())


def test_consultation_d_un_document_inconnu():
    with pytest.raises(DocumentNotFound):
        GetDocument(InMemoryDocuments()).execute(42)


def test_traitement_indexe_avant_de_passer_done():
    calls = []

    class Recorder(InMemoryDocuments):
        def index(self, document_id, text):
            calls.append("index")
            super().index(document_id, text)

        def mark_done(self, document_id):
            calls.append("done")
            super().mark_done(document_id)

    documents, notifications = Recorder(), InMemoryQueue()
    document = documents.add("Rapport", text_file("doc-1a2b3c4d"))
    clock = FakeClock()
    job = ProcessingJob(document.id, clock() - 12)

    delay = ProcessDocument(NoOcr(), documents, documents, notifications, clock=clock).execute(job)

    assert calls == ["index", "done"]
    assert delay == 12
    assert documents.get(document.id).status == "done"
    assert documents.search("doc-1a2b3c4d", 20) == [documents.get(document.id)]
    assert notifications.pop(timeout=0) == Notification(document.id, clock())


def test_recherche_par_mot_et_limite():
    documents = InMemoryDocuments()
    for i in range(25):
        documents.index(documents.add(f"Rapport {i}", text_file("")).id, "budget doc-1a2b3c4d")
    documents.add("Non indexé", text_file("budget"))

    search = SearchDocuments(documents)

    assert len(search.execute("budget")) == 20
    assert [doc.title for doc in search.execute("rapport 7")] == ["Rapport 7"]
    assert len(search.execute("doc-1a2b3c4d")) == 20
    assert search.execute("absent") == []
    assert len(search.execute("1a2b3c4d")) == 20  # partie d'un mot composé, comme avec Postgres


def test_envoi_renvoie_le_delai_depuis_la_mise_en_file():
    sent = []

    class Email:
        def send(self, notification):
            sent.append(notification)

    clock = FakeClock()
    notification = Notification(1, clock() - 3)

    assert SendNotification(Email(), clock=clock).execute(notification) == 3
    assert sent == [notification]


def test_titre_par_defaut_nom_du_fichier():
    documents = InMemoryDocuments()

    document = UploadDocument(documents, InMemoryQueue()).execute(text_file("x", "notes.md"))

    assert document.title == "notes.md"
    assert (document.filename, document.content_type, document.size) == ("notes.md", "text/plain", 1)


def test_telechargement():
    documents = InMemoryDocuments()
    document = documents.add("Rapport", text_file("contenu"))

    assert DownloadDocument(documents).execute(document.id) == text_file("contenu")
    with pytest.raises(DocumentNotFound):
        DownloadDocument(documents).execute(99)
