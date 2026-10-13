"""Services externes simulés : l'OCR et le fournisseur d'e-mails."""
import random
import time

TEXT_EXTENSIONS = (".txt", ".md", ".csv", ".json")
# Un tsvector Postgres est limité à 1 Mo : au-delà, seul le début du texte est indexé.
MAX_TEXT_CHARS = 100_000


def is_text(file):
    return file.content_type.startswith("text/") or file.filename.lower().endswith(TEXT_EXTENSIONS)


class SimulatedOcr:
    """Prend 1 à 3 s comme un vrai OCR, mais ne lit que les fichiers texte : les autres n'ont pas de texte."""

    def __init__(self, sleep=time.sleep):
        self.sleep = sleep

    def extract(self, file):
        self.sleep(random.uniform(1, 3))
        if not is_text(file):
            return ""
        # Postgres refuse le caractère NUL dans un texte.
        return file.data.decode("utf-8", errors="replace").replace("\x00", "")[:MAX_TEXT_CHARS]


class SimulatedEmailSender:
    def __init__(self, sleep=time.sleep):
        self.sleep = sleep

    def send(self, notification):
        self.sleep(0.05)
