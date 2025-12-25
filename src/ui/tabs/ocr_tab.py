"""
Onglet OCR
Permet de charger une image et d'utiliser l'OCR pour reconnaître un Pokémon
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLabel,
    QTextEdit, QListWidget, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont

from .base_tab import BaseTab


class OCRTab(BaseTab):
    """Onglet de reconnaissance OCR"""
    
    # Signal émis quand un Pokémon est reconnu
    pokemon_recognized = Signal(str, float)  # nom, confiance
    
    def __init__(self, capture_service, parent=None):
        self.capture_service = capture_service
        self.current_image_path = None
        super().__init__(parent)
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QHBoxLayout(self)
        
        # Partie gauche - Image
        left_widget = QGroupBox("📷 Image")
        left_layout = QVBoxLayout()
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_load = QPushButton("📁 Charger Image")
        btn_load.clicked.connect(self._load_image)
        btn_layout.addWidget(btn_load)
        
        btn_analyze = QPushButton("🔍 Analyser OCR")
        btn_analyze.clicked.connect(self._analyze_with_ocr)
        btn_layout.addWidget(btn_analyze)
        
        left_layout.addLayout(btn_layout)
        
        # Image
        self.lbl_image = QLabel("📷 Aucune image chargée")
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.lbl_image.setMinimumSize(400, 300)
        self.lbl_image.setStyleSheet(
            "QLabel { background-color: #34495E; color: white; }"
        )
        left_layout.addWidget(self.lbl_image)
        
        left_widget.setLayout(left_layout)
        layout.addWidget(left_widget)
        
        # Partie droite - Résultats
        right_widget = QGroupBox("📊 Résultats")
        right_layout = QVBoxLayout()
        
        # Résultats OCR
        results_group = QGroupBox("📝 Résultats OCR")
        results_layout = QVBoxLayout()
        
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.txt_results.setFont(font)
        results_layout.addWidget(self.txt_results)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # Alternatives
        alt_group = QGroupBox("🔄 Alternatives")
        alt_layout = QVBoxLayout()
        
        self.list_alternatives = QListWidget()
        self.list_alternatives.itemDoubleClicked.connect(self._select_alternative)
        alt_layout.addWidget(self.list_alternatives)
        
        alt_group.setLayout(alt_layout)
        right_layout.addWidget(alt_group)
        
        # Bouton d'analyse
        btn_analyze_selected = QPushButton("📊 Analyser Pokémon Sélectionné")
        btn_analyze_selected.clicked.connect(self._analyze_selected)
        right_layout.addWidget(btn_analyze_selected)
        
        right_widget.setLayout(right_layout)
        layout.addWidget(right_widget)
    
    def _load_image(self):
        """Charge une image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Charger une image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # Affiche l'image
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(
                self.lbl_image.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.lbl_image.setPixmap(scaled_pixmap)
            
            # Efface les résultats précédents
            self.txt_results.clear()
            self.list_alternatives.clear()
    
    def _analyze_with_ocr(self):
        """Analyse l'image avec OCR"""
        if not self.current_image_path:
            self.show_warning("Attention", "Chargez d'abord une image")
            return
        
        # Analyse OCR
        result = self.capture_service.analyze_image(
            self.current_image_path,
            confidence_threshold=0.6
        )
        
        if result.is_valid():
            # Affiche les résultats
            self.txt_results.setText(
                f"Pokémon reconnu: {result.pokemon_name.title()}\n"
                f"🎯 Confiance: {result.confidence:.2%}\n"
                f"📝 Texte détecté: {result.detected_text or 'N/A'}"
            )
            
            # Affiche les alternatives
            self.list_alternatives.clear()
            for alt in result.alternatives:
                self.list_alternatives.addItem(
                    f"{alt['name'].title()} ({alt['combined_confidence']:.2%})"
                )
            
            # Sélectionne le premier
            if self.list_alternatives.count() > 0:
                self.list_alternatives.setCurrentRow(0)
            
            # Émet le signal
            self.pokemon_recognized.emit(result.pokemon_name, result.confidence)
        else:
            self.txt_results.setText(
                f"Reconnaissance échouée: {result.error or 'Erreur inconnue'}"
            )
            self.list_alternatives.clear()
    
    def _select_alternative(self, item):
        """Sélectionne une alternative"""
        text = item.text()
        pokemon_name = text.split(' (')[0].lower()
        
        # Émet le signal avec une confiance de 1.0 (sélection manuelle)
        self.pokemon_recognized.emit(pokemon_name, 1.0)
    
    def _analyze_selected(self):
        """Analyse le Pokémon sélectionné"""
        current_item = self.list_alternatives.currentItem()
        if current_item:
            self._select_alternative(current_item)
        else:
            self.show_warning("Attention", "Aucun Pokémon sélectionné")

