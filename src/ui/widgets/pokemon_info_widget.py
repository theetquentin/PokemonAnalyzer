"""
Widget pour afficher les informations d'un Pokémon
Remplace l'affichage HTML par des widgets natifs Qt
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit, QScrollArea, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from ui.styles import TYPE_COLORS
from core.translations import translate_type, t
from ui.widgets.form_selector import FormSelector
from ui.dialogs.pokemon_details_dialog import PokemonDetailsDialog
from core.utils import get_resource_path
import os


class ResponsiveSpriteLabel(QLabel):
    """QLabel qui redimensionne son contenu (pixmap) en gardant le ratio"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setMinimumSize(60, 60)
        # Pas de maximum size fixe, s'adapte à l'espace
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

    def set_sprite(self, pixmap):
        self._pixmap = pixmap
        self._update_display()

    def resizeEvent(self, event):
        self._update_display()
        super().resizeEvent(event)

    def _update_display(self):
        if self._pixmap and not self._pixmap.isNull():
            # Redimensionne en gardant le ratio, basé sur la taille actuelle du widget
            scaled = self._pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled)
        else:
            super().setPixmap(QPixmap())
            self.setText("?" if self._pixmap is None else "")


class PokemonInfoWidget(QFrame):
    """
    Widget pour afficher les informations d'un Pokémon avec badges de types, sprite et sélecteur de forme
    """
    # Signal relayant le changement de forme (form_name, types, api_name, widget_number est ajouté par le parent)
    form_changed = Signal(str, list, str)

    def __init__(self, compact_mode=False, parent=None):
        super().__init__(parent)
        self.pokemon = None
        self.form_name = None
        self.compact_mode = compact_mode
        self.setObjectName("PokemonInfoWidget")
        
        # Style global du widget (Bordure)
        self.setStyleSheet("""
            #PokemonInfoWidget {
                background-color: #F8F9FA;
                border: 1px solid #BDC3C7;
                border-radius: 8px;
            }
        """)
        
        self._init_ui()
        self.set_compact_mode(compact_mode)
    
    def _init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)  # Centre le contenu verticalement
        
        # === SECTION FIXE (non scrollable) ===
        
        # Sprite (Responsive)
        self.sprite_label = ResponsiveSpriteLabel()
        # On définit une taille max raisonnable pour ne pas qu'il prenne toute la place si vide
        self.sprite_label.setMaximumHeight(200)
        self.sprite_label.setMinimumSize(100, 100) # Increased size
        self.sprite_label.setStyleSheet("QLabel { color: #555; }")
        
        # Configuration du sprite pour être cliquable
        self.sprite_label.setCursor(Qt.PointingHandCursor)
        self.sprite_label.installEventFilter(self)
        self.sprite_label.setToolTip(t('tooltip_click_details'))
        
        # === INFO CONTAINER (Centré mais aligné à gauche en interne) ===
        # Container global pour centrer le bloc d'infos
        info_wrapper = QWidget()
        wrapper_layout = QHBoxLayout(info_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        
        # Container interne (VBox) pour empiler les infos
        info_content = QWidget()
        info_layout = QVBoxLayout(info_content)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignLeft) # Alignement gauche des textes entre eux
        
        # Sprite (Centré par rapport à ce bloc d'infos)
        info_layout.addWidget(self.sprite_label, 0, Qt.AlignCenter)
        
        # Form Selector
        
        # Form Selector
        self.form_selector = FormSelector()
        self.form_selector.setVisible(False)
        self.form_selector.form_changed.connect(self._on_form_changed)
        info_layout.addWidget(self.form_selector)

        # En-tête (nom, numéro, génération)
        self.header_label = QLabel()
        self.header_label.setAlignment(Qt.AlignLeft)
        self.header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.header_label)
        
        # Container pour les types
        self.types_container = QWidget()
        self.types_layout = QHBoxLayout(self.types_container)
        self.types_layout.setContentsMargins(0, 0, 0, 0)
        self.types_layout.setSpacing(6)
        self.types_layout.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(self.types_container)
        self.type_badges = []
        
        # Ajout du bloc infos au wrapper avec des spacer pour le centrer
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(info_content)
        wrapper_layout.addStretch()
        
        layout.addWidget(info_wrapper)
        
        # Espace flexible pour pousser le contenu vers le haut (ou le centre selon l'alignement du layout principal)
        layout.addStretch()

    
    
    def eventFilter(self, source, event):
        """Gère les événements, notamment le clic sur le sprite"""
        if source == self.sprite_label and event.type() == event.Type.MouseButtonRelease:
            if self.pokemon: # Seulement si un Pokémon est affiché
                self.show_details()
            return True
        return super().eventFilter(source, event)
    
    def set_pokemon(self, pokemon, form_name=None):
        """Met à jour l'affichage avec les données du Pokémon"""
        self.pokemon = pokemon
        self.form_name = form_name
        
        # Nettoyage si aucun Pokémon
        if not self.pokemon:
            self.header_label.setText("")
            self._clear_types()
            return
        
        # En-tête
        header_text = f"{self.pokemon.name.upper()} #{self.pokemon.pokedex_number:03d} | Gen {self.pokemon.generation}"
        self.header_label.setText(header_text)
        
        # Types
        self._update_types()
    
    def show_details(self):
        """Ouvre la modale de détails"""
        if not self.pokemon:
            return
            
        # Get the original pixmap from the ResponsiveSpriteLabel
        current_pixmap = getattr(self.sprite_label, '_pixmap', None)
        
        dialog = PokemonDetailsDialog(self.pokemon, self, sprite_pixmap=current_pixmap)
        dialog.exec()

    def _update_types(self):
        """Met à jour les badges de types"""
        # Clear existing badges
        self._clear_types()
        
        # Clear the entire layout (including stretch)
        while self.types_layout.count():
            item = self.types_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.pokemon:
            return
        
        # Create new badges
        for type_en in self.pokemon.types:
            badge = self._create_type_badge(type_en)
            self.types_layout.addWidget(badge)
            self.type_badges.append(badge)
        
        # Add stretch at the end
        self.types_layout.addStretch()
    
    def _clear_types(self):
        """Efface les badges de types"""
        for badge in self.type_badges:
            badge.deleteLater()
        self.type_badges.clear()
    
    def _create_type_badge(self, type_en):
        """Crée un badge pour un type"""
        badge = QFrame()
        color = TYPE_COLORS.get(type_en.lower(), "#777777")
        badge.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(6, 4, 8, 4)
        badge_layout.setSpacing(6)
        
        # Icon
        icon_label = QLabel()
        icon_path = get_resource_path(f"assets/types/{type_en.lower()}.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setFixedSize(20, 20)
        
        # Text
        type_translated = translate_type(type_en)
        text_label = QLabel(type_translated.upper())
        text_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        
        badge_layout.addWidget(icon_label)
        badge_layout.addWidget(text_label)
        
        return badge
    
    def set_sprite(self, pixmap):
        """Définit le sprite affiché"""
        self.sprite_label.set_sprite(pixmap)

    def configure_form_selector(self, pokemon_name, forms_info, translated_species_name=None):
        """Configure et affiche le sélecteur de forme"""
        self.form_selector.blockSignals(True)
        
        # On utilise le nom d'espèce traduit si fourni, sinon fallback
        translated_name = translated_species_name if translated_species_name else (self.pokemon.name if self.pokemon else pokemon_name.title())
        
        self.form_selector.set_pokemon_forms(pokemon_name, forms_info, translated_pokemon_name=translated_name)
        self.form_selector.setVisible(True)
        self.form_selector.blockSignals(False)
        self.set_compact_mode(self.compact_mode) # Ajuste la taille si besoin

    def update_translations(self):
        """Met à jour les traductions"""
        # Met à jour le tooltip du sprite
        self.sprite_label.setToolTip(t('tooltip_click_details'))

        if self.pokemon:
            # Met à jour le header
            header_text = f"{self.pokemon.name.upper()} #{self.pokemon.pokedex_number:03d} | Gen {self.pokemon.generation}"
            self.header_label.setText(header_text)
            # Met à jour les types (qui seront traduits)
            self._update_types()
        
    def hide_form_selector(self):
        """Cache le sélecteur de forme"""
        self.form_selector.hide_forms()
        self.form_selector.setVisible(False)

    def _on_form_changed(self, form_name, types, api_name):
        """Relai le signal interne vers l'extérieur"""
        self.form_changed.emit(form_name, types, api_name)

    def set_compact_mode(self, enabled: bool):
        """Active ou désactive le mode compact (pour l'affichage en trio)"""
        self.compact_mode = enabled
        
        if enabled:
            # Mode compact (Trio) - Force une taille contrainte pour éviter l'étirement excessif
            self.sprite_label.setMinimumSize(80, 80)
            self.header_label.setStyleSheet("font-weight: bold; font-size: 11px; border: none;")
            self.layout().setContentsMargins(4, 4, 4, 4)
            # En trio, on veut éviter que le widget prenne toute la largeur s'il est seul
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        else:
            # Mode normal
            self.sprite_label.setMinimumSize(100, 100)
            self.header_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
            self.layout().setContentsMargins(10, 10, 10, 10)
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            
        # Force la mise à jour de la géométrie
        self.updateGeometry()
        if self.pokemon:
            self._update_types() # Refresh badges size/spacing if needed
