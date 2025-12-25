Installation
============

Option 1 : Utilisation de l'exécutable (RECOMMANDÉ)
----------------------------------------------------

**Pour utilisateurs finaux** : Aucune installation nécessaire !

L'exécutable ``PokemonAnalyzer.exe`` contient **toutes les dépendances** :

* ✅ Tesseract OCR intégré (reconnaissance de texte)
* ✅ Python et toutes les bibliothèques
* ✅ Interface graphique complète
* ✅ Icônes des types Pokémon

**Prérequis** :

* Windows 10/11 (64-bit)
* **Connexion Internet** : Nécessaire pour télécharger les données Pokémon depuis PokéAPI

**Lancement** :

1. Téléchargez ``PokemonAnalyzer.exe`` depuis les Releases
2. Double-cliquez sur l'exécutable
3. C'est tout ! L'application démarre immédiatement.

----

Option 2 : Installation depuis le code source (Développeurs)
-------------------------------------------------------------

**Pour développeurs souhaitant modifier le code** :

Prérequis
^^^^^^^^^

* Python 3.8 ou supérieur
* pip (gestionnaire de paquets Python)
* Tesseract OCR installé sur le système
* **Connexion Internet** (PokéAPI)

Installation de Python
----------------------

1. Téléchargez Python depuis `python.org <https://www.python.org/downloads/>`_
2. Lors de l'installation, cochez "Add Python to PATH"
3. Vérifiez l'installation :

   .. code-block:: bash

      python --version

Installation de Tesseract OCR
------------------------------

Windows
^^^^^^^

1. Téléchargez l'installateur depuis `GitHub <https://github.com/UB-Mannheim/tesseract/wiki>`_
2. Installez Tesseract dans ``C:\Program Files\Tesseract-OCR\``
3. Ajoutez le chemin au PATH ou définissez la variable d'environnement :

   .. code-block:: bash

      set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

macOS
^^^^^

.. code-block:: bash

   brew install tesseract

Linux (Ubuntu/Debian)
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   sudo apt-get install tesseract-ocr
   sudo apt-get install libtesseract-dev

Installation de l'application
------------------------------

1. Clonez le dépôt :

   .. code-block:: bash

      git clone https://github.com/votre-repo/pokemon-analyzer.git
      cd pokemon-analyzer

2. Installez les dépendances Python :

   .. code-block:: bash

      pip install -r requirements.txt

3. Lancez l'application :

   .. code-block:: bash

      python src/main.py

Vérification de l'installation
-------------------------------

Pour vérifier que tout fonctionne correctement :

1. Lancez l'application
2. Vous devriez voir la fenêtre principale
3. Dans la barre de statut, vérifiez que "OCR disponible" est affiché

.. note::
   Si vous voyez "OCR non disponible", vérifiez que Tesseract est bien installé
   et accessible depuis votre PATH.
