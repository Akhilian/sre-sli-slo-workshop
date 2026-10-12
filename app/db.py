"""Accès Postgres : connexion avec réessais et schéma idempotent."""
import logging
import os
import time

import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://docshare:docshare@localhost:5432/docshare")

log = logging.getLogger("db")

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


def connect(statement_timeout_ms=None):
    options = f"-c statement_timeout={statement_timeout_ms}" if statement_timeout_ms else ""
    return psycopg.connect(DATABASE_URL, autocommit=True, options=options)


def wait_until_ready():
    """Réessaie jusqu'à ce que Postgres réponde : aucun ordre de démarrage n'est garanti."""
    while True:
        try:
            with connect() as conn:
                conn.execute("SELECT 1")
            return
        except psycopg.Error as exc:
            log.warning("Postgres indisponible, nouvel essai dans 2 s : %s", exc)
            time.sleep(2)


def create_schema():
    while True:
        try:
            with connect() as conn:
                conn.execute(SCHEMA)
            return
        except psycopg.Error as exc:
            # Plusieurs réplicas d'API peuvent créer le schéma en même temps.
            log.warning("Création du schéma impossible, nouvel essai dans 2 s : %s", exc)
            time.sleep(2)
