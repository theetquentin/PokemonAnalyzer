"""
Widget de tableau d'analyse des types Pokémon
Composant réutilisable pour afficher les faiblesses, résistances, etc.
"""
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, 
    QWidget, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QColor

from core.entities import Pokemon, TypeAnalysis
from ui.styles import get_type_emoji, TYPE_COLORS
from core.translations import t, translate_type
from core.utils import get_resource_path
import os


class TypeBadgeWidget(QWidget):
    """
    Widget personnalisé pour afficher un badge de type et son multiplicateur
    Utilise des layouts (Flexbox-like) pour un alignement vertical parfait
    """
    def __init__(self, type_en, type_translated, multiplier, parent=None):
        super().__init__(parent)

        # Layout principal avec padding gauche uniforme
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0)  # 15px de padding à gauche
        layout.setSpacing(20) # Espace entre le badge et le multiplicateur
        
        # --- Badge coloré ---
        badge = QFrame()
        color = TYPE_COLORS.get(type_en.lower(), "#777777")
        badge.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(6, 4, 8, 4) # Padding interne du badge
        badge_layout.setSpacing(6) # Espace entre icône et texte
        badge_layout.setAlignment(Qt.AlignCenter)
        
        # Icône
        icon_label = QLabel()
        icon_path = get_resource_path(f"assets/types/{type_en.lower()}.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setFixedSize(20, 20)
        
        # Texte du type
        text_label = QLabel(type_translated.upper())
        text_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        text_label.setAlignment(Qt.AlignVCenter)
        
        badge_layout.addWidget(icon_label)
        badge_layout.addWidget(text_label)
        
        # --- Multiplicateur ---
        mult_label = QLabel(f"(×{multiplier})")
        mult_label.setStyleSheet("color: #333333; font-weight: bold; font-size: 12px;")
        mult_label.setAlignment(Qt.AlignVCenter)
        
        # Ajout au layout principal
        layout.addWidget(badge)
        layout.addWidget(mult_label)
        layout.addStretch()  # Pousse le contenu vers la gauche


class PokemonAnalysisTable(QTableWidget):
    """Tableau affichant l'analyse des types d'un Pokémon"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()

    def _get_cell_color(self, multiplier: float) -> str:
        """
        Retourne la couleur de fond de cellule en fonction du multiplicateur

        Args:
            multiplier: Multiplicateur de dégâts (0, 0.25, 0.5, 1, 2, 4)

        Returns:
            Code couleur hexadécimal
        """
        if multiplier >= 4:
            return "#FF7777"  # Rouge foncé pour x4
        elif multiplier >= 2:
            return "#FFAAAA"  # Rouge clair pour x2
        elif multiplier == 0:
            return "#CCCCCC"  # Gris pour x0 (immunité)
        elif multiplier <= 0.25:
            return "#88FF88"  # Vert foncé pour x0.25
        elif multiplier <= 0.5:
            return "#AAFFAA"  # Vert clair pour x0.5
        else:
            return "#FFFFFF"  # Blanc pour x1 (neutre)
    
    def _setup_table(self):
        """Configure le tableau"""
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            "🔻 Faiblesses", "🛡️ Résistances", "🚫 Immunités", "💥 Super efficace"
        ])
        
        # Alignement des en-têtes à gauche
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Active les lignes de grille verticales
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        
        # Hauteur de ligne par défaut plus compacte
        self.verticalHeader().setDefaultSectionSize(40)
        
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        font = QFont("Segoe UI Emoji", 10)
        self.setFont(font)
    
    def display_analysis(self, pokemon: Pokemon, analysis: TypeAnalysis, 
                        type_calculator):
        """
        Affiche l'analyse d'un Pokémon dans le tableau
        
        Args:
            pokemon: Pokémon à analyser
            analysis: Résultat de l'analyse
            type_calculator: Calculateur pour obtenir les multiplicateurs
        """
        # Prépare les données
        weaknesses = self._format_type_list(
            analysis.weaknesses, pokemon, type_calculator
        )
        resistances = self._format_type_list(
            analysis.resistances, pokemon, type_calculator
        )
        immunities = self._format_immunity_list(analysis.immunities, type_calculator)
        vulnerabilities = self._format_type_list(
            analysis.vulnerabilities[:8], pokemon, type_calculator, offensive=True
        )
        
        # Remplit le tableau
        max_rows = max(
            len(weaknesses), 
            len(resistances), 
            len(immunities), 
            len(vulnerabilities)
        )
        self.setRowCount(max_rows)
        
        for row in range(max_rows):
            self._set_item(row, 0, weaknesses, row)
            self._set_item(row, 1, resistances, row)
            self._set_item(row, 2, immunities, row)
            self._set_item(row, 3, vulnerabilities, row)
    

    
    def _format_type_list(self, types: list, pokemon: Pokemon, 
                         type_calculator, offensive: bool = False) -> list:
        """
        Formate une liste de types pour l'affichage
        
        Args:
            types: Liste des types
            pokemon: Pokémon concerné
            type_calculator: Calculateur d'efficacité
            offensive: Si True, calcule l'efficacité offensive
            
        Returns:
            Liste de dictionnaires avec les données pour l'affichage
        """
        formatted = []
        for type_name in types:
            if offensive:
                # Efficacité offensive (Pokémon attaque ce type)
                mult = type_calculator.calculate_damage_multiplier(
                    pokemon.types[0], [type_name]
                )
                if len(pokemon.types) > 1:
                    mult2 = type_calculator.calculate_damage_multiplier(
                        pokemon.types[1], [type_name]
                    )
                    mult = max(mult, mult2)
            else:
                # Efficacité défensive (type attaque Pokémon)
                mult = type_calculator.calculate_damage_multiplier(
                    type_name, pokemon.types
                )
            
            # Convertit le nom interne (français) en clé canonique (anglais) pour la traduction
            canonical_key = type_calculator.get_canonical_key(type_name)
            translated_type = translate_type(canonical_key)
            
            formatted.append({
                'type_en': canonical_key,
                'type_translated': translated_type,
                'multiplier': mult
            })
        
        return formatted
    
    def _format_immunity_list(self, types: list, type_calculator) -> list:
        """Formate la liste des immunités"""
        formatted = []
        for type_name in types:
            # Convertit le nom interne (français) en clé canonique (anglais) pour la traduction
            canonical_key = type_calculator.get_canonical_key(type_name)
            translated_type = translate_type(canonical_key)
            
            formatted.append({
                'type_en': canonical_key,
                'type_translated': translated_type,
                'multiplier': 0
            })
        return formatted
    
    def _set_item(self, row: int, col: int, data_list: list, index: int):
        """
        Définit un élément dans le tableau avec un badge HTML
        """
        # Nettoie d'abord la cellule
        self.setCellWidget(row, col, None)
        self.setItem(row, col, None)

        if index < len(data_list):
            data = data_list[index]

            # Crée un item de fond pour la couleur
            item = QTableWidgetItem("")
            item.setFlags(Qt.NoItemFlags)

            # Applique la couleur de fond en fonction du multiplicateur
            bg_color = self._get_cell_color(data['multiplier'])
            item.setBackground(QColor(bg_color))

            self.setItem(row, col, item)

            # Utilise le widget personnalisé pour un alignement parfait
            widget = TypeBadgeWidget(
                data['type_en'],
                data['type_translated'],
                data['multiplier']
            )

            # Ajoute le widget à la cellule
            self.setCellWidget(row, col, widget)
        else:
            # Cellule vide
            item = QTableWidgetItem("")
            item.setFlags(Qt.NoItemFlags)
            self.setItem(row, col, item)
    
    def clear_table(self):
        """Efface le contenu du tableau"""
        self.setRowCount(0)
    
    def update_translations(self):
        """Met à jour les en-têtes de colonnes"""
        self.setHorizontalHeaderLabels([
            f"🔻 {t('header_weaknesses')}",
            f"🛡️ {t('header_resistances')}",
            f"🚫 {t('header_immunities')}",
            f"💥 {t('header_vulnerabilities')}"
        ])
