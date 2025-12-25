"""
Widget de sélection de forme pour les Pokémon avec formes multiples
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QLabel
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class FormSelector(QWidget):
    """Widget pour sélectionner la forme d'un Pokémon"""

    # Signal émis quand la forme change (nom_forme, types, api_name)
    form_changed = Signal(str, list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pokemon = None
        self.forms_data = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Container pour le sélecteur de formes (caché par défaut)
        self.forms_container = QWidget()
        self.forms_container.setVisible(False)

        container_layout = QHBoxLayout(self.forms_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)
        container_layout.setSpacing(5)
        container_layout.setAlignment(Qt.AlignLeft)

        # Label
        from core.translations import TranslationManager
        current_lang = TranslationManager()._current_language
        
        form_labels = {
            'fr': 'Forme :',
            'en': 'Form:',
            'de': 'Form:',
            'es': 'Forma:',
            'it': 'Forma:',
            'jp': 'かたち :',
            'ja': 'かたち :'
        }
        
        label_text = form_labels.get(current_lang, 'Form:')
        label = QLabel(label_text)
        label_font = QFont()
        label_font.setPointSize(8)
        label.setFont(label_font)
        container_layout.addWidget(label)

        # ComboBox pour les formes
        self.combo_forms = QComboBox()
        self.combo_forms.setMinimumWidth(120)
        self.combo_forms.currentIndexChanged.connect(self._on_form_changed)
        container_layout.addWidget(self.combo_forms)
        # Removed addStretch to allow centering

        self.main_layout.addWidget(self.forms_container)

    def set_pokemon_forms(self, pokemon_name: str, forms_data: dict, emit_default=False, translated_pokemon_name=None):
        """
        Configure les formes disponibles pour un Pokémon

        Args:
            pokemon_name: Nom du Pokémon
            forms_data: Données des formes depuis pokemon_forms.py
            emit_default: Si True, émet le signal pour la forme par défaut (False par défaut)
            translated_pokemon_name: Nom traduit pour affichage
        """
        # Nettoie les anciennes formes
        self.clear_forms()

        if not forms_data or "forms" not in forms_data:
            self.forms_container.setVisible(False)
            return

        self.current_pokemon = pokemon_name
        self.forms_data = forms_data

        forms = forms_data["forms"]
        default_form = forms_data.get("default_form")

        # Bloque les signaux pendant le remplissage
        self.combo_forms.blockSignals(True)

        # Remplit le combobox
        default_index = 0
        for i, form_data in enumerate(forms):
            # Gestion des deux formats possibles (dict ou list de dicts)
            if isinstance(form_data, tuple):
                # Cas où on itère sur items() (ancien code)
                form_name, form_info = form_data
            else:
                # Cas liste de dicts (PokeAPIService)
                form_name = form_data['name']
                form_info = form_data

            # Types peuvent ne pas être présents
            types = form_info.get("types", [])

            # API name
            api_name = form_info.get("api_name", form_name)
            
            # Formatted name for display
            from core.translations import format_form_name
            display_name = format_form_name(pokemon_name, form_name, translated_pokemon_name)

            # Ajoute au combo avec les données stockées
            self.combo_forms.addItem(display_name)
            self.combo_forms.setItemData(i, {
                'form_name': form_name,
                'types': types,
                'api_name': api_name,
                'description': form_info.get('description', '')
            })

            # Tooltip avec description
            if "description" in form_info:
                self.combo_forms.setItemData(i, form_info["description"], Qt.ToolTipRole)

            # Sélectionne la forme par défaut
            if form_name == default_form:
                default_index = i

        # Sélectionne la forme par défaut
        self.combo_forms.setCurrentIndex(default_index)

        # Réactive les signaux
        self.combo_forms.blockSignals(False)

        # Affiche le container
        self.forms_container.setVisible(True)

        # Émet le signal pour la forme par défaut seulement si demandé
        if emit_default and default_form:
            # On essaie de trouver les infos de la forme par défaut
            default_types = []
            default_api_name = default_form

            for f in forms:
                name = f['name'] if isinstance(f, dict) else f
                if name == default_form:
                    if isinstance(f, dict):
                        default_types = f.get('types', [])
                        default_api_name = f.get('api_name', default_form)
                    break

            self.form_changed.emit(default_form, default_types, default_api_name)

    def clear_forms(self):
        """Nettoie toutes les formes"""
        self.combo_forms.blockSignals(True)
        self.combo_forms.clear()
        self.combo_forms.blockSignals(False)

        self.current_pokemon = None
        self.forms_data = None

    def hide_forms(self):
        """Cache le sélecteur de formes"""
        self.forms_container.setVisible(False)

    def _on_form_changed(self, index):
        """Appelé quand une forme est sélectionnée"""
        if index < 0:
            return

        form_data = self.combo_forms.itemData(index)
        if not form_data:
            return

        form_name = form_data['form_name']
        types = form_data['types']
        api_name = form_data['api_name']

        print(f"Forme selectionnee: {form_name} - Types: {types} - API: {api_name}")

        # Émet le signal
        self.form_changed.emit(form_name, types, api_name)

    def get_selected_form(self):
        """Récupère la forme actuellement sélectionnée"""
        index = self.combo_forms.currentIndex()
        if index < 0:
            return None, None

        form_data = self.combo_forms.itemData(index)
        if not form_data:
            return None, None

        return (
            form_data['form_name'],
            form_data['types']
        )
