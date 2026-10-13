## ADDED Requirements

### Requirement: Préparation documentée
Le guide `docs/operations/deployment.md` SHALL décrire, pour EKS et k3s local (colima) : la création du cluster de référence et ses prérequis, l'installation par `deploy/scripts/setup.sh`, la distribution des kubeconfigs, l'accès à Grafana, et le délai minimal de 15 min de trafic sain avant la séance.

#### Scenario: Préparation par un nouvel animateur
- **WHEN** une personne qui n'a pas écrit le projet suit le README sur un cluster EKS vierge
- **THEN** elle obtient 4 équipes opérationnelles et des kubeconfigs fonctionnels sans autre aide

### Requirement: Fiche par panne
Le README SHALL documenter pour chaque panne : la commande pour l'activer et la couper, le SLI qui doit se dégrader, les SLI qui doivent rester intacts, le temps de réaction attendu, et le message pédagogique associé.

#### Scenario: Fiche de `upload_error_rate`
- **WHEN** l'animateur consulte la fiche de `upload_error_rate`
- **THEN** il y trouve la séquence `0.02` (burn rate ≈ 4, aucune alerte) puis `0.5` (page en moins de 10 min) et leur justification

### Requirement: Critère de réussite vérifié
Avant la première séance, chaque panne SHALL être vérifiée sur deux équipes en parallèle : la panne déclenchée dans une seule équipe dégrade uniquement le SLI attendu, uniquement dans cette équipe, dans le temps annoncé. Les résultats (temps mesurés) MUST être consignés dans le README.

#### Scenario: Vérification de `worker_slow`
- **WHEN** `worker_slow=10` est activée dans `team-a`
- **THEN** seul le SLI de fraîcheur de `team-a` se dégrade ; disponibilité, latence et qualité de `team-a` restent nominales et `team-b` n'est pas affectée

#### Scenario: Vérification de l'alerte page
- **WHEN** `upload_error_rate=0.5` est activée dans `team-a` après 15 min de trafic sain
- **THEN** l'alerte page se déclenche en moins de 10 min et le budget restant affiché reste entre 0 et 100 %

### Requirement: Remise à zéro et déroulé
Le README SHALL expliquer comment couper toutes les pannes, comment repartir avec un budget vierge (recréer l'équipe sous un nouveau nom), et donner le déroulé de la séance de 2 h avec la règle « une seule panne active à la fois par équipe ».

#### Scenario: Entre deux pannes
- **WHEN** l'animateur passe d'une panne à la suivante
- **THEN** le README lui indique de couper la précédente et d'attendre le retour à la normale du burn rate 5 min
