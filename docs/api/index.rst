.. _api:

Référence API
=============

Cette section contient la documentation complète de l'API générée automatiquement
depuis les docstrings du code source.

.. note::
   Ce projet utilise les données de l'API **PokeAPI** (https://pokeapi.co/) pour récupérer
   les informations sur les Pokémon, leurs types, faiblesses et résistances.

Core
----

Ce module contient la logique métier principale de l'application.

Entities (Entités)
^^^^^^^^^^^^^^^^^^

.. automodule:: core.entities
   :members:
   :undoc-members:
   :show-inheritance:

Type Calculator (Calculateur de Types)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: core.type_calculator
   :members:
   :undoc-members:
   :show-inheritance:

Translations (Traductions)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: core.translations
   :members:
   :undoc-members:
   :show-inheritance:

Utils (Utilitaires)
^^^^^^^^^^^^^^^^^^^

.. automodule:: core.utils
   :members:
   :undoc-members:
   :show-inheritance:

Infrastructure
--------------

Ce module contient les couches d'infrastructure (API, OCR, etc.).

API
^^^

PokeAPI Service
"""""""""""""""

.. automodule:: infrastructure.api.pokeapi_service
   :members:
   :undoc-members:
   :show-inheritance:

OCR
^^^

Tesseract OCR
"""""""""""""

.. automodule:: infrastructure.ocr.tesseract_ocr
   :members:
   :undoc-members:
   :show-inheritance:

Screen Capture (Capture d'écran)
"""""""""""""""""""""""""""""""""

.. automodule:: infrastructure.ocr.screen_capture
   :members:
   :undoc-members:
   :show-inheritance:

Services
--------

Ce module contient les services applicatifs.

Analysis Service (Service d'Analyse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: services.analysis_service
   :members:
   :undoc-members:
   :show-inheritance:

Capture Service (Service de Capture)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: services.capture_service
   :members:
   :undoc-members:
   :show-inheritance:

Presenters (Présentateurs)
---------------------------

Ce module contient les présentateurs qui gèrent la logique de présentation.

Main Presenter (Présentateur Principal)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: presenters.main_presenter
   :members:
   :undoc-members:
   :show-inheritance:

UI (Interface Utilisateur)
---------------------------

Ce module contient les composants de l'interface utilisateur.

Main Window (Fenêtre Principale)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: ui.main_window
   :members:
   :undoc-members:
   :show-inheritance:
