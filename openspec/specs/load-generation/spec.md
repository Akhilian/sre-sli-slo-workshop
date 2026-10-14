# load-generation Specification

## Purpose
TBD - created by archiving change add-traffic-and-runbook. Update Purpose after archive.
## Requirements
### Requirement: Trafic constant par équipe
Le chart SHALL installer dans chaque namespace d'équipe un Job k6 qui cible le Service `api` du namespace, en `constant-arrival-rate`, avec par défaut 1 upload/s, environ 1,5 consultation/s (suivi du statut) et 2 recherches/s, pendant 3 h. Le débit d'upload et le nombre de recherches par document MUST être configurables par les valeurs du chart.

#### Scenario: Débit maintenu sous latence
- **WHEN** `upload_latency=2.0` est active
- **THEN** le débit d'uploads reçu par l'API reste d'environ 1/s

#### Scenario: Débit maintenu sous worker lent
- **WHEN** `worker_slow=10` est active et que chaque itération k6 attend 60 s le statut `done`
- **THEN** le débit d'uploads reste d'environ 1/s, y compris dans la première minute de la panne

#### Scenario: Trafic dès l'installation
- **WHEN** une équipe vient d'être installée
- **THEN** des requêtes apparaissent dans ses métriques en moins de 2 min, sans action de l'équipe

### Requirement: Jeton unique et recherche après traitement
Chaque upload k6 SHALL contenir un jeton unique (`doc-<identifiant court>`) en plus d'un texte tiré d'un petit corpus. k6 MUST ne rechercher le jeton d'un document qu'après avoir constaté son statut `done` via `GET /documents/{id}`.

#### Scenario: Régime nominal
- **WHEN** aucune panne n'est active
- **THEN** toutes les recherches renvoient au moins un résultat

#### Scenario: Index périmé
- **WHEN** `stale_index=1` est active
- **THEN** les recherches portant sur des documents traités pendant la panne renvoient 0 résultat avec un statut 200

#### Scenario: Worker lent
- **WHEN** `worker_slow=10` est active
- **THEN** les documents arrivent en `done` plus tard mais les recherches continuent de renvoyer au moins un résultat

### Requirement: Aucune métrique côté client exploitée
Le trafic k6 MUST NOT être utilisé comme source de SLI : ses métriques ne sont ni exportées vers Prometheus ni affichées dans les dashboards.

#### Scenario: Prometheus ne contient que les métriques serveur
- **WHEN** on cherche des séries `k6_*` dans Prometheus
- **THEN** aucune n'existe

