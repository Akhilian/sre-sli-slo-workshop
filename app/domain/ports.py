"""Ports : ce dont le domaine a besoin, sans dire comment c'est fait."""
from typing import Protocol, TypeVar

from domain.models import Document, Notification

Message = TypeVar("Message")


class DocumentRepository(Protocol):
    def add(self, title: str, content: str) -> Document: ...

    def get(self, document_id: int) -> Document | None: ...

    def mark_done(self, document_id: int) -> None: ...


class Indexer(Protocol):
    def index(self, document_id: int) -> None: ...


class SearchIndex(Protocol):
    def search(self, query: str, limit: int) -> list[Document]:
        """Lève SearchUnavailable si l'index ne répond pas."""
        ...


class Queue(Protocol[Message]):
    def push(self, message: Message) -> None: ...

    def pop(self, timeout: float) -> Message | None:
        """Attend un message au plus `timeout` secondes. Renvoie None si la file reste vide."""
        ...

    def length(self) -> int: ...


class Ocr(Protocol):
    def extract(self, document_id: int) -> None: ...


class EmailSender(Protocol):
    def send(self, notification: Notification) -> None: ...
