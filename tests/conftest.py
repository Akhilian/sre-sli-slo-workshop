import pytest

import bootstrap
from adapters.simulated import SimulatedEmailSender, SimulatedOcr
from helpers import no_sleep


@pytest.fixture
def standalone():
    """Application complète en mémoire, sans attente simulée ; les boucles ne sont pas démarrées."""
    return bootstrap.build_standalone(ocr=SimulatedOcr(sleep=no_sleep), email=SimulatedEmailSender(sleep=no_sleep))
