"""Adaptateurs en mémoire : mode standalone et tests. Données perdues au redémarrage."""
import queue
import re
import threading
from dataclasses import replace
from datetime import datetime, timezone

from domain.models import Document

WORDS = re.compile(r"[\w-]+")


def words(text):
    """Mots en minuscules. Comme Postgres, un mot composé (doc-1a2b) compte aussi pour chacune de ses parties."""
    found = set()
    for word in WORDS.findall(text.lower()):
        found.add(word)
        found.update(part for part in word.split("-") if part)
    return found


class InMemoryDocuments:
    """Implémente DocumentRepository, Indexer et SearchIndex. Sûr entre threads."""

    def __init__(self):
        self.lock = threading.Lock()
        self.documents = {}  # id -> Document
        self.files = {}  # id -> StoredFile
        self.index_words = {}  # id -> mots indexés ; absent tant que le document n'est pas indexé
        self.next_id = 1

    def add(self, title, file):
        with self.lock:
            document = Document(self.next_id, title, file.filename, file.content_type, len(file.data),
                                "pending", datetime.now(timezone.utc))
            self.documents[document.id] = document
            self.files[document.id] = file
            self.next_id += 1
        return document

    def get(self, document_id):
        with self.lock:
            return self.documents.get(document_id)

    def get_file(self, document_id):
        with self.lock:
            return self.files.get(document_id)

    def mark_done(self, document_id):
        with self.lock:
            document = self.documents[document_id]
            self.documents[document_id] = replace(document, status="done", processed_at=datetime.now(timezone.utc))

    def index(self, document_id, text):
        with self.lock:
            self.index_words[document_id] = words(f"{self.documents[document_id].title} {text}")

    def search(self, query, limit):
        wanted = words(query)
        if not wanted:
            return []
        with self.lock:
            ids = [doc_id for doc_id, indexed in self.index_words.items() if wanted <= indexed]
            return [self.documents[doc_id] for doc_id in sorted(ids)[:limit]]


class InMemoryQueue:
    def __init__(self):
        self.messages = queue.Queue()

    def push(self, message):
        self.messages.put(message)

    def pop(self, timeout):
        try:
            return self.messages.get(timeout=timeout)
        except queue.Empty:
            return None

    def length(self):
        return self.messages.qsize()


class InMemoryFaultStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.active = {}

    def current(self):
        with self.lock:
            return dict(self.active)

    def set(self, name, value):
        with self.lock:
            if value == 0:
                self.active.pop(name, None)
            else:
                self.active[name] = float(value)
