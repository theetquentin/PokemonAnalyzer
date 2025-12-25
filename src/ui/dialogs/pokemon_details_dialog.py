from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from ui.styles import TYPE_COLORS
from core.translations import translate_type, t
from core.utils import get_resource_path
import os

class PokemonDetailsDialog(QDialog):
    """
    Dialogue modal affichant les détails complets d'un Pokémon
    """
    def __init__(self, pokemon, parent=None, sprite_pixmap=None):
        super().__init__(parent)
        self.pokemon = pokemon
        self.sprite_pixmap = sprite_pixmap
        self.setWindowTitle(f"Détails - {pokemon.name.title()}")
        self.setMinimumWidth(400)
        self.setMinimumHeight(600) # Increased height for sprite
        
        # Style pour fenêtre modale moderne
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
            QLabel {
                color: #2C3E50;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 8px;
                color: #34495E;
                font-size: 13px;
            }
            QPushButton#close_btn {
                background-color: #34495E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton#close_btn:hover {
                background-color: #2C3E50;
            }
        """)
        
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Sprite (si disponible)
        if self.sprite_pixmap and not self.sprite_pixmap.isNull():
            sprite_lbl = QLabel()
            sprite_lbl.setAlignment(Qt.AlignCenter)
            # Scale sprite up for details view but keep quality
            scaled = self.sprite_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            sprite_lbl.setPixmap(scaled)
            layout.addWidget(sprite_lbl)
        
        # En-tête
        header_lbl = QLabel(f"{self.pokemon.name.upper()} #{self.pokemon.pokedex_number:03d}")
        header_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #2C3E50;")
        header_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_lbl)

        # Types
        types_container = self._create_types_display()
        layout.addWidget(types_container)

        gen_lbl = QLabel(f"Gen {self.pokemon.generation}")
        gen_lbl.setStyleSheet("font-size: 14px; color: #7F8C8D;")
        gen_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(gen_lbl)
        
        # Séparateur
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #BDC3C7;")
        layout.addWidget(line)
        
        # Stats Physiques
        stats_layout = QHBoxLayout()
        
        # Convertir et formater
        height_m = (self.pokemon.height / 10.0) if self.pokemon.height else 0
        weight_kg = (self.pokemon.weight / 10.0) if self.pokemon.weight else 0
        
        stats_layout.addWidget(self._create_stat_box(t('label_height'), f"{height_m:.1f}m"))
        stats_layout.addWidget(self._create_stat_box(t('label_weight'), f"{weight_kg:.1f}kg"))
        
        layout.addLayout(stats_layout)
        
        # Talents
        layout.addWidget(self._create_section_title(t('label_talents')))
        
        abilities_text = "Aucun talent connu"
        if self.pokemon.abilities:
            abilities_list = []
            for ability in self.pokemon.abilities:
                name = ability['name'].replace('-', ' ').title()
                if ability.get('is_hidden'):
                    name += f" {t('label_hidden')}"
                abilities_list.append(name)
            abilities_text = ", ".join(abilities_list)
            
        abilities_lbl = QLabel(abilities_text)
        abilities_lbl.setWordWrap(True)
        abilities_lbl.setStyleSheet("font-size: 14px; padding: 5px;")
        layout.addWidget(abilities_lbl)
        
        # Description
        layout.addWidget(self._create_section_title(t('label_description')))
        
        desc_area = QTextEdit()
        desc_area.setReadOnly(True)
        if self.pokemon.description:
            desc_area.setPlainText(self.pokemon.description)
        else:
            desc_area.setPlainText("Aucune description disponible.")
            desc_area.setStyleSheet("font-style: italic; color: #95A5A6;")
            
        layout.addWidget(desc_area)
        
        # Espace flexible
        layout.addStretch()
        
        # Bouton fermer
        close_btn = QPushButton(t('btn_close'))
        close_btn.setObjectName("close_btn")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
    def _create_stat_box(self, title, value):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(5)
        
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("color: #95A5A6; font-size: 11px; font-weight: bold;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("color: #2C3E50; font-size: 16px; font-weight: bold;")
        val_lbl.setAlignment(Qt.AlignCenter)
        
        vbox.addWidget(title_lbl)
        vbox.addWidget(val_lbl)
        
        return container
        
    def _create_section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #7F8C8D;
            margin-top: 10px;
            text-transform: uppercase;
        """)
        return lbl

    def _create_types_display(self):
        """Crée l'affichage des types avec badges"""
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 2, 0, 2)
        h_layout.setSpacing(8)
        h_layout.setAlignment(Qt.AlignCenter)

        for type_en in self.pokemon.types:
            badge = self._create_type_badge(type_en)
            h_layout.addWidget(badge)

        return container

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
        badge_layout.setContentsMargins(6, 4, 6, 4)
        badge_layout.setSpacing(4)

        # Icon
        icon_label = QLabel()
        icon_path = get_resource_path(f"assets/types/{type_en.lower()}.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)

        # Text
        type_translated = translate_type(type_en)
        text_label = QLabel(type_translated.upper())
        text_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px; border: none; background: transparent;")

        badge_layout.addWidget(icon_label)
        badge_layout.addWidget(text_label)

        return badge
