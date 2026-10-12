## ADDED Requirements

### Requirement: Image unique multi-arch
Le projet SHALL produire une seule image Docker pour les trois rôles, construite pour `linux/amd64` et `linux/arm64`.

#### Scenario: Exécution sur une machine arm64
- **WHEN** l'image est tirée sur un Mac Apple Silicon ou un nœud Graviton
- **THEN** elle démarre sans émulation

### Requirement: Publication sur un registre public
L'image SHALL être publiée sur `ghcr.io` par un workflow GitHub Actions, pour être tirée depuis GKE, EKS ou k3d sans registre propre au fournisseur.

#### Scenario: Publication sur la branche principale
- **WHEN** un commit modifiant `app/` ou le `Dockerfile` arrive sur `main`
- **THEN** une image taguée par le SHA du commit et `latest` est disponible sur `ghcr.io`
