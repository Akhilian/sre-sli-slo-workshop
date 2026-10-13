"""Cas d'usage. Ils ne connaissent ni HTTP, ni Redis, ni Postgres, ni les pannes, ni les métriques."""
import time

from domain.errors import DocumentNotFound
from domain.models import Document, Notification, ProcessingJob, StoredFile
from domain.ports import DocumentRepository, EmailSender, Indexer, Ocr, Queue, SearchIndex

SEARCH_LIMIT = 20


class UploadDocument:
    def __init__(self, documents: DocumentRepository, jobs: Queue[ProcessingJob]):
        self.documents = documents
        self.jobs = jobs

    def execute(self, file: StoredFile, title: str | None = None) -> Document:
        # Sans titre, le document porte le nom de son fichier.
        # Si l'enregistrement échoue, aucun job n'est mis en file.
        document = self.documents.add(title or file.filename, file)
        self.jobs.push(ProcessingJob(document.id, document.uploaded_at.timestamp()))
        return document


class GetDocument:
    def __init__(self, documents: DocumentRepository):
        self.documents = documents

    def execute(self, document_id: int) -> Document:
        document = self.documents.get(document_id)
        if document is None:
            raise DocumentNotFound(document_id)
        return document


class DownloadDocument:
    def __init__(self, documents: DocumentRepository):
        self.documents = documents

    def execute(self, document_id: int) -> StoredFile:
        file = self.documents.get_file(document_id)
        if file is None:
            raise DocumentNotFound(document_id)
        return file


class SearchDocuments:
    def __init__(self, index: SearchIndex):
        self.index = index

    def execute(self, query: str) -> list[Document]:
        return self.index.search(query, SEARCH_LIMIT)


class ProcessDocument:
    def __init__(self, ocr: Ocr, indexer: Indexer, documents: DocumentRepository,
                 notifications: Queue[Notification], clock=time.time):
        self.ocr = ocr
        self.indexer = indexer
        self.documents = documents
        self.notifications = notifications
        self.clock = clock

    def execute(self, job: ProcessingJob) -> float:
        """Traite un document et renvoie le délai depuis son upload, en secondes."""
        file = self.documents.get_file(job.id)
        text = self.ocr.extract(file) if file else ""
        # Indexer avant de passer « done » : une recherche lancée dès « done » doit trouver le document.
        self.indexer.index(job.id, text)
        self.documents.mark_done(job.id)
        delay = self.clock() - job.uploaded_at
        self.notifications.push(Notification(job.id, self.clock()))
        return delay


class SendNotification:
    def __init__(self, email: EmailSender, clock=time.time):
        self.email = email
        self.clock = clock

    def execute(self, notification: Notification) -> float:
        """Envoie la notification et renvoie le délai depuis sa mise en file, en secondes."""
        self.email.send(notification)
        return self.clock() - notification.enqueued_at
