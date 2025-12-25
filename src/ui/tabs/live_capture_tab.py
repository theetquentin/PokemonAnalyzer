"""
Onglet de capture en temps réel
Permet de capturer et analyser l'écran en continu
"""
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize, QUrl
from PySide6.QtGui import QFont, QPixmap, QImage, QPalette
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox, QListWidget,
    QListWidgetItem, QSplitter, QFrame, QAbstractSpinBox, QSizePolicy
)

from .base_tab import BaseTab
from ui.widgets.form_selector import FormSelector
from ui.widgets.pokemon_analysis_table import PokemonAnalysisTable
from ui.widgets.pokemon_info_widget import PokemonInfoWidget
from ui.styles import TYPE_COLORS
from core.translations import t
from core.utils import get_resource_path
import requests
import os


class SpriteWorker(QThread):
    """Worker thread pour charger les sprites via requests (plus robuste que QNetworkAccessManager)"""
    finished = Signal(bytes, int)
    error = Signal(str)

    def __init__(self, url, number, parent=None):
        super().__init__(parent)
        self.url = url
        self.number = number

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            self.finished.emit(response.content, self.number)
        except Exception as e:
            self.error.emit(str(e))


class TypeBadgeContainer(QWidget):
    """
    Widget pour afficher les badges de types d'un Pokémon
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.badges = []
    
    def set_types(self, types_info):
        """
        Affiche les badges pour une liste de types
        types_info: list of dict with 'type_en' and 'type_translated'
        """
        # Clear existing badges
        for badge in self.badges:
            badge.deleteLater()
        self.badges.clear()
        
        # Create new badges
        for info in types_info:
            badge = self._create_badge(info['type_en'], info['type_translated'])
            self.layout.addWidget(badge)
            self.badges.append(badge)
        
        # Add stretch to push badges to the left
        self.layout.addStretch()
    
    def _create_badge(self, type_en, type_translated):
        """
        Crée un badge pour un type
        """
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
        text_label = QLabel(type_translated.upper())
        text_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        
        badge_layout.addWidget(icon_label)
        badge_layout.addWidget(text_label)
        
        return badge


class LiveCaptureTab(BaseTab):
    """Onglet de capture en temps réel (Passive View)"""
    
    # Signal émis quand un Pokémon est détecté (pour compatibilité, mais géré par presenter)
    pokemon_detected = Signal(str, float, dict)
    # Signal émis quand une forme est sélectionnée (form_name, types, api_name, widget_number)
    form_selected = Signal(str, list, str, int)
    
    def __init__(self, parent=None):
        # Note: On ne passe plus le service ici
        super().__init__(parent)
        # Stocke l'état de capture pour la gestion des traductions
        self._is_capturing = False

    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)  # Padding général
        layout.setSpacing(10)

        # Statut discret en haut
        self.lbl_status = QLabel("En attente - Sélectionnez une zone d'écran")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        font_status = QFont()
        font_status.setPointSize(9)
        self.lbl_status.setFont(font_status)
        self.lbl_status.setStyleSheet("QLabel { color: #95A5A6; padding: 4px; }")
        layout.addWidget(self.lbl_status)

        # Style global Windows - fond gris uniforme
        self.setStyleSheet("""
            LiveCaptureTab { background-color: #F0F0F0; font-family: 'Segoe UI', sans-serif; }
            QGroupBox { 
                background-color: #F0F0F0; 
                border: 1px solid #D0D0D0;
                border-radius: 0px;
                margin-top: 8px;
                font-weight: normal;
                padding: 18px 10px 10px 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0px 5px 4px 5px;
                background-color: #F0F0F0;
                left: 5px;
            }
            QWidget#section_group { 
                background-color: #F0F0F0; 
                border-radius: 0px;
            }
            QWidget#section_group QPushButton { 
                background-color: #34495E; 
                color: white; 
                border-radius: 3px; 
                padding: 8px; 
                font-weight: bold; 
                border: none;
            }
            QWidget#section_group QPushButton:hover { background-color: #2C3E50; }
            QWidget#section_group QPushButton:pressed { background-color: #1A252F; }
            QWidget#section_group QPushButton:disabled { background-color: #BDC3C7; }
            /* Styles minimaux - laisse les contrôles natifs */
            /* Styles minimaux - laisse les contrôles natifs */
            QSpinBox, QDoubleSpinBox {
                background-color: white;
                color: #000000;
            }
            QTextEdit { 
                background-color: #F0F0F0; 
                border: 1px solid #D0D0D0;
                border-radius: 0px;
            }
            QListWidget {
                background-color: #F0F0F0;
                border: 1px solid #D0D0D0;
                border-radius: 0px;
            }
            QSplitter::handle {
                background-color: transparent;
                width: 0px;
                height: 0px;
            }
        """)

        # ========== SPLITTER PRINCIPAL : Contrôles + Tableau (haut) | Aperçus (bas) ==========

        # Partie haute : Contrôles (gauche) + Tableau d'analyse (droite)
        top_splitter = QSplitter(Qt.Horizontal)

        # ===== COLONNE DE GAUCHE : Contrôles =====
        controls_container = QGroupBox("Contrôles")
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Zone de capture
        zone_group = QWidget()
        zone_group.setObjectName("section_group")
        zone_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        zone_layout = QVBoxLayout()
        zone_layout.setSpacing(10)
        zone_layout.setContentsMargins(10, 10, 10, 10)

        self.btn_select_region = QPushButton("🎯 Sélectionner Zone")
        self.btn_select_region.setMinimumWidth(200)
        self.btn_select_region.setMinimumHeight(32)
        zone_layout.addWidget(self.btn_select_region)
        
        # Spacer fixe pour éviter la compression
        from PySide6.QtWidgets import QSpacerItem
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        zone_layout.addItem(spacer)

        zone_buttons_layout = QHBoxLayout()
        self.btn_save_region = QPushButton("💾 Sauv.")
        self.btn_save_region.setMinimumWidth(95)
        self.btn_save_region.setMinimumHeight(32)
        zone_buttons_layout.addWidget(self.btn_save_region)

        self.btn_load_region = QPushButton("📂 Charger")
        self.btn_load_region.setMinimumWidth(95)
        self.btn_load_region.setMinimumHeight(32)
        zone_buttons_layout.addWidget(self.btn_load_region)
        zone_layout.addLayout(zone_buttons_layout)

        # Info région
        self.lbl_region_info = QLabel("Aucune zone sélectionnée")
        self.lbl_region_info.setAlignment(Qt.AlignCenter)
        font_small = QFont()
        font_small.setPointSize(8)
        self.lbl_region_info.setFont(font_small)
        self.lbl_region_info.setStyleSheet("QLabel { color: #7F8C8D; padding: 3px; background-color: transparent; }")
        zone_layout.addWidget(self.lbl_region_info)

        zone_group.setLayout(zone_layout)
        controls_layout.addWidget(zone_group)

        # Mode de combat
        mode_group = QWidget()
        mode_group.setObjectName("section_group")
        mode_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(5)
        mode_layout.setContentsMargins(10, 10, 10, 10)

        self.lbl_pokemon_count = QLabel("Nombre de Pokémon:")
        self.lbl_pokemon_count.setStyleSheet("background-color: transparent;")
        mode_layout.addWidget(self.lbl_pokemon_count)

        self.combo_battle_mode = QComboBox()
        self.combo_battle_mode.addItems(["Solo (1)", "Duo (2)", "Trio (3)"])
        self.combo_battle_mode.setCurrentIndex(0)
        self.combo_battle_mode.setToolTip("Solo: détecte 1 Pokémon\nDuo: détecte 2 Pokémon\nTrio: détecte 3 Pokémon")
        mode_layout.addWidget(self.combo_battle_mode)

        mode_group.setLayout(mode_layout)
        controls_layout.addWidget(mode_group)

        # Paramètres de capture
        params_group = QWidget()
        params_group.setObjectName("section_group")
        params_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        params_layout = QVBoxLayout()
        params_layout.setSpacing(5)
        params_layout.setContentsMargins(10, 10, 10, 10)

        # Intervalle
        interval_container = QHBoxLayout()
        self.lbl_interval = QLabel("Intervalle (s):")
        self.lbl_interval.setStyleSheet("background-color: transparent;")
        self.lbl_interval.setToolTip("Délai entre chaque capture d'écran")
        interval_container.addWidget(self.lbl_interval)

        self.spin_interval = QDoubleSpinBox()
        self.spin_interval.setRange(0.5, 10.0)
        self.spin_interval.setValue(2.0)
        self.spin_interval.setSingleStep(0.5)
        self.spin_interval.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_interval.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_interval.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                color: #000000;
            }
        """)
        self.spin_interval.setToolTip("Temps d'attente entre les captures")
        interval_container.addWidget(self.spin_interval)
        params_layout.addLayout(interval_container)

        # Confiance
        conf_container = QHBoxLayout()
        self.lbl_confidence = QLabel("Confiance:")
        self.lbl_confidence.setStyleSheet("background-color: transparent;")
        self.lbl_confidence.setToolTip("Seuil minimum de confiance OCR")
        conf_container.addWidget(self.lbl_confidence)

        self.spin_confidence = QDoubleSpinBox()
        self.spin_confidence.setRange(0.1, 1.0)
        self.spin_confidence.setValue(0.6)
        self.spin_confidence.setSingleStep(0.1)
        self.spin_confidence.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_confidence.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_confidence.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                color: #000000;
            }
        """)
        self.spin_confidence.setToolTip("60% de confiance minimum recommandé")
        conf_container.addWidget(self.spin_confidence)
        params_layout.addLayout(conf_container)

        # Détections consécutives
        sens_container = QHBoxLayout()
        self.lbl_consecutive = QLabel("Consécutives:")
        self.lbl_consecutive.setStyleSheet("background-color: transparent;")
        self.lbl_consecutive.setToolTip("Nombre de détections consécutives requises")
        sens_container.addWidget(self.lbl_consecutive)

        self.spin_sensitivity = QSpinBox()
        self.spin_sensitivity.setRange(1, 5)
        self.spin_sensitivity.setValue(1)
        self.spin_sensitivity.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_sensitivity.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin_sensitivity.setStyleSheet("""
            QSpinBox {
                background-color: white;
                color: #000000;
            }
        """)
        self.spin_sensitivity.setToolTip("1 = immédiat, 3-5 = plus fiable")
        sens_container.addWidget(self.spin_sensitivity)
        params_layout.addLayout(sens_container)

        params_group.setLayout(params_layout)
        controls_layout.addWidget(params_group)

        # Boutons de capture
        capture_group = QWidget()
        capture_group.setObjectName("section_group")
        capture_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        capture_layout = QVBoxLayout()
        capture_layout.setSpacing(5)
        capture_layout.setContentsMargins(10, 10, 10, 10)

        self.btn_toggle = QPushButton(f"▶️ {t('btn_start_capture')}")
        # Style spécifique pour le bouton toggle (vert par défaut)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        self.btn_toggle.setEnabled(False)
        self.btn_toggle.setMinimumHeight(40)
        capture_layout.addWidget(self.btn_toggle)


        capture_group.setLayout(capture_layout)
        controls_layout.addWidget(capture_group)

        # Stretch pour pousser tout vers le haut
        controls_layout.addStretch()

        controls_container.setLayout(controls_layout)
        # Force une largeur fixe absolue (augmentée pour éviter la compression des boutons)
        controls_container.setFixedWidth(280)
        # Empêche la compression dans le splitter mais permet l'extension
        controls_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        top_splitter.addWidget(controls_container)

        # ===== COLONNE DE DROITE : Tableau d'analyse =====
        table_group = QGroupBox("Analyse des Types")
        table_layout = QVBoxLayout()

        # Dropdown pour sélectionner quel pokémon analyser (en mode multi)
        selector_layout = QHBoxLayout()
        self.lbl_analyze = QLabel("Analyser:")
        selector_layout.addWidget(self.lbl_analyze)

        self.combo_pokemon_selector = QComboBox()
        self.combo_pokemon_selector.setVisible(False)  # Caché par défaut
        selector_layout.addWidget(self.combo_pokemon_selector)

        selector_layout.addStretch()
        table_layout.addLayout(selector_layout)

        self.analysis_table = PokemonAnalysisTable()
        table_layout.addWidget(self.analysis_table)
        table_group.setLayout(table_layout)
        top_splitter.addWidget(table_group)

        # Empêche le panneau de contrôles d'être compressé par le splitter
        top_splitter.setCollapsible(0, False)
        # Proportions Contrôles vs Tableau : largeur fixe pour contrôles, reste pour tableau
        top_splitter.setStretchFactor(0, 0)  # Pas de stretch pour contrôles (largeur fixe)
        top_splitter.setStretchFactor(1, 1)  # Tout le stretch va au tableau

        # top_splitter.setMaximumHeight(400)  # REMOVED: Limite la hauteur du tableau causait des soucis de layout
        layout.addWidget(top_splitter, 2)  # Tableau prend moins d'espace

        # ===== Partie basse : Aperçus et Pokémon détectés =====
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        # Aperçu de capture (plus compact)
        preview_group = QGroupBox("Aperçu")
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(5, 5, 5, 5)
        preview_layout.setSpacing(3)

        self.lbl_preview = QLabel("Aucune capture")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setMinimumSize(100, 75)
        self.lbl_preview.setStyleSheet("QLabel { background-color: #34495E; color: white; border-radius: 5px; padding: 5px; }")

        preview_layout.addWidget(self.lbl_preview)
        preview_group.setLayout(preview_layout)
        bottom_layout.addWidget(preview_group, 1)

        # Historique (plus compact)
        history_group = QGroupBox("Historique")
        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(5, 5, 5, 5)
        history_layout.setSpacing(3)
        self.list_history = QListWidget()
        history_font = QFont()
        history_font.setPointSize(9)
        self.list_history.setFont(history_font)
        history_layout.addWidget(self.list_history)
        history_group.setLayout(history_layout)
        bottom_layout.addWidget(history_group, 1)

        # Pokémon détectés (plus compact)
        info_sprite_group = QGroupBox("Pokémon(s)")
        info_sprite_layout = QVBoxLayout()
        info_sprite_layout.setContentsMargins(5, 5, 5, 5)
        info_sprite_layout.setSpacing(3)
        # Layout principal qui contiendra 1, 2 ou 3 colonnes
        self.pokemon_container_layout = QHBoxLayout()
        self.pokemon_container_layout.setSpacing(5)

        # === Pokémon 1 (toujours visible) ===
        self.pokemon1_widget = self._create_pokemon_display_widget(1)
        self.pokemon_container_layout.addWidget(self.pokemon1_widget)

        # === Pokémon 2 (caché par défaut pour combats duo/trio) ===
        self.pokemon2_widget = self._create_pokemon_display_widget(2)
        self.pokemon2_widget.setVisible(False)
        self.pokemon_container_layout.addWidget(self.pokemon2_widget)

        # === Pokémon 3 (caché par défaut pour combats trio) ===
        self.pokemon3_widget = self._create_pokemon_display_widget(3)
        self.pokemon3_widget.setVisible(False)
        self.pokemon_container_layout.addWidget(self.pokemon3_widget)

        info_sprite_layout.addLayout(self.pokemon_container_layout)
        info_sprite_group.setLayout(info_sprite_layout)
        bottom_layout.addWidget(info_sprite_group, 2)

        bottom_container.setLayout(bottom_layout)
        layout.addWidget(bottom_container, 3)  # Plus d'espace pour la partie basse

    def _create_pokemon_display_widget(self, number: int):
        """
        Crée un widget pour afficher un Pokémon
        """
        # On utilise directement PokemonInfoWidget qui contient maintenant tout (sprite, forme, info)
        info_widget = PokemonInfoWidget()
        
        # Connecte le signal de changement de forme
        info_widget.form_changed.connect(
            lambda form_name, types, api_name: self._on_form_changed_signal(form_name, types, api_name, number)
        )

        return info_widget

    # === Méthodes d'accès pour le Presenter ===

    def get_capture_params(self):
        """Retourne les paramètres de capture"""
        return {
            'interval': self.spin_interval.value(),
            'sensitivity': self.spin_sensitivity.value(),
            'confidence': self.spin_confidence.value(),
            'max_pokemon': self.combo_battle_mode.currentIndex() + 1
        }

    def update_region_info(self, width, height):
        """Met à jour l'info de la région"""
        self.lbl_region_info.setText(f"{width}×{height}")

    def set_status(self, message, status_type="info"):
        """Met à jour le statut"""
        self.lbl_status.setText(message)
        if status_type == "running":
            self.lbl_status.setStyleSheet("QLabel { color: #27AE60; padding: 4px; font-size: 9pt; }")
        elif status_type == "error":
            self.lbl_status.setStyleSheet("QLabel { color: #E74C3C; padding: 4px; font-size: 9pt; }")
        elif status_type == "success":
            self.lbl_status.setStyleSheet("QLabel { color: #27AE60; padding: 4px; font-size: 9pt; }")
        else:
            self.lbl_status.setStyleSheet("QLabel { color: #95A5A6; padding: 4px; font-size: 9pt; }")

    def enable_capture_controls(self, enabled):
        """Active/Désactive les boutons de capture"""
        self.btn_toggle.setEnabled(enabled)

    def update_capture_state(self, is_capturing):
        """Met à jour l'état visuel de la capture"""
        # Stocke l'état pour les changements de langue
        self._is_capturing = is_capturing

        if is_capturing:
            from core.translations import t
            self.btn_toggle.setText(f"⏸️ {t('btn_stop_capture')}")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
                QPushButton:pressed {
                    background-color: #A93226;
                }
            """)
        else:
            from core.translations import t
            self.btn_toggle.setText(f"▶️ {t('btn_start_capture')}")
            self.btn_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #27AE60;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1E8449;
                }
            """)

    def display_preview(self, image):
        """Affiche l'aperçu de l'image"""
        if image is None:
            return
            
        try:
            import numpy as np
            from PySide6.QtGui import QImage
            
            # Conversion OpenCV -> Qt
            if isinstance(image, np.ndarray):
                height, width, channel = image.shape
                bytes_per_line = 3 * width
                q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(q_img)
            else:
                # Si c'est une image PIL
                # Conversion manuelle robuste sans PIL.ImageQt
                if image.mode == "RGB":
                    data = image.tobytes("raw", "RGB")
                    q_img = QImage(data, image.size[0], image.size[1], QImage.Format_RGB888)
                elif image.mode == "RGBA":
                    data = image.tobytes("raw", "RGBA")
                    q_img = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)
                else:
                    # Fallback pour autres modes
                    image = image.convert("RGBA")
                    data = image.tobytes("raw", "RGBA")
                    q_img = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)
                    
                pixmap = QPixmap.fromImage(q_img)
                
            # Redimensionne pour l'aperçu
            scaled_pixmap = pixmap.scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_preview.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Erreur affichage aperçu: {e}")

    def add_to_history(self, text):
        """Ajoute un élément à l'historique"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.list_history.addItem(f"[{timestamp}] {text}")
        self.list_history.scrollToBottom()

    def set_single_view(self):
        """Configure la vue pour un seul Pokémon"""
        self.pokemon2_widget.setVisible(False)
        self.pokemon3_widget.setVisible(False)
        self.pokemon1_widget.setVisible(True)
        self.pokemon1_widget.set_compact_mode(False) # Mode normal
        self.combo_pokemon_selector.setVisible(False)

    def set_multi_view(self, pokemons_data):
        """Configure la vue pour plusieurs Pokémon (layout + dropdown)"""
        num_pokemon = min(len(pokemons_data), 3)

        # Mode compact si Trio sélectionné (index 2) OU si 3 Pokémon détectés
        # Cela force le redimensionnement même si 1 seul Pokémon est détecté en mode trio
        is_trio_mode = self.combo_battle_mode.currentIndex() == 2
        is_compact = (num_pokemon >= 3) or is_trio_mode

        self.pokemon1_widget.set_compact_mode(is_compact)
        self.pokemon2_widget.set_compact_mode(is_compact)
        self.pokemon3_widget.set_compact_mode(is_compact)

        # Cache tous les sélecteurs de forme pour éviter les signaux parasites
        self.pokemon1_widget.hide_form_selector()
        self.pokemon2_widget.hide_form_selector()
        self.pokemon3_widget.hide_form_selector()

        # Déconnecte les signaux - Note: PokemonInfoWidget gère déjà ses connexions internes
        # On ne touche plus ici car le signal est relayé proprement

        self.pokemon1_widget.setVisible(num_pokemon >= 1)
        self.pokemon2_widget.setVisible(num_pokemon >= 2)
        self.pokemon3_widget.setVisible(num_pokemon >= 3)

        # Peuple le dropdown
        self.combo_pokemon_selector.blockSignals(True)
        self.combo_pokemon_selector.clear()
        for idx, pkmn_data in enumerate(pokemons_data):
            pokemon_name = pkmn_data['pokemon'].name.title()
            self.combo_pokemon_selector.addItem(pokemon_name, idx)
        self.combo_pokemon_selector.setVisible(True)
        self.combo_pokemon_selector.blockSignals(False)

    def display_single_pokemon(self, pokemon, confidence, analysis, image=None, sprite_url=None):
        """
        DEPRECATED: Utiliser set_single_view + _update_pokemon_slot dans le presenter
        Garde pour compatibilité temporaire
        """
        self.set_single_view()


        # Affiche les infos
        info_text = f"{pokemon.name.upper()} #{pokemon.number:03d} | Gen {pokemon.generation} \n"
        types_str = " ".join([f"{get_type_emoji(t)}{translate_type(t)}" for t in pokemon.types])
        info_text += f"Type(s) : {types_str}\n"

        # Ajoute la description si disponible
        if pokemon.description:
            info_text += f"Description : \n{pokemon.description}"

        self.pokemon1_widget.info_txt.setText(info_text)
        
        if image:
            self.display_preview(image)
            
        if sprite_url:
            self._display_sprite(sprite_url, 1)

    def display_multiple_pokemon(self, pokemons_data, image=None, forms_per_pokemon=None):
        """
        Affiche plusieurs Pokémon

        Args:
            pokemons_data: Liste des données Pokémon
            image: Image capturée (optionnel)
            forms_per_pokemon: Dictionnaire {pokemon_number: forms_info} (optionnel)
        """
        num_pokemon = min(len(pokemons_data), 3)

        # Cache tous les sélecteurs de forme pour éviter les signaux parasites
        self.pokemon1_widget.hide_form_selector()
        self.pokemon2_widget.hide_form_selector()
        self.pokemon3_widget.hide_form_selector()

        # Déconnecte les signaux - plus nécessaire avec la nouvelle structure
        
        self.pokemon1_widget.setVisible(num_pokemon >= 1)
        self.pokemon2_widget.setVisible(num_pokemon >= 2)
        self.pokemon3_widget.setVisible(num_pokemon >= 3)

        for idx, pkmn_data in enumerate(pokemons_data[:3], start=1):
            pokemon = pkmn_data['pokemon']
            confidence = pkmn_data['confidence']
            sprite_url = pkmn_data.get('sprite_url')
            
            # Sélectionne le bon widget
            widget = self.pokemon1_widget if idx == 1 else self.pokemon2_widget if idx == 2 else self.pokemon3_widget
            
            # Met à jour les infos
            # Note: widget est maintenant directement instance de PokemonInfoWidget
            widget.set_pokemon(pokemon)

            if sprite_url:
                self._display_sprite(sprite_url, idx)

            # Affiche le sélecteur de forme si disponible
            if forms_per_pokemon and pokemon.number in forms_per_pokemon:
                forms_info = forms_per_pokemon[pokemon.number]
                if forms_info and forms_info.get('has_forms'):
                    # Utilise species_name au lieu de pokemon.name pour éviter la confusion avec les formes
                    species_name = forms_info.get('species_name', pokemon.api_name.split('-')[0])
                    widget.configure_form_selector(species_name, forms_info)

        # Peuple le dropdown
        self.combo_pokemon_selector.blockSignals(True)
        self.combo_pokemon_selector.clear()
        for idx, pkmn_data in enumerate(pokemons_data):
            pokemon_name = pkmn_data['pokemon'].name.title()
            self.combo_pokemon_selector.addItem(pokemon_name, idx)
        self.combo_pokemon_selector.setVisible(True)
        self.combo_pokemon_selector.blockSignals(False)

        if image:
            self.display_preview(image)

    def update_analysis_table(self, pokemon, analysis, type_calculator):
        """Met à jour le tableau d'analyse"""
        self.analysis_table.display_analysis(pokemon, analysis, type_calculator)

    def refresh_pokemon_selector(self, pokemons_data):
        """Rafraîchit le dropdown du sélecteur de Pokémon avec les noms traduits"""
        if not pokemons_data or len(pokemons_data) <= 1:
            return

        # Sauvegarde l'index actuel
        current_index = self.combo_pokemon_selector.currentIndex()

        # Re-peuple le dropdown avec les noms traduits
        self.combo_pokemon_selector.blockSignals(True)
        self.combo_pokemon_selector.clear()
        for idx, pkmn_data in enumerate(pokemons_data):
            pokemon_name = pkmn_data['pokemon'].name.title()
            self.combo_pokemon_selector.addItem(pokemon_name, idx)

        # Restaure l'index sélectionné
        if current_index >= 0 and current_index < len(pokemons_data):
            self.combo_pokemon_selector.setCurrentIndex(current_index)

        self.combo_pokemon_selector.blockSignals(False)

    def _display_sprite(self, url, number):
        """Affiche le sprite depuis une URL"""
        if not url:
            return
            
        # Utilisation de requests dans un thread séparé
        if not hasattr(self, '_sprite_workers'):
            self._sprite_workers = {}
            
        # Gestion de l'ancien worker s'il existe
        if number in self._sprite_workers:
            old_worker = self._sprite_workers[number]
            # Déconnecte tous les signaux pour éviter les callbacks
            try:
                old_worker.finished.disconnect()
                old_worker.error.disconnect()
            except:
                pass
            
            # Attends que le thread finisse (timeout de 2 secondes max)
            if old_worker.isRunning():
                old_worker.wait(2000)
            
            # Nettoie proprement
            old_worker.deleteLater()
        
        # Crée et lance le nouveau worker
        worker = SpriteWorker(url, number, self)
        worker.finished.connect(self._on_sprite_loaded)
        worker.error.connect(lambda err: print(f"Erreur chargement sprite: {err}"))
        
        # Nettoie automatiquement quand terminé
        worker.finished.connect(lambda: self._cleanup_worker(number, worker))
        worker.error.connect(lambda: self._cleanup_worker(number, worker))
        
        self._sprite_workers[number] = worker
        worker.start()

    def _cleanup_worker(self, number, worker):
        """Nettoie le worker une fois fini"""
        if hasattr(self, '_sprite_workers') and number in self._sprite_workers:
            # Ne supprime que si c'est toujours le même worker
            if self._sprite_workers[number] is worker:
                self._sprite_workers.pop(number, None)
        # Attend que le thread soit vraiment terminé avant de détruire
        if worker.isRunning():
            worker.wait(1000)
        worker.deleteLater()

    def _on_sprite_loaded(self, data, number):
        """Callback quand le sprite est chargé"""
        try:
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            
            if not pixmap.isNull():
                # Sélectionne le bon widget
                widget = None
                if number == 1:
                    widget = self.pokemon1_widget
                elif number == 2:
                    widget = self.pokemon2_widget
                elif number == 3:
                    widget = self.pokemon3_widget

                # Vérifie que le widget existe toujours et est valide
                if widget:
                    try:
                        widget.set_sprite(pixmap)
                    except RuntimeError:
                        # Le widget a été supprimé entre-temps
                        pass
                    
        except Exception as e:
            print(f"Erreur traitement sprite: {e}")

    def show_form_selector(self, pokemon_name, forms_info, widget_number=1, pokemon_api_name=None, translated_species_name=None):
        """Affiche le sélecteur de forme pour un widget spécifique"""
        # Sélectionne le bon widget
        if widget_number == 1:
            widget = self.pokemon1_widget
        elif widget_number == 2:
            widget = self.pokemon2_widget
        elif widget_number == 3:
            widget = self.pokemon3_widget
        else:
            return

        # Configure les formes via la méthode du widget
        # On passe toujours pokemon_name (species_name) comme référence de base,
        # jamais pokemon_api_name pour éviter la confusion entre forme de base et forme alternative
        widget.configure_form_selector(pokemon_name, forms_info, translated_species_name=translated_species_name)

    def _on_form_changed_signal(self, form_name, types, api_name, widget_number=1):
        """Relai le signal de changement de forme avec le numéro du widget"""
        try:
            self.form_selected.emit(form_name, types, api_name, widget_number)
        except RuntimeError:
            # Le widget ou le signal n'existe plus
            pass

    def hide_form_selector(self, widget_number=1):
        """Cache le sélecteur de forme pour un widget spécifique"""
        # Sélectionne le bon widget
        if widget_number == 1:
            widget = self.pokemon1_widget
        elif widget_number == 2:
            widget = self.pokemon2_widget
        elif widget_number == 3:
            widget = self.pokemon3_widget
        else:
            return

        widget.hide_form_selector()

    def update_translations(self):
        """Met à jour tous les textes traduits de l'interface"""
        # Boutons principaux
        self.btn_select_region.setText(f"🎯 {t('btn_select_region')}")
        self.btn_save_region.setText(f"💾 {t('save_short')}")
        self.btn_load_region.setText(f"📂 {t('load_short')}")
        
        # Labels de paramètres (références directes)
        self.lbl_pokemon_count.setText(t('label_pokemon_count'))
        self.lbl_interval.setText(t('label_interval_full'))
        self.lbl_confidence.setText(t('label_confidence_full'))
        self.lbl_consecutive.setText(t('label_consecutive'))
        self.lbl_analyze.setText(t('label_analyze'))
        
        # Label région - seulement si pas de dimensions affichées
        if not any(c.isdigit() for c in self.lbl_region_info.text()):
            self.lbl_region_info.setText(t('label_region_not_selected'))

        # Bouton toggle - utilise l'état stocké au lieu de deviner depuis le texte
        if self._is_capturing:
            self.btn_toggle.setText(f"⏸️ {t('btn_stop_capture')}")
        else:
            self.btn_toggle.setText(f"▶️ {t('btn_start_capture')}")
        
        # Preview label
        if hasattr(self, 'lbl_preview'):
            current_preview = self.lbl_preview.text()
            if any(no_cap in current_preview for no_cap in
                  ["Aucune capture", "No capture", "Keine Aufnahme", "Sin captura", "Nessuna cattura", "キャプチャなし"]):
                self.lbl_preview.setText(t('no_capture'))
        
        # Trouver tous les QGroupBox et les mettre à jour
        group_boxes = self.findChildren(QGroupBox)
        for gb in group_boxes:
            title = gb.title()
            title_lower = title.lower()
            # Contrôles
            if any(word.lower() in title_lower for word in ["Contrôles", "Controls", "Steuerung", "Controles", "Controlli", "コントロール"]):
                gb.setTitle(t('group_controls'))
            # Analyse
            elif any(word.lower() in title_lower for word in ["Analyse", "Analysis", "Typ-Analyse", "Análisis", "Analisi", "タイプ分析"]):
                gb.setTitle(t('group_analysis'))
            # Aperçu
            elif any(word.lower() in title_lower for word in ["Aperçu", "Preview", "Vorschau", "Vista Previa", "Anteprima", "プレビュー"]):
                gb.setTitle(t('group_preview'))
            # Historique
            elif any(word.lower() in title_lower for word in ["Historique", "History", "Verlauf", "Historial", "Cronologia", "履歴"]):
                gb.setTitle(t('group_history'))
            # Pokémon
            elif "pokémon" in title_lower or "ポケモン" in title:
                gb.setTitle(t('group_pokemon'))
        
        # Mettre à jour le combo box des modes de combat
        if hasattr(self, 'combo_battle_mode'):
            current_index = self.combo_battle_mode.currentIndex()
            self.combo_battle_mode.blockSignals(True)
            self.combo_battle_mode.clear()
            self.combo_battle_mode.addItems([
                t('battle_solo'),
                t('battle_duo'),
                t('battle_trio')
            ])
            self.combo_battle_mode.setCurrentIndex(current_index)
            self.combo_battle_mode.blockSignals(False)
        
        # Mettre à jour le tableau d'analyse
        if hasattr(self, 'analysis_table'):
            self.analysis_table.update_translations()

        # Mettre à jour les widgets Pokemon
        if hasattr(self, 'pokemon1_widget'):
            self.pokemon1_widget.update_translations()
        if hasattr(self, 'pokemon2_widget'):
            self.pokemon2_widget.update_translations()
        if hasattr(self, 'pokemon3_widget'):
            self.pokemon3_widget.update_translations()




