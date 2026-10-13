# Architecture de DocShare

Système fictif de partage de documents, support d'un workshop SLI / SLO de 2 h. Les participants partent d'un SLI fonctionnel, l'implémentent en SLO avec Sloth, puis regardent le budget d'erreur brûler pendant de vraies pannes.

## Architecture

Une seule image, trois rôles choisis par la variable `ROLE` (plus `standalone`, qui regroupe les trois dans un processus, voir plus bas) :

```
client ──POST /documents──▶ api ──LPUSH jobs──▶ Redis ──BRPOP──▶ worker ──LPUSH notifications──▶ Redis ──BRPOP──▶ notifier
                             │                                     │
                             └──────────── Postgres ◀──────────────┘
                               (documents + index plein texte)
```

1. `api` insère le document (statut `pending`), le met en file et répond 202.
2. `worker` simule l'OCR (1 à 3 s), indexe le document, le passe en `done` et demande une notification.
3. `notifier` « envoie » la notification (simulé).

Dans le code, architecture hexagonale (ports et adaptateurs) :

```
app/
  domain/        modèles, ports (Protocol) et cas d'usage ; ni FastAPI, ni Redis, ni Postgres, ni métriques
  adapters/      postgres.py, redis.py, memory.py, simulated.py (OCR, e-mail),
                 faults.py (les pannes), metrics.py (toutes les métriques)
  entrypoints/   http.py (FastAPI), worker.py, notifier.py, standalone.py
  bootstrap.py   câblage : adaptateurs du rôle, pannes posées sur les ports, cas d'usage
  main.py        ROLE -> bootstrap
```

Pour savoir ce qui est mesuré, lisez `app/adapters/metrics.py`. Pour savoir comment une panne agit, lisez `app/adapters/faults.py` : chaque panne y est un décorateur posé sur un port, le code métier n'en sait rien.

## Interface web

`web/` contient l'interface Vue 3/Vite et ses tests. Elle est séparée de l'image Python construite par le `Dockerfile` à la racine ; son intégration à l'image et au chart est suivie dans le changement OpenSpec `add-web-ui`.

## Déploiement et observabilité

`deploy/helm/docshare/` contient le chart d'une équipe, y compris son Job k6. `deploy/environments/{local,eks}/` porte les valeurs spécifiques aux cibles ; `deploy/scripts/` installe et supprime les piles. Les définitions SLO et solutions d'atelier, ainsi que les dashboards et leur générateur, sont regroupés sous `observability/`.
