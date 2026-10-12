"""Point d'entrée : la variable ROLE choisit le rôle du processus."""
import logging
import os
import sys

import prometheus_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

ROLES = ("api", "worker", "notifier")

# Pas de séries *_created : elles encombrent /metrics sans servir l'exercice.
prometheus_client.disable_created_metrics()


def main():
    role = os.environ.get("ROLE", "")
    if role not in ROLES:
        sys.exit(f"ROLE doit valoir {', '.join(ROLES)} (reçu : {role!r})")

    if role == "api":
        import api
        api.run()
    elif role == "worker":
        import worker
        worker.run()
    else:
        import notifier
        notifier.run()


if __name__ == "__main__":
    main()
