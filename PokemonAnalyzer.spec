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
        'tkinter',
        '_tkinter',
        'tcl',
        'tk',
        'unittest',
        'pydoc',
        # Exclusions PySide6 pour réduire la taille (Gain: ~50-100 Mo)
        'PySide6.QtNetwork',
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DExtras',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DLogic',
        'PySide6.QtQuick',
        'PySide6.QtQuickWidgets',
        'PySide6.QtQuickShapes',
        'PySide6.QtQml',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtTextToSpeech',
        'PySide6.QtDesigner',
        'PySide6.QtHelp',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtCharts',
        'PySide6.QtSpatialAudio',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtLocation',
        'PySide6.QtPositioning',
        'PySide6.QtWebChannel',
        'PySide6.QtWebSockets',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# --- OPTIMISATION TAILLE AVANCÉE ---
# Exclut les DLLs volumineuses non utilisées
excluded_binaries = [
    'opencv_videoio_ffmpeg',  # Vidéo I/O (on ne traite que des images)
    'opengl32sw.dll',         # Rendu software OpenGL (lourd)
    'Qt6Quick',               # QML non utilisé
    'Qt6Qml',                 # QML non utilisé
    'Qt6Pdf',                 # PDF non utilisé
    'Qt6Network',             # Non utilisé (requests est utilisé à la place)
    'Qt6VirtualKeyboard',
    'D3Dcompiler_47.dll',     # Souvent inutile si pas de 3D complexe
    'tcl',                    # Tcl/Tk
    'tk',                     # Tcl/Tk
    # 'libicudt',             # RESTAURÉ: Requis pour le Japonais/Unicode
    
    # Exclusions Tesseract Graphiques (Probablement inutiles pour l'OCR pur)
    'libpango',               # Pango (Rendu texte)
    'libcairo',               # Cairo (Graphisme)
    'libglib',                # GLib
    'libharfbuzz',            # Harfbuzz
]

print("Analyse des binaires à exclure...")
new_binaries = []
for (name, path, typecode) in a.binaries:
    should_exclude = False
    for exclusion in excluded_binaries:
        if exclusion.lower() in name.lower():
            print(f"  [EXCLUSION] {name}")
            should_exclude = True
            break
            
    if not should_exclude:
        new_binaries.append((name, path, typecode))

a.binaries = new_binaries
# -----------------------------------

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
