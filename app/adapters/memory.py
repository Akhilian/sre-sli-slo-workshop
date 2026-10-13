"""Adaptateurs en mémoire : mode standalone et tests. Données perdues au redémarrage."""
import queue
import re
import threading
from dataclasses import replace
from datetime import datetime, timezone

from domain.models import Document

WORDS = re.compile(r"[\w-]+")


def words(text):
    return {word.lower() for word in WORDS.findall(text)}


class InMemoryDocuments:
    """Implémente DocumentRepository, Indexer et SearchIndex. Sûr entre threads."""

    def __init__(self):
        self.lock = threading.Lock()
        self.documents = {}  # id -> Document
        self.contents = {}   # id -> texte à indexer
        self.index_words = {}  # id -> mots indexés ; absent tant que le document n'est pas indexé
        self.next_id = 1

    def add(self, title, content):
        with self.lock:
            document = Document(self.next_id, title, "pending", datetime.now(timezone.utc))
            self.documents[document.id] = document
            self.contents[document.id] = f"{title} {content}"
            self.next_id += 1
        return document

    def get(self, document_id):
        with self.lock:
            return self.documents.get(document_id)

    def mark_done(self, document_id):
        with self.lock:
            document = self.documents[document_id]
            self.documents[document_id] = replace(document, status="done", processed_at=datetime.now(timezone.utc))

    def index(self, document_id):
        with self.lock:
            self.index_words[document_id] = words(self.contents[document_id])

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
