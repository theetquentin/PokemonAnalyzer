.. Pokémon Analyzer documentation master file

Bienvenue dans la documentation de Pokémon Analyzer !
======================================================

**Pokémon Analyzer** est une application de bureau qui utilise l'OCR (Reconnaissance Optique de Caractères)
pour identifier automatiquement les Pokémon affichés à l'écran et fournir une analyse des types en temps réel.

🎯 Fonctionnalités principales
-------------------------------

* **Capture en temps réel** : Détecte automatiquement les Pokémon sur votre écran
* **Analyse des types** : Calcule les faiblesses, résistances et immunités
* **Support multi-langue** : Interface disponible en FR, EN, DE, ES, IT, JP
* **Mode multi-combat** : Détection de 1 à 3 Pokémon simultanément
* **Recherche avancée** : Filtres par type et génération

🚀 Démarrage rapide
--------------------

1. Installez les dépendances :

   .. code-block:: bash

      pip install -r requirements.txt

2. Installez Tesseract OCR :

   * Windows : `Télécharger Tesseract <https://github.com/UB-Mannheim/tesseract/wiki>`_

3. Lancez l'application :

   .. code-block:: bash

      python src/main.py

📚 Table des matières
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   installation
   usage
   api/index

📖 Référence API
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

🔗 Liens utiles
----------------

* `GitHub Repository <https://github.com/>`_
* `Report Issues <https://github.com/>`_

.. note::
   Cette documentation a été générée automatiquement avec Sphinx.
