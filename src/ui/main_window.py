"""
Fenêtre principale de l'application
Coordonne tous les onglets (Passive View)
"""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QComboBox
from PySide6.QtCore import Qt
import sys
from pathlib import Path

from ui.tabs.live_capture_tab import LiveCaptureTab
from ui.tabs.search_tab import SearchTab
from core.translations import t

# Import de la fonction utilitaire pour les chemins
try:
    from core.utils import get_resource_path
except ImportError:
    # Fallback si l'import échoue
    def get_resource_path(relative_path):
        try:
            base_path = Path(sys._MEIPASS)
        except AttributeError:
            base_path = Path(__file__).parent.parent
        return base_path / relative_path

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t('app_title'))
        self.setGeometry(100, 100, 1400, 900)

        # Configuration du logo
        self._setup_logo()
        
        # Initialise l'interface
        self._init_ui()
        
    def _setup_logo(self):
        """Configure le logo de l'application"""
        try:
            from PySide6.QtGui import QIcon, QPixmap
            from PySide6.QtCore import QSize
            # Utilise get_resource_path pour fonctionner en dev et avec PyInstaller
            logo_path = get_resource_path('assets/logo.png')
            if logo_path.exists():
                icon = QIcon(str(logo_path))
                pixmap = QPixmap(str(logo_path))
                icon.addPixmap(pixmap.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon.addPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon.addPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon.addPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.setWindowIcon(icon)
            else:
                print(f"Logo non trouve a: {logo_path}")
        except Exception as e:
            print(f"Impossible de charger le logo: {e}")
            
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header avec sélecteur de langue
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Français", "English", "Deutsch", "Español", "Italiano", "日本語"])
        self.lang_combo.setFixedWidth(120)

        # TODO: Connecter le changement de langue
        
        header_layout.addWidget(self.lang_combo)
        main_layout.addLayout(header_layout)
        
        # Onglets
        self.tabs = QTabWidget()
        
        # Style Windows - tabs collés à la page
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #F0F0F0;
                margin: 0px;
                padding: 0px;
                border-radius: 0px;
            }
            QTabBar {
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                color: #333333;
                padding: 10px 40px;
                margin-right: 1px;
                margin-bottom: 0px;
                border: none;
                min-width: 80px;
                min-height: 20px;
            }
            QTabBar::tab:selected {
                background-color: #F0F0F0;
                color: #000000;
                font-weight: normal;
            }
            QTabBar::tab:hover:!selected {
                background-color: #DADADA;
            }
        """)
        
        main_layout.addWidget(self.tabs)

        # Crée les onglets
        self.live_capture_tab = LiveCaptureTab()
        self.tabs.addTab(self.live_capture_tab, t('tab_capture'))

        self.search_tab = SearchTab()
        self.tabs.addTab(self.search_tab, t('tab_search'))
        
    def show_status_message(self, message, timeout=0):
        """Affiche un message dans la barre de statut"""
        self.statusBar().showMessage(message, timeout)
        
    def switch_to_tab(self, index):
        """Change l'onglet actif"""
        self.tabs.setCurrentIndex(index)
    
    def update_translations(self):
        """Met à jour tous les textes traduits de l'interface"""
        self.setWindowTitle(t('app_title'))
        self.tabs.setTabText(0, t('tab_capture'))
        self.tabs.setTabText(1, t('tab_search'))
        
        # Demande aux onglets de se mettre à jour
        if hasattr(self.live_capture_tab, 'update_translations'):
            self.live_capture_tab.update_translations()
        if hasattr(self.search_tab, 'update_translations'):
            self.search_tab.update_translations()
