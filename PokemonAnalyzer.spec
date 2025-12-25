# -*- mode: python ; coding: utf-8 -*-
"""
Fichier .spec pour PyInstaller - Pokémon Analyzer
Compile l'application avec toutes les ressources nécessaires
"""

import os
import sys
from pathlib import Path

block_cipher = None

# Détermine le chemin de base
base_path = Path.cwd()

# Liste de tous les fichiers de données à inclure
datas = [
    # Fichiers JSON essentiels pour l'API
    ('src/infrastructure/api/pokemon_names.json', 'infrastructure/api'),
    ('src/infrastructure/api/type_translations.json', 'infrastructure/api'),

    # Assets (logo, icônes, styles)
    ('src/assets/logo.png', 'assets'),
    ('src/assets/search.svg', 'assets'),
    ('src/assets/styles.qss', 'assets'),

    # Icônes des types Pokémon
    ('src/assets/types', 'assets/types'),

    # Tesseract-OCR - Données linguistiques
    ('build/tesseract/tessdata', 'tesseract/tessdata'),
]

# Binaires Tesseract à inclure
binaries = [
    ('build/tesseract/tesseract.exe', 'tesseract'),
]

# Ajoute toutes les DLLs de Tesseract
import glob
for dll in glob.glob('build/tesseract/*.dll'):
    binaries.append((dll, 'tesseract'))

# Imports cachés nécessaires
hiddenimports = [
    'pytesseract',
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageGrab',
    'cv2',
    'numpy',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'requests',
    'urllib3',
    'json',
    'pathlib',
    'tkinter',
    'tkinter.ttk',
]

# Analyse des dépendances
a = Analysis(
    ['src/main.py'],
    pathex=[str(base_path)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['build/hook-tesseract.py'],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Fichiers Python compilés
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Configuration de l'exécutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PokemonAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console (interface graphique seulement)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/logo.png' if os.path.exists('src/assets/logo.png') else None,
)
