"""
Script de création d'exécutable complet pour Pokémon Analyzer
Génère un exécutable Windows avec toutes les ressources incluant Tesseract-OCR
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import urllib.request
import zipfile
import tempfile

# Change le répertoire de travail à la racine du projet
script_dir = Path(__file__).parent.parent.parent
os.chdir(script_dir)

# URL de Tesseract portable pour Windows
TESSERACT_URL = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
TESSERACT_DIR = Path("build/tesseract")

# URL de UPX pour la compression
UPX_URL = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-win64.zip"
UPX_DIR = Path("build/upx")


def print_step(step, message):
    """Affiche une étape du processus"""
    print(f"\n{'='*70}")
    print(f"  [{step}] {message}")
    print('='*70)


def download_tesseract():
    """Télécharge et prépare Tesseract portable pour l'inclusion"""
    print_step("1/7", "PRÉPARATION DE TESSERACT-OCR")

    # Vérifie si Tesseract est déjà préparé
    if TESSERACT_DIR.exists() and (TESSERACT_DIR / "tesseract.exe").exists():
        print(f"[OK] Tesseract déjà préparé dans {TESSERACT_DIR}")
        return True

    print("[INFO] Recherche de Tesseract sur le système...")

    # Cherche Tesseract dans les chemins standards
    possible_paths = [
        Path(r'C:\Program Files\Tesseract-OCR'),
        Path(r'C:\Program Files (x86)\Tesseract-OCR'),
    ]

    # Ajoute le chemin depuis la variable d'environnement si elle existe
    if 'TESSERACT_PATH' in os.environ:
        tesseract_exe = Path(os.environ['TESSERACT_PATH'])
        if tesseract_exe.exists():
            possible_paths.insert(0, tesseract_exe.parent)

    tesseract_source = None
    for path in possible_paths:
        if path.exists() and (path / "tesseract.exe").exists():
            tesseract_source = path
            print(f"[OK] Tesseract trouvé : {path}")
            break

    if not tesseract_source:
        print("[ERREUR] Tesseract non trouvé sur le système")
        print("        Veuillez installer Tesseract depuis:")
        print("        https://github.com/UB-Mannheim/tesseract/wiki")
        print("        Ou définir la variable TESSERACT_PATH")
        return False

    # Crée le dossier de destination
    print(f"[INFO] Copie de Tesseract vers {TESSERACT_DIR}...")
    TESSERACT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Copie les fichiers essentiels
        essential_files = [
            "tesseract.exe",
        ]

        for file in essential_files:
            src = tesseract_source / file
            dst = TESSERACT_DIR / file
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  [OK] {file}")

        # Copie toutes les DLLs
        print("[INFO] Copie des DLLs...")
        dll_count = 0
        for dll_file in tesseract_source.glob("*.dll"):
            shutil.copy2(dll_file, TESSERACT_DIR / dll_file.name)
            dll_count += 1
        print(f"  [OK] {dll_count} DLLs copiees")

        # Copie le dossier tessdata (données linguistiques)
        tessdata_src = tesseract_source / "tessdata"
        tessdata_dst = TESSERACT_DIR / "tessdata"

        if tessdata_src.exists():
            # Copie UNIQUEMENT les données linguistiques nécessaires (optimisation taille)
            print("[INFO] Copie des données linguistiques (tessdata)...")
            
            # Liste des langues à conserver
            langs_to_keep = ["eng", "fra", "jpn"] # Japonais ajouté
            
            if not tessdata_dst.exists():
                tessdata_dst.mkdir(parents=True)
                
            copied_count = 0
            for lang in langs_to_keep:
                # Cherche tous les fichiers commençant par le code langue
                # ex: fra.traineddata, fra.user-patterns, etc.
                for src_file in tessdata_src.glob(f"{lang}*"):
                    shutil.copy2(src_file, tessdata_dst / src_file.name)
                    copied_count += 1
            
            print(f"  [OK] {copied_count} fichiers de langues copies (Filtre: {langs_to_keep})")
        else:
            print("[WARN] Dossier tessdata non trouvé")

        print(f"[OK] Tesseract préparé dans {TESSERACT_DIR}")

        # Affiche la taille totale
        total_size = sum(f.stat().st_size for f in TESSERACT_DIR.rglob("*") if f.is_file())
        print(f"[INFO] Taille totale : {total_size / (1024*1024):.1f} MB")

        return True

    except Exception as e:
        print(f"[ERREUR] Erreur lors de la copie : {e}")
        return False


