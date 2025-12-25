Guide d'utilisation
===================

Démarrage de l'application
---------------------------

**Avec l'exécutable** (recommandé) :

Double-cliquez sur ``PokemonAnalyzer.exe`` - tout est déjà inclus !

**Depuis le code source** (développeurs) :

.. code-block:: bash

   python src/main.py

.. important::
   **Connexion Internet requise** : L'application télécharge les données Pokémon
   depuis PokéAPI au démarrage et lors de la recherche de nouveaux Pokémon.

Interface principale
--------------------

L'application comporte deux onglets principaux :

1. **Capture Live** : Détection automatique en temps réel
2. **Recherche** : Recherche manuelle de Pokémon

Onglet Capture Live
-------------------

Sélection de la zone d'écran
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Cliquez sur **"Sélectionner Zone"**
2. Une fenêtre transparente apparaît
3. Cliquez et glissez pour délimiter la zone contenant le nom du Pokémon
4. Relâchez pour valider
5. La capture démarre automatiquement

.. tip::
   Sauvegardez votre zone avec **"Sauvegarder Configuration"** pour la réutiliser
   plus tard avec **"Charger Configuration"**.

Configuration de la capture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Intervalle** : Temps entre chaque capture (en secondes)
* **Sensibilité** : Nombre de détections consécutives nécessaires
* **Confiance** : Seuil de confiance minimal pour valider une détection (0-1)
* **Max Pokémon** :

  * Solo (1) : Détecte un seul Pokémon
  * Duo (2) : Détecte jusqu'à 2 Pokémon
  * Trio (3) : Détecte jusqu'à 3 Pokémon

Analyse des types
^^^^^^^^^^^^^^^^^

Une fois un Pokémon détecté, l'analyse s'affiche automatiquement :

* **Faiblesses** : Types contre lesquels le Pokémon est vulnérable (×2, ×4)
* **Résistances** : Types que le Pokémon résiste (×0.5, ×0.25)
* **Immunités** : Types auxquels le Pokémon est immunisé (×0)
* **Super efficace** : Types que le Pokémon peut utiliser efficacement

Onglet Recherche
----------------

Recherche par nom
^^^^^^^^^^^^^^^^^

1. Tapez le nom d'un Pokémon dans la barre de recherche
2. Les résultats apparaissent en temps réel
3. Cliquez sur un résultat pour voir les détails

Filtres
^^^^^^^

* **Type** : Filtrez par type de Pokémon (Feu, Eau, Plante, etc.)
* **Génération** : Filtrez par génération (I à IX)

.. note::
   Vous pouvez combiner les filtres pour affiner votre recherche.

Changement de langue
--------------------

L'interface supporte 6 langues :

* 🇫🇷 Français
* 🇬🇧 English
* 🇩🇪 Deutsch
* 🇪🇸 Español
* 🇮🇹 Italiano
* 🇯🇵 日本語

Pour changer la langue :

1. Sélectionnez la langue dans le menu déroulant en haut
2. L'interface se met à jour automatiquement
3. La détection OCR utilise maintenant les noms dans la langue sélectionnée

Raccourcis clavier
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Raccourci
     - Action
   * - ``Ctrl+Q``
     - Quitter l'application
   * - ``F1``
     - Ouvrir l'aide
   * - ``Esc``
     - Annuler la sélection de zone

Résolution de problèmes
------------------------

OCR non disponible
^^^^^^^^^^^^^^^^^^

**Problème** : Le message "OCR non disponible" s'affiche.

.. note::
   Si vous utilisez l'exécutable ``PokemonAnalyzer.exe``, **ce problème ne devrait jamais se produire**
   car Tesseract OCR est déjà intégré dans l'exécutable.

**Solutions (mode développement uniquement)** :

1. Vérifiez que Tesseract est installé sur votre système
2. Vérifiez le PATH ou définissez ``TESSERACT_PATH``
3. Installez Tesseract depuis https://github.com/UB-Mannheim/tesseract/wiki
4. Redémarrez l'application

Problèmes de connexion
^^^^^^^^^^^^^^^^^^^^^^^

**Problème** : Impossible de charger les données Pokémon.

**Solutions** :

1. Vérifiez votre connexion Internet
2. PokéAPI pourrait être temporairement indisponible - réessayez plus tard
3. Vérifiez que votre pare-feu n'bloque pas l'application

Détection imprécise
^^^^^^^^^^^^^^^^^^^

**Problème** : Les Pokémon sont mal détectés.

**Solutions** :

1. Ajustez la **zone de capture** pour n'inclure que le nom
2. Augmentez la **sensibilité** (plus de détections consécutives)
3. Augmentez le **seuil de confiance**
4. Assurez-vous que la zone capturée est claire et lisible

Performance
^^^^^^^^^^^

**Problème** : L'application est lente.

**Solutions** :

1. Augmentez l'**intervalle** entre les captures
2. Réduisez la taille de la zone capturée
3. Fermez d'autres applications
