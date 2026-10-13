"""Point d'entrée : la variable ROLE choisit le rôle du processus."""
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

# api, worker et notifier forment le mode distribué (Redis + Postgres) ;
# standalone exécute les trois dans un seul processus, en mémoire.
ROLES = ("api", "worker", "notifier", "standalone")


def main():
    role = os.environ.get("ROLE", "")
    if role not in ROLES:
        sys.exit(f"ROLE doit valoir {', '.join(ROLES)} (reçu : {role!r})")

    import bootstrap
    bootstrap.run(role)


if __name__ == "__main__":
    main()