def download_upx():
    """Télécharge et installe UPX pour la compression"""
    print_step("X/7", "PRÉPARATION DE UPX (COMPRESSION)")
    
    if UPX_DIR.exists() and (UPX_DIR / "upx.exe").exists():
        print(f"[OK] UPX déjà présent dans {UPX_DIR}")
        return True
        
    print(f"[INFO] Téléchargement de UPX depuis {UPX_URL}...")
    try:
        # Téléchargement
        zip_path = Path("build/upx.zip")
        UPX_DIR.parent.mkdir(parents=True, exist_ok=True)
        
        # User-Agent pour éviter 403 Forbidden sur GitHub
        req = urllib.request.Request(
            UPX_URL, 
            data=None, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
        print("[INFO] Extraction de UPX...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Cherche le dossier interne
            upx_exe_path = None
            for file in zip_ref.namelist():
                if file.endswith("upx.exe"):
                    upx_exe_path = file
                    break
                    
            if upx_exe_path:
                UPX_DIR.mkdir(exist_ok=True)
                with zip_ref.open(upx_exe_path) as source, open(UPX_DIR / "upx.exe", "wb") as target:
                    shutil.copyfileobj(source, target)
                print(f"[OK] UPX extrait vers {UPX_DIR}")
                
        # Nettoyage
        if zip_path.exists():
            os.remove(zip_path)
            
        return True
        
    except Exception as e:
        print(f"[ERREUR] Impossible de télécharger UPX: {e}")
        print("         La compression sera désactivée.")
        return True # On continue même sans UPX, c'est optionnel pour le build
            

def check_dependencies():
    """Vérifie que les dépendances (PySide6-Essentials) sont installées"""
    print_step("0/7", "VÉRIFICATION DES DÉPENDANCES")
    
    try:
        import PySide6
        print(f"[OK] PySide6 détecté : {PySide6.__version__}")
        print(f"     Chemin : {os.path.dirname(PySide6.__file__)}")
        
        # Vérification optionnelle pour voir si c'est Essentials
        # (Difficile à vérifier programmatiquement de manière fiable sans pip, 
        #  mais on suppose que l'utilisateur a suivi les instructions)
        return True
    except ImportError:
        print("[ERREUR] PySide6 n'est pas installé.")
        print("         Veuillez installer PySide6-Essentials :")
        print("         pip install PySide6-Essentials>=6.5.0")
        return False

def check_pyinstaller():
    """Vérifie et installe PyInstaller si nécessaire"""
    print_step("2/7", "VÉRIFICATION DE PYINSTALLER")

    try:
        import PyInstaller
        print("[OK] PyInstaller déjà installé")
        return True
    except ImportError:
        print("[INFO] Installation de PyInstaller...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                check=True,
                capture_output=True
            )
            print("[OK] PyInstaller installé avec succès")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERREUR] Erreur lors de l'installation : {e}")
            return False


def create_spec_file():
    """Crée le fichier .spec optimisé pour PyInstaller"""
    print_step("3/7", "CRÉATION DU FICHIER SPEC")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
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
'''

    with open('PokemonAnalyzer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("[OK] Fichier PokemonAnalyzer.spec créé")
    return True


def create_runtime_hook():
    """Crée le runtime hook pour configurer Tesseract au démarrage"""
    print_step("4/7", "CRÉATION DU RUNTIME HOOK TESSERACT")

    hook_content = '''# -*- coding: utf-8 -*-
"""
Runtime hook pour configurer Tesseract au démarrage de l'application
Ce script s'exécute avant le code principal quand l'application est lancée
"""
import os
import sys
from pathlib import Path

# Détecte si on est dans un bundle PyInstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Mode exécutable PyInstaller
    bundle_dir = Path(sys._MEIPASS)
    tesseract_path = bundle_dir / 'tesseract' / 'tesseract.exe'
    tessdata_dir = bundle_dir / 'tesseract' / 'tessdata'

    # Configure les variables d'environnement pour Tesseract
    if tesseract_path.exists():
        os.environ['TESSERACT_CMD'] = str(tesseract_path)
        print(f"[Runtime Hook] Tesseract configuré : {tesseract_path}")

    if tessdata_dir.exists():
        os.environ['TESSDATA_PREFIX'] = str(tessdata_dir)
        print(f"[Runtime Hook] TESSDATA_PREFIX configuré : {tessdata_dir}")
'''

    hook_path = Path("build/hook-tesseract.py")
    hook_path.parent.mkdir(parents=True, exist_ok=True)

    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    print(f"[OK] Runtime hook créé : {hook_path}")
    return True


def build_with_pyinstaller():
    """Construit l'exécutable avec PyInstaller"""
    print_step("5/7", "CONSTRUCTION DE L'EXÉCUTABLE (ONE-FILE)")

    print("[INFO] Lancement de PyInstaller...")
    print("[INFO] Cela peut prendre 5-10 minutes (one-file)...\n")

    try:
        # Essaye d'abord avec la commande pyinstaller
        # Construit la commande de base
        cmd = ['pyinstaller', 'PokemonAnalyzer.spec', '--clean', '--noconfirm', '--distpath=dist/pyinstaller']
        
        # Ajoute UPX si présent
        if (UPX_DIR / "upx.exe").exists():
            print(f"[INFO] Utilisation de UPX pour la compression (Chemin: {UPX_DIR})")
            cmd.append(f'--upx-dir={UPX_DIR.absolute()}')
        else:
            print("[WARN] UPX non trouvé, pas de compression")

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False  # Affiche la sortie en temps réel
        )
        print("\n[OK] Compilation réussie !")
        return True
    except FileNotFoundError:
        print("\n[WARN] Commande 'pyinstaller' non trouvée")
        print("       Tentative avec 'python -m PyInstaller'...\n")
        try:
            cmd = [sys.executable, '-m', 'PyInstaller', 'PokemonAnalyzer.spec', '--clean', '--noconfirm', '--distpath=dist/pyinstaller']
            if (UPX_DIR / "upx.exe").exists():
                cmd.append(f'--upx-dir={UPX_DIR.absolute()}')
                
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=False
            )
            print("\n[OK] Compilation réussie !")
            return True
        except Exception as e:
            print(f"\n[ERREUR] PyInstaller ne semble pas installé correctement")
            print(f"         Détails : {e}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n[ERREUR] Erreur lors de la compilation : {e}")
        return False
    except Exception as e:
        print(f"\n[ERREUR] Erreur inattendue : {e}")
        return False


def organize_distribution():
    """Vérifie l'exécutable one-file"""
    print_step("6/7", "VÉRIFICATION DE L'EXÉCUTABLE")

    exe_path = Path('dist/pyinstaller/PokemonAnalyzer.exe')

    if not exe_path.exists():
        print("[ERREUR] L'exécutable n'a pas été trouvé")
        return False

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Exécutable créé : {exe_path}")
    print(f"[INFO] Taille : {size_mb:.1f} MB")

    # Crée un fichier README simple dans le dossier dist/pyinstaller
    simple_readme = """# Pokémon Analyzer - Analyseur de Pokémon

## 🚀 Lancement

Double-cliquez sur **PokemonAnalyzer.exe**

✅ **Tout est inclus !** Aucune installation nécessaire.

## ⚠️ Prérequis

**Connexion Internet** : Nécessaire pour télécharger les données Pokémon depuis PokéAPI.

## 📦 Ce qui est inclus

Cet exécutable contient TOUTES les dépendances nécessaires :
- ✅ Tesseract OCR (reconnaissance de texte)
- ✅ Bibliothèques Python (PySide6, OpenCV, Pillow, etc.)
- ✅ Icônes des types Pokémon
- ✅ Interface graphique complète

**Taille** : ~163 MB (un seul fichier autonome)

## 🎯 Utilisation

### Capture en Temps Réel
1. Allez dans l'onglet "Capture Live"
2. Cliquez sur "Sélectionner Zone"
3. Tracez une zone d'écran à analyser
4. Cliquez sur "Démarrer"
5. L'analyse apparaît automatiquement !

### Recherche Manuelle
1. Onglet "Recherche"
2. Tapez le nom d'un Pokémon
3. Double-cliquez pour l'analyser

### Modes Multi-Pokémon
- **Solo** : Analyse 1 Pokémon
- **Duo** : Analyse 2 Pokémon simultanément
- **Trio** : Analyse 3 Pokémon simultanément

## 📝 Notes

- **Première utilisation** : Le téléchargement des données Pokémon peut prendre quelques secondes
- **Capture d'écran** : Fonctionne sur n'importe quelle fenêtre (émulateur, jeu, navigateur...)
- **Types supportés** : Tous les types des Générations 1 à 9

---

**Version** : 1.0
**Pokémon** est une marque de Nintendo/Game Freak/The Pokémon Company
Ce projet n'est pas affilié à Nintendo.
"""

    readme_path = Path('dist/pyinstaller/LISEZ-MOI.txt')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(simple_readme)

    print(f"[INFO] README créé : {readme_path}")
    print("\n[OK] Vérification terminée")
    return True


def show_summary():
    """Affiche le résumé"""
    print_step("7/7", "RÉSUMÉ")

    exe_path = Path('dist/pyinstaller/PokemonAnalyzer.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[INFO] Exécutable : {exe_path.absolute()}")
        print(f"[INFO] Taille : {size_mb:.1f} MB")
        print(f"[INFO] Format : ONE-FILE (1 seul fichier)")
        return True
    return False




def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print(" "*10 + "CRÉATION DE L'EXÉCUTABLE POKEMON ANALYZER")
    print("="*70)

    # Vérifications préliminaires
    if not Path('src/main.py').exists():
        print("\n[ERREUR] src/main.py non trouvé")
        print("         Assurez-vous d'être dans le dossier racine du projet")
        return

    if not Path('src/assets').exists():
        print("\n[ERREUR] dossier 'src/assets' non trouvé")
        print("         Le dossier src/assets/ est nécessaire pour l'exécutable")
        return

    # Étapes de construction
    steps = [
        ("Vérification des dépendances", check_dependencies),
        ("Préparation de Tesseract", download_tesseract),
        ("Préparation de UPX", download_upx),
        ("Vérification de PyInstaller", check_pyinstaller),
        ("Création du fichier spec", create_spec_file),
        ("Création du runtime hook", create_runtime_hook),
        ("Construction de l'exécutable", build_with_pyinstaller),
        ("Vérification", organize_distribution),
        ("Résumé", show_summary),
    ]

    for step_name, step_func in steps:
        try:
            if not step_func():
                print(f"\n[ERREUR] Échec : {step_name}")
                print("         Consultez les messages d'erreur ci-dessus")
                return
        except Exception as e:
            print(f"\n[ERREUR] Erreur inattendue lors de '{step_name}' : {e}")
            import traceback
            traceback.print_exc()
            return

    # Résumé final
    print("\n" + "="*70)
    print(" "*15 + "COMPILATION PYINSTALLER TERMINÉE !")
    print("="*70)
    print(f"\n[INFO] Exécutable : dist/pyinstaller/PokemonAnalyzer.exe")
    print("[INFO] Format : ONE-FILE")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Construction annulée par l'utilisateur")
    except Exception as e:
        print(f"\n[ERREUR] Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
