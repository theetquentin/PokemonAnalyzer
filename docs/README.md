# Documentation Pokémon Analyzer

Cette documentation est générée avec [Sphinx](https://www.sphinx-doc.org/).

## 🔧 Prérequis

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

## 📚 Génération de la documentation

### Windows

```bash
# Générer la documentation HTML
cd docs
make.bat html

# Nettoyer les builds précédents
make.bat clean
```

### Linux/macOS

```bash
# Générer la documentation HTML
cd docs
make html

# Nettoyer les builds précédents
make clean
```

## 👀 Consulter la documentation

Après la génération, ouvrez `docs/_build/html/index.html` dans votre navigateur.

## 📝 Style des docstrings

Cette documentation utilise le **Google Style** pour les docstrings.

### Exemple de docstring :

```python
def calculate_effectiveness(attacker_type: str, defender_types: List[str]) -> float:
    """Calculate type effectiveness for an attack.

    This function computes the damage multiplier when a Pokémon of a given type
    attacks another Pokémon with one or more types.

    Args:
        attacker_type: The type of the attacking move (e.g., "fire", "water").
        defender_types: List of the defending Pokémon's types.

    Returns:
        A float representing the damage multiplier. Values can be:
        - 0.0: No effect (immune)
        - 0.25: Double resistance
        - 0.5: Resistance
        - 1.0: Normal damage
        - 2.0: Super effective
        - 4.0: Double super effective

    Raises:
        ValueError: If attacker_type or any defender_type is invalid.

    Example:
        >>> calculate_effectiveness("fire", ["grass"])
        2.0
        >>> calculate_effectiveness("water", ["fire", "rock"])
        4.0
    """
    # Implementation here
    pass
```

### Sections Google Style :

- **Args:** Arguments de la fonction
- **Returns:** Valeur de retour
- **Raises:** Exceptions levées
- **Example:** Exemples d'utilisation
- **Note:** Notes importantes
- **Warning:** Avertissements
- **See Also:** Références croisées

## 🔄 Mise à jour automatique

Pour mettre à jour la documentation après modification du code :

```bash
cd docs
make.bat clean
make.bat html
```

## 📖 Structure

```
docs/
├── conf.py              # Configuration Sphinx
├── index.rst            # Page d'accueil
├── installation.rst     # Guide d'installation
├── usage.rst            # Guide d'utilisation
├── api/                 # Référence API
│   ├── index.rst
│   ├── core.rst
│   ├── infrastructure.rst
│   ├── services.rst
│   ├── presenters.rst
│   └── ui.rst
├── _build/              # Documentation générée
│   └── html/
├── _static/             # Fichiers statiques (CSS, images)
└── _templates/          # Templates personnalisés
```

## 🎨 Thème

Cette documentation utilise le thème **Read the Docs** (`sphinx_rtd_theme`).
