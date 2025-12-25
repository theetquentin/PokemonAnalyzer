#!/usr/bin/env python3
"""
Point d'entrée de l'application Pokémon Analyzer
Architecture Clean Code (MVP)
"""
import sys
import os

# Configure l'encodage UTF-8 pour la console Windows
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

# Ajoute le dossier src au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from presenters.main_presenter import MainPresenter

def main():
    """Point d'entrée principal de l'application"""
    print("\n" + "="*70)
    print(" "*25 + "LANCEMENT DE POKÉOCR")
    print("="*70 + "\n")

    try:
        # Initialise le presenter principal qui gère tout le cycle de vie
        presenter = MainPresenter()

        # Lance l'application
        presenter.run()

    except Exception as e:
        print(f"\n[ERREUR] Erreur lors du lancement de l'application :\n{e}\n")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
