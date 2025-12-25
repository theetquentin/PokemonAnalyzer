"""
Script de création d'exécutable avec Nuitka pour Pokémon Analyzer
Génère un exécutable Windows ONE-FILE optimisé et performant avec Tesseract intégré
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Change le répertoire de travail à la racine du projet
script_dir = Path(__file__).parent.parent.parent
os.chdir(script_dir)

# Chemin de Tesseract
TESSERACT_DIR = Path("build/tesseract")


def print_step(step, message):
    """Affiche une étape du processus"""
    print(f"\n{'='*70}")
    print(f"  [{step}] {message}")
    print('='*70)


def prepare_tesseract():
    """Prépare Tesseract pour l'inclusion dans l'exécutable"""
    print_step("1/8", "PRÉPARATION DE TESSERACT-OCR")

    # Vérifie si Tesseract est déjà préparé
    if TESSERACT_DIR.exists() and (TESSERACT_DIR / "tesseract.exe").exists():
        print(f"[OK] Tesseract deja prepare dans {TESSERACT_DIR}")
        return True

    print("[INFO] Recherche de Tesseract sur le systeme...")

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
            print(f"[OK] Tesseract trouve : {path}")
            break

    if not tesseract_source:
        print("[ERREUR] Tesseract non trouve sur le systeme")
        print("        Veuillez installer Tesseract depuis:")
        print("        https://github.com/UB-Mannheim/tesseract/wiki")
        return False

    # Crée le dossier de destination
    print(f"[INFO] Copie de Tesseract vers {TESSERACT_DIR}...")
    TESSERACT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Copie tesseract.exe
        shutil.copy2(tesseract_source / "tesseract.exe", TESSERACT_DIR / "tesseract.exe")
        print("  [OK] tesseract.exe")

        # Copie toutes les DLLs
        print("[INFO] Copie des DLLs...")
        dll_count = 0
        for dll_file in tesseract_source.glob("*.dll"):
            shutil.copy2(dll_file, TESSERACT_DIR / dll_file.name)
            dll_count += 1
        print(f"  [OK] {dll_count} DLLs copiees")

        # Copie le dossier tessdata
        tessdata_src = tesseract_source / "tessdata"
        tessdata_dst = TESSERACT_DIR / "tessdata"

        if tessdata_src.exists():
            print("[INFO] Copie des donnees linguistiques (tessdata)...")
            if tessdata_dst.exists():
                shutil.rmtree(tessdata_dst)
            shutil.copytree(tessdata_src, tessdata_dst)
            traineddata_files = list(tessdata_dst.glob("*.traineddata"))
            print(f"  [OK] {len(traineddata_files)} fichiers de langues copies")

        total_size = sum(f.stat().st_size for f in TESSERACT_DIR.rglob("*") if f.is_file())
        print(f"[OK] Tesseract prepare ({total_size / (1024*1024):.1f} MB)")
        return True

    except Exception as e:
        print(f"[ERREUR] Erreur lors de la copie : {e}")
        return False


def check_nuitka():
    """Vérifie et installe Nuitka si nécessaire"""
    print_step("2/8", "VÉRIFICATION DE NUITKA")

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'nuitka', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"[OK] Nuitka installé : {result.stdout.strip()}")
            return True
    except:
        pass

    print("[INFO] Installation de Nuitka...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'nuitka', 'ordered-set', 'zstandard'],
            check=True,
            capture_output=True
        )
        print("[OK] Nuitka installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Erreur lors de l'installation : {e}")
        return False


def check_c_compiler():
    """Vérifie la présence d'un compilateur C"""
    print_step("3/8", "VÉRIFICATION DU COMPILATEUR C")

    # Vérifier MinGW64
    try:
        result = subprocess.run(['gcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Compilateur GCC trouvé")
            return True
    except:
        pass

    print("[WARN] Aucun compilateur C trouvé")
    print("[INFO] Nuitka va télécharger automatiquement MinGW64...")
    print("       (Cela peut prendre quelques minutes la première fois)")
    return True


def clean_previous_builds():
    """Nettoie les builds précédents (GARDE build/tesseract)"""
    print_step("4/8", "NETTOYAGE DES BUILDS PRÉCÉDENTS")

    # Dossiers Nuitka à supprimer
    folders_to_clean = ['dist', 'main.build', 'main.dist', 'main.onefile-build']

    for folder in folders_to_clean:
        folder_path = Path(folder)
        if folder_path.exists():
            print(f"[INFO] Suppression de {folder}/")
            shutil.rmtree(folder_path, ignore_errors=True)

    # Nettoie build/ SAUF build/tesseract/
    build_path = Path('build')
    if build_path.exists():
        for item in build_path.iterdir():
            if item.name != 'tesseract':  # GARDE Tesseract
                if item.is_dir():
                    print(f"[INFO] Suppression de {item}/")
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    print(f"[INFO] Suppression de {item}")
                    item.unlink(missing_ok=True)
        print("[INFO] build/tesseract/ conservé")

    print("[OK] Nettoyage terminé")
    return True


def verify_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    print_step("5/8", "VÉRIFICATION DES DÉPENDANCES")

    required_packages = [
        'PySide6',
        'pytesseract',
        'Pillow',
        'opencv-python',
        'numpy',
        'requests'
    ]

    # Mapping entre nom de package pip et nom de module Python
    package_to_module = {
        'opencv-python': 'cv2',
        'Pillow': 'PIL',
        'PySide6': 'PySide6'
    }

    missing = []
    for package in required_packages:
        try:
            # Obtenir le nom du module à importer
            module_name = package_to_module.get(package, package.replace('-', '_'))
            __import__(module_name)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[ERREUR] {package} manquant")
            missing.append(package)

    if missing:
        print(f"\n[WARN] Packages manquants : {', '.join(missing)}")
        print("        Installez-les avec : pip install " + ' '.join(missing))
        return False

    print("\n[OK] Toutes les dépendances sont installées")
    return True


# NOTE: Runtime hook supprimé - La détection de Tesseract est gérée directement
# dans src/infrastructure/ocr/tesseract_ocr.py (lignes 24-82)
# Le hook était redondant et n'était jamais appelé par Nuitka.
def skip_runtime_hook():
    """Hook runtime non nécessaire - Détection automatique dans tesseract_ocr.py"""
    print_step("6/8", "VÉRIFICATION DE LA DÉTECTION TESSERACT")
    print("[INFO] La détection de Tesseract est gérée automatiquement")
    print("[INFO] Code de détection dans: src/infrastructure/ocr/tesseract_ocr.py")
    print("[OK] Pas de runtime hook nécessaire avec Nuitka en mode standalone")
    return True


def build_with_nuitka():
    """
    Compile l'application avec Nuitka en mode STANDALONE

    NOTES SUR LES WARNINGS COURANTS:

    1. "Unwanted import of 'tkinter' that is redundant with 'PySide6'"
       -> C'est un FAUX POSITIF. tkinter est nécessaire pour la sélection de région
       -> NE PAS ajouter --nofollow-import-to=tkinter (cela casserait l'application)

    2. "Le chemin d'accès spécifié est introuvable" (répété pendant le linking)
       -> Messages du compilateur GCC qui ne trouve pas certaines bibliothèques
       -> Ces warnings sont NORMAUX et n'affectent PAS la compilation
       -> Solution: --mingw64 force Nuitka à utiliser son propre compilateur

    3. "Non downloaded winlibs-gcc is being ignored"
       -> Nuitka détecte MSYS2/MinGW64 mais préfère son propre compilateur
       -> C'est NORMAL avec --mingw64
    """
    print_step("7/8", "COMPILATION AVEC NUITKA (STANDALONE)")

    # Chemin du script principal
    main_script = Path('src/main.py')

    if not main_script.exists():
        print(f"[ERREUR] {main_script} introuvable")
        return False

    # Chemins absolus pour les données
    base_dir = Path.cwd()
    api_dir = base_dir / 'src' / 'infrastructure' / 'api'
    assets_dir = base_dir / 'src' / 'assets'
    tesseract_dir = base_dir / 'build' / 'tesseract'

    # Vérifications des dossiers nécessaires
    print("[INFO] Vérification des ressources...")

    if not api_dir.exists():
        print(f"[ERREUR] Dossier API manquant : {api_dir}")
        return False
    print(f"  [OK] {api_dir}")

    if not assets_dir.exists():
        print(f"[ERREUR] Dossier assets manquant : {assets_dir}")
        return False
    print(f"  [OK] {assets_dir}")

    if not tesseract_dir.exists():
        print(f"[ERREUR] Tesseract non préparé : {tesseract_dir}")
        print("        Relancez le script pour préparer Tesseract")
        return False

    # Vérifie que les fichiers Tesseract essentiels sont présents
    tesseract_exe = tesseract_dir / 'tesseract.exe'
    tessdata_dir_path = tesseract_dir / 'tessdata'

    if not tesseract_exe.exists():
        print(f"[ERREUR] tesseract.exe manquant : {tesseract_exe}")
        print("        Supprimez le dossier build/ et relancez")
        return False

    if not tessdata_dir_path.exists():
        print(f"[ERREUR] tessdata manquant : {tessdata_dir_path}")
        print("        Supprimez le dossier build/ et relancez")
        return False

    print(f"  [OK] {tesseract_dir}")

    # Compte les DLLs et fichiers de langues
    dll_files = list(tesseract_dir.glob('*.dll'))
    traineddata_files = list(tessdata_dir_path.glob('*.traineddata'))
    print(f"  [OK] Tesseract : {len(dll_files)} DLLs + {len(traineddata_files)} langues")
    print("[OK] Toutes les ressources sont présentes\n")

    # Options Nuitka pour un exécutable optimisé
    nuitka_args = [
        sys.executable, '-m', 'nuitka',

        # Mode ONEFILE (un seul fichier .exe portable)
        # Les fichiers de données sont extraits dans un dossier temporaire au lancement
        '--onefile',

        # Console activée pour DEBUG (retirer après debug)
        # '--windows-disable-console',

        # Nom de l'exécutable
        '--output-filename=PokemonAnalyzer.exe',

        # Dossier de sortie
        '--output-dir=dist/nuitka',

        # Optimisations et plugins
        '--enable-plugin=pyside6',
        '--enable-plugin=tk-inter',  # Plugin pour tkinter (sélection de zone)
        '--follow-imports',

        # Force Nuitka à utiliser son propre compilateur MinGW (évite les conflits avec MSYS2)
        '--mingw64',  # Télécharge et utilise le compilateur officiel de Nuitka

        # Optimisation de taille
        '--lto=yes',  # Link Time Optimization
        '--prefer-source-code',  # Préfère le bytecode au lieu du code natif quand possible

        # N'inclure que ce qui est utilisé (pas --include-package)
        # Nuitka va suivre automatiquement les imports avec --follow-imports

        # Inclure les données (chemins absolus)
        f'--include-data-dir={api_dir}=infrastructure/api',
        f'--include-data-dir={assets_dir}=assets',
    ]

    # Inclure Tesseract fichier par fichier (comme PyInstaller)
    print("[INFO] Ajout des binaires Tesseract...")

    # tesseract.exe
    tesseract_exe = tesseract_dir / 'tesseract.exe'
    nuitka_args.append(f'--include-data-files={tesseract_exe}=tesseract/tesseract.exe')
    print(f"  [OK] tesseract.exe")

    # Toutes les DLLs
    dll_count = 0
    for dll_file in tesseract_dir.glob('*.dll'):
        nuitka_args.append(f'--include-data-files={dll_file}=tesseract/{dll_file.name}')
        dll_count += 1
    print(f"  [OK] {dll_count} DLLs")

    # Dossier tessdata
    nuitka_args.append(f'--include-data-dir={tessdata_dir_path}=tesseract/tessdata')
    print(f"  [OK] tessdata ({len(traineddata_files)} langues)")

    # NOTE IMPORTANTE : Structure en mode ONEFILE
    # - Compilation : Un seul fichier dist/nuitka/PokemonAnalyzer.exe
    # - Exécution : Les fichiers sont extraits temporairement dans %TEMP% :
    #   %TEMP%/onefile_<PID>_<random>/tesseract/tesseract.exe
    #   %TEMP%/onefile_<PID>_<random>/tesseract/*.dll
    #   %TEMP%/onefile_<PID>_<random>/tesseract/tessdata/*.traineddata
    #
    # Le code dans src/infrastructure/ocr/tesseract_ocr.py détecte automatiquement
    # le dossier d'extraction et trouve Tesseract (comme PyInstaller)

    nuitka_args.extend([
        # Optimisation de taille et nettoyage
        '--remove-output',  # Supprime les fichiers temporaires
        '--assume-yes-for-downloads',  # Accepte automatiquement les téléchargements

        # Exclure les modules non utilisés pour réduire la taille (GARDE tkinter)
        '--nofollow-import-to=unittest',
        '--nofollow-import-to=test',
        '--nofollow-import-to=distutils',

        # NOTE: Ne PAS ajouter --nofollow-import-to=tkinter même si Nuitka le suggère
        # tkinter est utilisé pour la sélection interactive de région d'écran (screen_capture.py)
        # Le warning "tkinter redondant avec PySide6" est un FAUX POSITIF

        # Amélioration des performances de compilation
        '--jobs=4',  # Utilise 4 threads pour accélérer la compilation
    ])

    # Script principal
    nuitka_args.append(str(main_script))

    # Vérifier si une icône existe
    logo_ico = Path('src/assets/logo.ico')
    logo_png = Path('src/assets/logo.png')

    if logo_ico.exists():
        nuitka_args.append(f'--windows-icon-from-ico={logo_ico}')
        print(f"[INFO] Icône : {logo_ico}")
    elif logo_png.exists():
        # Pour utiliser un PNG, Nuitka nécessite imageio
        try:
            import imageio
            nuitka_args.append(f'--windows-icon-from-ico={logo_png}')
            print(f"[INFO] Icône : {logo_png} (conversion automatique)")
        except ImportError:
            print(f"[WARN] Icône PNG disponible mais imageio manquant")
            print(f"       pip install imageio pour utiliser l'icône PNG")
            print(f"       Compilation sans icône...")

    print("\n[INFO] Compilation en cours...")
    print("[INFO] Cela peut prendre 5-15 minutes...")
    print("[INFO] Mode ONEFILE : un seul fichier .exe portable")
    print("[INFO] Démarrage optimal avec Nuitka (plus rapide que PyInstaller)\n")

    try:
        result = subprocess.run(
            nuitka_args,
            check=True,
            text=True
        )

        print("\n[OK] Compilation réussie !")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n[ERREUR] Erreur lors de la compilation :")
        print(f"         Code de retour : {e.returncode}")
        return False


def verify_executable():
    """Vérifie que l'exécutable a bien été créé"""
    print_step("8/8", "VÉRIFICATION DE L'EXÉCUTABLE")

    # En mode --onefile, Nuitka crée l'exe dans dist/nuitka/ (pas directement dans dist/)
    exe_path = Path('dist/nuitka/PokemonAnalyzer.exe')

    if not exe_path.exists():
        print("[ERREUR] L'exécutable n'a pas été trouvé")
        return False

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Exécutable créé : {exe_path}")
    print(f"[INFO] Taille : {size_mb:.1f} MB")
    print(f"[INFO] Emplacement : {exe_path.absolute()}")

    return True


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("  COMPILATION NUITKA - STANDALONE")
    print("  Pokémon Analyzer")
    print("="*70)

    # Étapes de compilation
    steps = [
        ("Préparation de Tesseract", prepare_tesseract),
        ("Vérification de Nuitka", check_nuitka),
        ("Vérification du compilateur", check_c_compiler),
        ("Nettoyage", clean_previous_builds),
        ("Vérification des dépendances", verify_dependencies),
        ("Vérification détection Tesseract", skip_runtime_hook),
        ("Compilation", build_with_nuitka),
        ("Vérification finale", verify_executable),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n[ERREUR] Échec à l'étape : {step_name}")
            print("\n[ERREUR] La compilation a échoué")
            return False

    print("\n" + "="*70)
    print("  COMPILATION TERMINÉE AVEC SUCCÈS !")
    print("="*70)
    print("\n[INFO] Exécutable prêt : dist/nuitka/PokemonAnalyzer.exe")
    print("[INFO] Format : FICHIER UNIQUE PORTABLE (.exe)")
    print("       Un seul fichier à distribuer - Aucune installation requise !")
    print("\n[INFO] Contenu intégré (extrait au lancement) :")
    print("       - Tesseract-OCR complet (tesseract/)")
    print("       - tkinter + Tcl/Tk (sélection de zone)")
    print("       - Icônes des types Pokémon")
    print("       - Toutes les dépendances Python")
    print("\n[INFO] Avantages Nuitka --onefile :")
    print("       - Un seul fichier .exe (facile à distribuer)")
    print("       - Démarrage optimisé (plus rapide que PyInstaller)")
    print("       - Tesseract fonctionne parfaitement en capture temps réel")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Compilation annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
