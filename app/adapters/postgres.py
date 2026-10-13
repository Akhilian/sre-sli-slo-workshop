"""Adaptateur Postgres : dépôt de documents, indexation et recherche plein texte."""
import logging
import time

import psycopg

from domain.errors import SearchUnavailable
from domain.models import Document

log = logging.getLogger("postgres")

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id            BIGSERIAL PRIMARY KEY,
    title         TEXT NOT NULL,
    content       TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending',
    uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at  TIMESTAMPTZ,
    -- Rempli par le worker, jamais à l'INSERT : c'est ce qui rend stale_index possible.
    search_vector TSVECTOR
);
CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN (search_vector);
"""

COLUMNS = "id, title, status, uploaded_at, processed_at"


class PostgresDocuments:
    """Implémente DocumentRepository, Indexer et SearchIndex sur la table `documents`."""

    def __init__(self, url):
        self.url = url

    def connect(self, statement_timeout_ms=None):
        options = f"-c statement_timeout={statement_timeout_ms}" if statement_timeout_ms else ""
        return psycopg.connect(self.url, autocommit=True, options=options)

    def wait_until_ready(self):
        """Réessaie jusqu'à ce que Postgres réponde : aucun ordre de démarrage n'est garanti."""
        while True:
            try:
                with self.connect() as conn:
                    conn.execute("SELECT 1")
                return
            except psycopg.Error as exc:
                log.warning("Postgres indisponible, nouvel essai dans 2 s : %s", exc)
                time.sleep(2)

    def create_schema(self):
        while True:
            try:
                with self.connect() as conn:
                    conn.execute(SCHEMA)
                return
            except psycopg.Error as exc:
                # Plusieurs réplicas d'API peuvent créer le schéma en même temps.
                log.warning("Création du schéma impossible, nouvel essai dans 2 s : %s", exc)
                time.sleep(2)

    def add(self, title, content):
        with self.connect() as conn:
            row = conn.execute(
                f"INSERT INTO documents (title, content) VALUES (%s, %s) RETURNING {COLUMNS}",
                (title, content),
            ).fetchone()
        return Document(*row)

    def get(self, document_id):
        with self.connect() as conn:
            row = conn.execute(f"SELECT {COLUMNS} FROM documents WHERE id = %s", (document_id,)).fetchone()
        return Document(*row) if row else None

    def mark_done(self, document_id):
        with self.connect() as conn:
            conn.execute(
                "UPDATE documents SET status = 'done', processed_at = now() WHERE id = %s",
                (document_id,),
            )

    def index(self, document_id):
        with self.connect() as conn:
            conn.execute(
                "UPDATE documents SET search_vector = to_tsvector('simple', title || ' ' || content)"
                " WHERE id = %s",
                (document_id,),
            )

    def search(self, query, limit):
        try:
            with self.connect(statement_timeout_ms=2000) as conn:
                rows = conn.execute(
                    f"SELECT {COLUMNS} FROM documents"
                    " WHERE search_vector @@ plainto_tsquery('simple', %s) LIMIT %s",
                    (query, limit),
                ).fetchall()
        except psycopg.Error as exc:
            raise SearchUnavailable(str(exc)) from exc
        return [Document(*row) for row in rows]
