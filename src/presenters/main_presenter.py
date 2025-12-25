"""
Presenter principal de l'application
Coordonne l'initialisation et la communication entre les composants
"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from infrastructure.api.pokeapi_service import PokeAPIService
from core.type_calculator import TypeCalculator
from infrastructure.ocr.tesseract_ocr import TesseractOCR, test_ocr_setup
from services.analysis_service import AnalysisService
from services.capture_service import CaptureService

from ui.main_window import MainWindow
from presenters.capture_presenter import CapturePresenter
from presenters.search_presenter import SearchPresenter

class MainPresenter:
    """
    Presenter principal
    """
    
    def __init__(self):
        # Initialise l'application Qt
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Pokémon Analyzer")
        self.app.setOrganizationName("PokemonOCR")
        
        # Workaround pour le bug d'affichage des QSpinBox sur Windows 11 avec Qt 6.7+
        # Force le style "windowsvista" pour retrouver les boutons verticaux natifs
        if sys.platform == "win32":
            self.app.setStyle("windowsvista")
        
        # Initialise les services
        self._init_services()
        
        # Initialise la vue principale
        self.view = MainWindow()
        
        # Initialise les presenters enfants
        self._init_presenters()
        
        # Charge les styles
        self._load_styles()
        
    def _init_services(self):
        """Initialise tous les services"""
        try:
            # Core & Infrastructure
            self.db = PokeAPIService()
            self.calc = TypeCalculator()
            
            # OCR
            if test_ocr_setup():
                # Récupère les noms pour l'OCR
                pokemon_names = self.db.get_all_pokemon_names()
                self.ocr = TesseractOCR(pokemon_names)
                self.ocr_status = "OCR disponible"
            else:
                self.ocr = None
                self.ocr_status = "OCR non disponible"
                
            # Services applicatifs
            self.analysis_service = AnalysisService(self.calc)
            self.capture_service = CaptureService(self.ocr)
            
        except Exception as e:
            print(f"Erreur d'initialisation: {e}")
            sys.exit(1)
            
    def _init_presenters(self):
        """Initialise les presenters pour chaque onglet"""
        # Capture Tab
        self.capture_presenter = CapturePresenter(
            self.view.live_capture_tab,
            self.capture_service,
            self.analysis_service,
            self.db,
            self.calc
        )
        
        # Search Tab
        self.search_presenter = SearchPresenter(
            self.view.search_tab,
            self.db,
            self.calc
        )
        
        # Connecte les signaux inter-onglets
        self._connect_cross_tab_signals()
        
        # Met à jour le statut initial
        pokemon_count = len(self.db._names_db)
        self.view.show_status_message(
            f"Modules initialisés - {pokemon_count} noms disponibles - {self.ocr_status}"
        )
        
    def _connect_cross_tab_signals(self):
        """Connecte les signaux entre les onglets (via les presenters ou directement)"""
        # Quand un Pokémon est sélectionné dans la recherche, on l'affiche dans l'onglet capture
        self.view.search_tab.pokemon_selected.connect(self._on_pokemon_selected_from_search)
        
        # Connecte le changement de langue
        self.view.lang_combo.currentTextChanged.connect(self._on_language_changed)
        
    def _on_language_changed(self, text):
        """Gère le changement de langue"""
        lang_map = {
            "Français": "fr",
            "English": "en",
            "Deutsch": "de",
            "Español": "es",
            "Italiano": "it",
            "日本語": "jp"
        }
        code = lang_map.get(text, "fr")

        # Met à jour la langue dans le système de traduction
        from core.translations import set_language
        set_language(code)

        # Met à jour la langue dans l'API
        self.db.set_language(code)

        # Met à jour les noms de Pokémon dans l'OCR pour la nouvelle langue
        if self.ocr:
            pokemon_names = self.db.get_all_pokemon_names()
            self.ocr.update_pokemon_names(pokemon_names)

        # Rafraîchit l'interface
        self.view.update_translations()

        # Rafraîchit les résultats de recherche si nécessaire
        if self.search_presenter:
            self.search_presenter.refresh_results()

        # Rafraîchit l'affichage du/des Pokémon actuellement visible(s)
        if self.capture_presenter:
            self.capture_presenter.refresh_current_display()

        # Met à jour le statut
        from core.translations import t
        self.view.show_status_message(t('status_language_changed') + f": {text}")
        
    def _on_pokemon_selected_from_search(self, pokemon_name):
        """Gère la sélection depuis la recherche"""
        # Bascule vers l'onglet capture
        self.view.switch_to_tab(0) # 0 = Capture Tab
        
        # Simule une détection pour l'afficher
        # On utilise le presenter de capture pour ça
        # Note: On triche un peu en créant un résultat fictif
        pokemon_data = self.db.get_pokemon_by_name(pokemon_name)
        if pokemon_data:
            # Appelle directement la méthode de gestion du presenter capture
            self.capture_presenter.handle_single_pokemon_detection(
                pokemon_name, 
                1.0, # Confiance 100%
                {'image': None} # Pas d'image
            )
            
    def _load_styles(self):
        """Charge les styles QSS"""
        try:
            import os
            style_path = os.path.join(os.path.dirname(__file__), '../assets/styles.qss')
            if os.path.exists(style_path):
                with open(style_path, 'r') as f:
                    self.view.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erreur chargement styles: {e}")
            
    def run(self):
        """Lance l'application"""
        self.view.show()
        sys.exit(self.app.exec_())
