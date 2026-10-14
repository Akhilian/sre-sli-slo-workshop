## Context

Les SLO sont des `PrometheusServiceLevel` par namespace ; Sloth enregistre pour chacun `slo:sli_error:ratio_rate<fenêtre>`, `slo:error_budget:ratio` et `slo:objective:ratio`, avec les labels `namespace` et `sloth_id`. Le dashboard *Burn rate et budget* filtre sur un couple (namespace, sloth_id) choisi par variables.

## Goals / Non-Goals

**Goals:**
- Voir en un écran l'état de tous les SLO de toutes les équipes.
- Mêmes chiffres que le dashboard détaillé, pour ne jamais avoir deux vérités.

**Non-Goals:**
- Remplacer le dashboard détaillé (fenêtres 5 min et 30 min, temps avant épuisement).
- Classer les équipes entre elles.

## Decisions

**Matrice équipes × SLO plutôt qu'un panneau par SLO.** Une requête instantanée agrégée `by (namespace, sloth_id)`, mise en forme par la transformation `groupingToMatrix` de Grafana. Une ligne par équipe, une colonne par SLO, quel que soit le nombre de SLO écrits par les équipes. Les noms de colonnes perdent le préfixe `docshare-` (`renameByRegex`) pour tenir à l'écran.
Alternative écartée : un panneau *stat* répété par SLO. La grille dépendrait du nombre de SLO et serait illisible à 20.

**Burn rate sur 1 h comme indicateur principal.** C'est la fenêtre longue de l'alerte page la plus rapide ; les couleurs reprennent les seuils des alertes (6 et 14,4). La fenêtre 5 min réagit plus vite mais clignote ; elle reste dans le détail.

**Mêmes formules que le dashboard détaillé.** Burn rate = ratio d'erreur / budget ; budget restant = 1 − Σ(ratio 5 min × 15 s) / (budget × 30 j) sur `$__range`, borné à 0. Seule l'agrégation change (`by (namespace, sloth_id)` et `on (namespace, sloth_id)` pour la division).

**Lien vers le détail.** Chaque case porte un lien vers `docshare-burn-rate` avec `var-namespace` (colonne *Équipe*) et `var-slo` (`docshare-` + nom de colonne) et la plage de temps courante.

**Variable `namespace` multiple, « All » par défaut.** Respecte l'exigence « chaque dashboard a une variable `namespace` » et permet de se concentrer sur une partie des équipes.

## Risks / Trade-offs

- [Un SLO d'équipe dont le `sloth_id` ne commence pas par `docshare-` casse le lien] → les squelettes fixent le service `docshare-…` ; le nom de colonne reste lisible, seul le lien est faux.
- [Case vide (« — ») quand la requête d'erreurs ne renvoie rien] → cas déjà documenté (`or vector(0)`), visible ici d'un coup d'œil.
- [Visible par les équipes, qui voient l'état des autres] → les dashboards existants le permettent déjà ; aucune solution n'y apparaît, seulement les SLO déjà appliqués.
