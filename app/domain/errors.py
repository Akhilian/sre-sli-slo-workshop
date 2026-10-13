"""Erreurs métier, traduites en réponses HTTP par les points d'entrée."""


class DocumentNotFound(Exception):
    pass


class SearchUnavailable(Exception):
    """L'index de recherche ne répond pas (base indisponible, délai dépassé)."""
