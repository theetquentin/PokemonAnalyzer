"""
Utilitaires pour l'application Pokémon Analyzer
"""
import sys
import os
from pathlib import Path


def get_resource_path(relative_path):
    """
    Obtient le chemin absolu vers une ressource, fonctionne en dev et avec PyInstaller

    Args:
        relative_path: Chemin relatif depuis src/ (ex: 'infrastructure/api/pokemon_names.json')

    Returns:
        Path absolu vers la ressource
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # En mode développement, utilise le chemin du dossier src
        base_path = Path(__file__).parent.parent

    return base_path / relative_path
