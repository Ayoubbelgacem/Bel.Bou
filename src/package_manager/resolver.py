def resolve_dependencies(deps):
    """Résout les dépendances (version simple sans versioning avancé)."""
    # Pour l'instant, on suppose qu'il n'y a pas de conflit
    # et on retourne la liste des dépendances triées.
    # Une vraie résolution nécessiterait un graphe et des contraintes.
    resolved = []
    for name, version in deps.items():
        resolved.append((name, version))
    return resolved