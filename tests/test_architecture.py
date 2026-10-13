"""Garde-fous de l'architecture : domaine sans infrastructure, contrat des métriques."""
import pathlib
import subprocess
import sys

from prometheus_client import REGISTRY

from adapters import metrics

APP = pathlib.Path(__file__).parent.parent / "app"


def test_le_domaine_s_importe_sans_infrastructure():
    # Un module mis à None dans sys.modules fait échouer tout import qui le vise.
    script = (
        "import sys\n"
        "for name in ('fastapi', 'psycopg', 'redis', 'prometheus_client', 'uvicorn', 'pydantic'):\n"
        "    sys.modules[name] = None\n"
        "import domain.models, domain.ports, domain.services, domain.errors\n"
    )
    result = subprocess.run([sys.executable, "-c", script], cwd=APP, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


# Contrat de la spec service-metrics : les SLO Sloth et les dashboards en dépendent.
EXPECTED = {
    "http_requests": ("counter", ["route", "status"], None),
    "http_request_duration_seconds": ("histogram", ["route"], [0.1, 0.3, 1.0, 3.0]),
    "search_requests": ("counter", ["status"], None),
    "search_results_count": ("histogram", [], [0.0, 1.0, 5.0, 20.0]),
    "search_fallback": ("counter", [], None),
    "jobs_processed": ("counter", ["status"], None),
    "queue_depth": ("gauge", [], None),
    "document_processing_delay_seconds": ("histogram", [], [10.0, 60.0, 300.0, 900.0]),
    "notifications_enqueued": ("counter", [], None),
    "notifications_sent": ("counter", ["status"], None),
    "notification_delay_seconds": ("histogram", [], [1.0, 5.0, 30.0, 120.0]),
}


def test_metriques_exposees_conformes_au_contrat():
    declared = {
        value._name: value for value in vars(metrics).values()
        if hasattr(value, "_name") and hasattr(value, "_type")
    }

    assert set(declared) == set(EXPECTED)
    for name, (kind, labels, buckets) in EXPECTED.items():
        metric = declared[name]
        assert metric._type == kind, name
        assert list(metric._labelnames) == labels, name
        if buckets:
            # _upper_bounds n'existe que sur le parent ou sur un histogramme sans label.
            assert metric._upper_bounds == buckets + [float("inf")], name


def test_pas_de_series_created():
    exposed = "".join(
        sample.name + "\n" for family in REGISTRY.collect() for sample in family.samples
    )
    assert "_created" not in exposed
