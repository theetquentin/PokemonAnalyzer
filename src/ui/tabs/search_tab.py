"""
Onglet de recherche de Pokémon
Permet de rechercher et filtrer les Pokémon par nom, type, génération
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QComboBox, QListWidget, QListWidgetItem, QFrame, QWidget, QGridLayout
)
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtGui import QFont, QIcon

from .base_tab import BaseTab
from core.translations import t, translate_type
import os

class SearchTab(BaseTab):
    """Onglet de recherche de Pokémon (Passive View)"""
    
    # Signal émis quand un Pokémon est sélectionné
    pokemon_selected = Signal(str)
    # Signal émis pour déclencher une recherche (après debounce)
    search_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Timer pour debounce (300ms)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)  # 300ms delay
        self.search_timer.timeout.connect(self._emit_search_request)
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # Reduced spacing
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Grid Layout for Search + Filters
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar with icon - custom widget for better control
        search_container = QWidget()
        search_container.setFixedHeight(32)
        search_container.setStyleSheet("background: transparent;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        # Icon label with padding
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'search.svg')
        self.icon_label = QLabel()
        self.icon_label.setObjectName("searchIcon")
        self.icon_label.setFixedWidth(32)
        self.icon_label.setFixedHeight(32)
        self.icon_label.setAlignment(Qt.AlignCenter)
        if os.path.exists(icon_path):
            search_icon = QIcon(icon_path)
            self.icon_label.setPixmap(search_icon.pixmap(16, 16))
        self.icon_label.setStyleSheet("""
            QLabel#searchIcon {
                background-color: #FFFFFF;
                border: 1px solid #D0D4DB;
                border-right: none;
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                padding-left: 8px;
            }
        """)

        # Search input
        self.txt_search = QLineEdit()
        self.txt_search.setObjectName("searchBar")
        self.txt_search.setPlaceholderText(t('search_placeholder'))
        self.txt_search.setStyleSheet("""
            QLineEdit#searchBar {
                border: 1px solid #D0D4DB;
                border-left: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 6px 12px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #2C3E50;
            }
            QLineEdit#searchBar:focus {
                border: 1px solid #3498DB;
                border-left: none;
                background-color: #FAFBFC;
            }
        """)
        self.txt_search.setMinimumHeight(32)
        self.txt_search.setMaximumHeight(32)
        self.txt_search.textChanged.connect(self._on_search_text_changed)

        # Install event filter to handle focus changes
        self.txt_search.installEventFilter(self)

        search_layout.addWidget(self.icon_label)
        search_layout.addWidget(self.txt_search)

        # Add search container to grid (Row 0, Col 0)
        grid_layout.addWidget(search_container, 0, 0)
        
        # Dropdown de résultats (hidden by default)
        self.results_dropdown = QListWidget()
        self.results_dropdown.setMaximumHeight(300)
        self.results_dropdown.setVisible(False)
        self.results_dropdown.setUniformItemSizes(True)
        self.results_dropdown.itemClicked.connect(self._on_item_selected)
        
        # Style pour la dropdown
        self.results_dropdown.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-top: none;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                background-color: white;
                font-size: 11pt;
                padding: 0px;
                margin: 0px;
                outline: none;
            }
            QListWidget::item {
                padding: 0px 12px;
                border-bottom: 1px solid #f0f0f0;
                min-height: 32px;
                border-radius: 0px;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
        """)
        
        # Add results dropdown to grid (Row 1, Col 0)
        grid_layout.addWidget(self.results_dropdown, 1, 0)
        
        # Filters Container
        filters_container = QWidget()
        filters_layout = QHBoxLayout(filters_container)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        filters_layout.setSpacing(10)
        
        # Type filter
        filters_layout.addWidget(QLabel("Type:"))
        self.combo_type = QComboBox()
        self.combo_type.setStyleSheet("QAbstractItemView::item { min-height: 24px; padding: 4px; }")
        self.combo_type.setFixedWidth(150)
        self.combo_type.setFixedHeight(32)
        self.combo_type.addItem("all", "all")
        self.type_keys = [
            'normal', 'fire', 'water', 'electric', 'grass', 'ice',
            'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug',
            'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy'
        ]
        for type_key in self.type_keys:
            self.combo_type.addItem(translate_type(type_key), type_key)
        self.combo_type.currentIndexChanged.connect(self._on_filter_changed)
        filters_layout.addWidget(self.combo_type)
        
        # Generation filter
        filters_layout.addWidget(QLabel("Gen:"))
        self.combo_gen = QComboBox()
        self.combo_gen.setStyleSheet("QAbstractItemView::item { min-height: 24px; padding: 4px; }")
        self.combo_gen.setFixedWidth(100)
        self.combo_gen.setFixedHeight(32)
        self.combo_gen.addItems(["Toutes", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        self.combo_gen.currentIndexChanged.connect(self._on_filter_changed)
        filters_layout.addWidget(self.combo_gen)
        
        # Add filters to grid (Row 0, Col 1)
        grid_layout.addWidget(filters_container, 0, 1, Qt.AlignVCenter | Qt.AlignLeft)
        
        # Column stretch: Search bar expands, Filters don't
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 0)
        
        layout.addLayout(grid_layout)
        

        layout.addStretch()  # Push everything to top
    
    def _on_search_text_changed(self):
        """Called when search text changes - restart debounce timer"""
        self.search_timer.stop()
        if self.txt_search.text().strip():
            self.search_timer.start()  # Start 300ms countdown
        else:
            self.results_dropdown.clear()
            self.results_dropdown.setVisible(False)
    
    def _on_filter_changed(self):
        """Called when filters change - trigger immediate search if text present"""
        if self.txt_search.text().strip():
            self._emit_search_request()
    
    def _emit_search_request(self):
        """Emit signal to trigger search"""
        self.search_requested.emit()
    
    def _on_item_selected(self, item):
        """Called when a result item is clicked"""
        # Extract Pokemon name from item data
        pokemon_name = item.data(256)  # UserRole = 256
        if pokemon_name:
            self.pokemon_selected.emit(pokemon_name)
            self.results_dropdown.setVisible(False)
    
    def eventFilter(self, obj, event):
        """Handle focus events for search input to update icon style"""
        from PySide6.QtCore import QEvent
        if obj == self.txt_search:
            if event.type() == QEvent.Type.FocusIn:
                self.icon_label.setStyleSheet("""
                    QLabel#searchIcon {
                        background-color: #FAFBFC;
                        border: 1px solid #3498DB;
                        border-right: none;
                        border-top-left-radius: 6px;
                        border-bottom-left-radius: 6px;
                        border-top-right-radius: 0px;
                        border-bottom-right-radius: 0px;
                        padding-left: 8px;
                    }
                """)
            elif event.type() == QEvent.Type.FocusOut:
                self.icon_label.setStyleSheet("""
                    QLabel#searchIcon {
                        background-color: #FFFFFF;
                        border: 1px solid #D0D4DB;
                        border-right: none;
                        border-top-left-radius: 6px;
                        border-bottom-left-radius: 6px;
                        border-top-right-radius: 0px;
                        border-bottom-right-radius: 0px;
                        padding-left: 8px;
                    }
                """)
        return super().eventFilter(obj, event)

    def get_search_text(self):
        """Retourne le texte de recherche"""
        return self.txt_search.text().strip().lower()

    def get_filters(self):
        """Retourne les filtres sélectionnés"""
        return {
            'type': self.combo_type.currentData(),
            'gen': self.combo_gen.currentText(),
            'text': self.get_search_text()
        }
    
    def display_results(self, matches):
        """Affiche les résultats dans la dropdown"""
        self.results_dropdown.clear()
        
        if not matches:
            self.results_dropdown.setVisible(False)
            return
        
        # Limit to first 50 results to avoid lag
        display_matches = matches[:50]
        
        for name, data in display_matches:
            # Format: "#001 Bulbasaur - Plante | Poison - Gen 1"
            translated_types = [translate_type(t) for t in data['types']]

            display_text = f"#{data['number']:03d}  {data['name'].title()}  -  {' | '.join(translated_types)}  -  Gen {data['generation']}"

            item = QListWidgetItem(display_text)
            # Store API name (English) for API calls, not the translated display name
            item.setData(256, data['api_name'])
            
            # Make font slightly larger for readability
            font = item.font()
            font.setPointSize(10)
            item.setFont(font)
            
            self.results_dropdown.addItem(item)
        
        # Show dropdown with results
        self.results_dropdown.setVisible(True)
        
        # Add note if results were limited
        if len(matches) > 50:
            note_item = QListWidgetItem(f"... et {len(matches) - 50} autres résultats")
            font = note_item.font()
            font.setItalic(True)
            font.setPointSize(9)
            note_item.setFont(font)
            note_item.setFlags(note_item.flags() & ~2)  # Disable selection
            self.results_dropdown.addItem(note_item)
            
        # Adjust height based on content
        item_count = self.results_dropdown.count()
        if item_count > 0:
            # Get actual row height from the first item if possible, otherwise default to 32
            row_height = self.results_dropdown.sizeHintForRow(0)
            if row_height < 0:
                row_height = 32
            
            # Calculate total height: items * row_height + 2px for borders
            total_height = (item_count * row_height) + 2
            self.results_dropdown.setFixedHeight(min(total_height, 300))
        else:
            self.results_dropdown.setFixedHeight(0)
    
    def update_translations(self):
        """Met à jour tous les textes traduits"""
        self.txt_search.setPlaceholderText(t('search_placeholder'))
        
        # Met à jour les types dans le combo box
        current_index = self.combo_type.currentIndex()
        self.combo_type.blockSignals(True)
        self.combo_type.clear()
        self.combo_type.addItem(t('filter_all_types') if t('filter_all_types') != 'filter_all_types' else "Tous les types", "all")
        for type_key in self.type_keys:
            self.combo_type.addItem(translate_type(type_key), type_key)
        self.combo_type.setCurrentIndex(current_index)
        self.combo_type.blockSignals(False)
