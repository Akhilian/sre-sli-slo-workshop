## Context

L'application, le déploiement par équipe, les SLO et les dashboards existent. Il manque le trafic qui fait vivre les SLI, et la preuve que chaque panne raconte la bonne histoire dans le temps imparti. Les débits et seuils ont été calibrés dans les changes précédents (capacité du worker ~2 jobs/s, budget 0.5 %, fenêtres Sloth par défaut).

## Goals / Non-Goals

**Goals:**
- Un trafic stable, indépendant de la latence du serveur, présent dès l'installation.
- Une recherche dont le résultat vide signale toujours un défaut de qualité, et rien d'autre.
- Un animateur autonome grâce au README.

**Non-Goals:**
- Tests de charge ou de performance.
- Déclenchement automatique des pannes (elles restent manuelles, c'est le moment fort de la séance).
- Exploitation des métriques k6.

## Decisions

**Job plutôt que k6-operator.** Un `Job` avec l'image officielle `grafana/k6` et le script monté par ConfigMap ; `backoffLimit` faible, `activeDeadlineSeconds` de 3 h. Pas de CRD supplémentaire à installer sur chaque cible.
Alternative écartée : k6-operator. Utile pour le distribué, inutile à 5 requêtes/s.

**Trois scénarios `constant-arrival-rate`.** `uploads`, `consultations`, `recherches`, chacun avec son débit et un `preAllocatedVUs` suffisant pour absorber 2 s de latence (débit × durée max + marge). Un modèle à VU constants ferait baisser le débit quand la latence monte et fausserait les ratios.

**Partage d'état entre scénarios.** Les VU k6 ne partagent pas de mémoire. Le scénario `consultations` n'a donc pas accès aux `id` du scénario `uploads`. Solution retenue : chaque itération d'upload enchaîne elle-même le suivi de son document — upload, puis consultations espacées (`GET /documents/{id}` toutes les 2 s, au plus 60 s), puis une recherche du jeton dès que le statut est `done`. Les débits de consultation et de recherche résultent de ce parcours ; un scénario séparé complète les consultations jusqu'à ~2/s sur des `id` récents connus du VU.
Alternative écartée : stocker les `id` dans Redis côté k6. Ajoute un couplage entre l'outil de trafic et l'application.
Conséquence : sous `worker_slow`, un document qui n'est pas `done` dans les 60 s n'est pas recherché ; la qualité reste donc intacte, comme attendu.

**Jeton.** `doc-` suivi de 8 caractères aléatoires `[a-z0-9]`, indexé tel quel grâce à la configuration `simple` du `tsvector`.

**Pas d'export des métriques k6.** Sortie par défaut uniquement (logs du Job). Cohérent avec la règle « aucune métrique côté client ».

**README.** Structure : prérequis par cible → installation → accès des équipes → déroulé de séance → fiches pannes → remise à zéro → résultats de vérification (tableau des temps mesurés, daté).

## Risks / Trade-offs

- [Débits réels de consultation et de recherche différents des valeurs indicatives] → mesurés pendant la vérification et ajustés dans les valeurs du chart.
- [Job k6 terminé avant la fin de la séance] → durée de 3 h et relance documentée (`kubectl delete job` + `helm upgrade`).
- [Bruit statistique sur `notifier_drop=0.2` à ~1 notification/s] → fenêtre de 5 min suffisante (~300 événements) ; à confirmer pendant la vérification.

## Open Questions

- Faut-il un mode « répétition » du chart avec des débits doublés pour vérifier les pannes plus vite ?
