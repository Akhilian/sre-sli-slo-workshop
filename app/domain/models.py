"""Objets métier échangés entre les cas d'usage et les ports."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StoredFile:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class Document:
    """Métadonnées d'un document. Les octets du fichier ne sont chargés qu'au téléchargement."""
    id: int
    title: str
    filename: str | None
    content_type: str | None
    size: int | None
    status: str  # "pending" puis "done"
    uploaded_at: datetime
    processed_at: datetime | None = None


@dataclass(frozen=True)
class ProcessingJob:
    """Message de la file `jobs` (api -> worker)."""
    id: int
    uploaded_at: float  # horodatage Unix


@dataclass(frozen=True)
class Notification:
    """Message de la file `notifications` (worker -> notifier)."""
    id: int
    enqueued_at: float  # horodatage Unix
