# Pokemon Analyzer

**Analyseur de Pokémon avec reconnaissance OCR et calcul automatique des super-efficacités.**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://pypi.org/project/PySide6/)

---

## 🚀 Installation Rapide

### Option 1 : Utiliser l'exécutable (RECOMMANDÉ - Pour utilisateurs)

1. Allez dans [**Releases**](https://github.com/VOTRE_USERNAME/PokemonAnalyzer/releases)
2. Téléchargez **PokemonAnalyzer.exe** (dernière version)
3. Double-cliquez sur l'exécutable
4. **C'est tout !** L'application démarre immédiatement.

**✅ Tout est inclus** :
- Tesseract OCR intégré (reconnaissance de texte)
- Toutes les dépendances Python
- Interface graphique complète
- Icônes des types Pokémon

**⚠️ Prérequis :**
- **Connexion Internet** : Nécessaire pour télécharger les données Pokémon depuis [PokéAPI](https://pokeapi.co/)
- Windows 10/11 (64-bit)

**Aucune installation Python ou Tesseract requise !**

---

### Option 2 : Depuis le code source (Pour développeurs)

**Pour développeurs souhaitant modifier le code :**

```bash
# Clonez le repository
git clone https://github.com/VOTRE_USERNAME/PokemonAnalyzer.git
cd PokemonAnalyzer

# Installez les dépendances Python
pip install -r src/requirements.txt

# Installez Tesseract OCR (nécessaire en mode développement)
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt install tesseract-ocr
# macOS: brew install tesseract

# Lancez l'application
python src/main.py
```

**Prérequis pour le développement :**
- Python 3.8+ ([Télécharger](https://www.python.org/downloads/))
- Tesseract OCR installé sur le système
- Connexion Internet (PokéAPI)

---

## ✨ Fonctionnalités

- 🔴 **Capture en temps réel** - Détection automatique depuis votre écran
- 🎯 **Multi-Pokémon** - Analysez jusqu'à 3 Pokémon simultanément (Solo/Duo/Trio)
- 📊 **Analyse des types** - Calcul automatique des super-efficacités
- 🔄 **Formes alternatives** - Support des Méga-évolutions, Gigamax, formes Alola...
- 🔍 **Recherche manuelle** - Base de données complète (Générations 1-9)
- 📜 **Historique** - Consultez vos analyses précédentes

---

## 📖 Documentation

La documentation complète est disponible sur :

**[📚 ReadTheDocs - Pokemon Analyzer](https://pokemonanalyzer.readthedocs.io/)**

Guides disponibles :
- [Installation et configuration](docs/installation.rst)
- [Guide d'utilisation](docs/usage.rst)
- [Référence API](docs/api/)

---

## 🎯 Utilisation

### Mode Capture en Temps Réel

1. Lancez l'application
2. Allez dans l'onglet **"Capture Live"**
3. Cliquez sur **"Sélectionner la région"** et tracez la zone à analyser
4. Cliquez sur **"Démarrer la capture"**
5. L'analyse apparaît automatiquement !

### Mode Recherche Manuelle

1. Allez dans l'onglet **"Recherche"**
2. Tapez le nom d'un Pokémon
3. Double-cliquez sur le résultat pour l'analyser

---

## 🔧 Compiler l'exécutable

**Pour développeurs** : Pour créer votre propre exécutable autonome avec **Tesseract intégré** :

### Avec PyInstaller (recommandé)
```bash
python src/scripts/create_executable.py
```

**Sortie** : `dist/pyinstaller/PokemonAnalyzer.exe` (~163 MB)

**Inclut automatiquement** :
- Tesseract OCR (binaires + données linguistiques)
- tkinter (sélection de zone)
- Icônes des types Pokémon
- Toutes les dépendances Python

### Avec Nuitka (plus léger et rapide)
```bash
python src/scripts/create_executable_nuitka.py
```

**Sortie** : `dist/nuitka/PokemonAnalyzer.exe` (30-50% plus petit que PyInstaller)

**Avantages Nuitka** :
- Exécutable plus petit
- Démarrage plus rapide
- Meilleures performances d'exécution

**Note** : Tesseract doit être installé sur le système pour compiler (il sera copié dans l'exécutable)
Une version sans Tessereact est prévu mais pour l'instant ça ne fonctionne pas.

---

## 🛠️ Technologies

- **Python 3.8+**
- **PySide6** - Interface graphique moderne
- **Tesseract OCR** - Reconnaissance de texte
- **OpenCV** - Traitement d'images
- **PokéAPI** - Base de données Pokémon
- **PyInstaller / Nuitka** - Compilation en exécutable

---

## 📁 Structure du projet

```
PokemonAnalyzer/
├── src/
│   ├── main.py              # Point d'entrée
│   ├── requirements.txt     # Dépendances Python
│   ├── core/                # Logique métier
│   ├── infrastructure/      # API et OCR
│   ├── ui/                  # Interface PySide6
│   ├── assets/              # Images et styles
│   └── scripts/             # Scripts de compilation
├── docs/                    # Documentation Sphinx
├── PokemonAnalyzer.spec     # Configuration PyInstaller
└── README.md
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Commitez vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

---

## 🐛 Rapporter un bug

Ouvrez une [issue](https://github.com/VOTRE_USERNAME/PokemonAnalyzer/issues) avec :
- Une description claire du problème
- Les étapes pour reproduire
- Votre version de Windows et Python
- Les logs d'erreur si disponibles

---

## 📜 Licence

Projet à usage **personnel et éducatif** uniquement.

**Pokémon** est une marque déposée de Nintendo / Game Freak / The Pokémon Company.

Ce projet n'est pas affilié, sponsorisé ou approuvé par Nintendo, Game Freak ou The Pokémon Company.

---

## 🙏 Remerciements

- Smirn pour l'idée de l'application et la correction de bugs
- [PokéAPI](https://pokeapi.co/) - API Pokémon complète
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Moteur de reconnaissance de texte
- [PySide6](https://pypi.org/project/PySide6/) - Framework GUI Qt

---

