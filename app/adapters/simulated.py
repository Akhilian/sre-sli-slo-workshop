"""Services externes simulés : l'OCR et le fournisseur d'e-mails."""
import random
import time


class SimulatedOcr:
    def __init__(self, sleep=time.sleep):
        self.sleep = sleep

    def extract(self, document_id):
        self.sleep(random.uniform(1, 3))


class SimulatedEmailSender:
    def __init__(self, sleep=time.sleep):
        self.sleep = sleep

    def send(self, notification):
        self.sleep(0.05)
