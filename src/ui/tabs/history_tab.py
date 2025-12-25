"""
Onglet d'historique
Affiche l'historique des analyses effectuées
"""
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFileDialog
)
from PySide6.QtCore import Signal

from .base_tab import BaseTab
from core.entities import AnalysisResult


class HistoryTab(BaseTab):
    """Onglet d'historique des analyses"""
    
    # Signal émis quand un élément de l'historique est sélectionné
    history_item_selected = Signal(str)  # nom du Pokémon
    
    def __init__(self, parent=None):
        self.history = []
        super().__init__(parent)
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        
        # Liste d'historique
        history_group = QGroupBox("📜 Analyses précédentes")
        history_layout = QVBoxLayout()
        
        self.tree_history = QTreeWidget()
        self.tree_history.setHeaderLabels(["Date/Heure", "Pokémon", "Méthode", "Confiance"])
        self.tree_history.itemDoubleClicked.connect(self._on_item_double_clicked)
        history_layout.addWidget(self.tree_history)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        btn_clear = QPushButton("🗑️ Effacer Historique")
        btn_clear.clicked.connect(self._clear_history)
        btn_layout.addWidget(btn_clear)
        
        btn_export = QPushButton("💾 Exporter Historique")
        btn_export.clicked.connect(self._export_history)
        btn_layout.addWidget(btn_export)
        
        layout.addLayout(btn_layout)
    
    def add_analysis(self, analysis_result: AnalysisResult):
        """
        Ajoute une analyse à l'historique
        
        Args:
            analysis_result: Résultat de l'analyse
        """
        self.history.append(analysis_result)
        
        # Ajoute à l'arbre
        item = QTreeWidgetItem([
            analysis_result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            analysis_result.pokemon.name.title(),
            analysis_result.method,
            f"{analysis_result.confidence:.1%}"
        ])
        self.tree_history.addTopLevelItem(item)
    
    def _on_item_double_clicked(self, item, column):
        """Appelé lors du double-clic sur un élément"""
        row = self.tree_history.indexOfTopLevelItem(item)
        if 0 <= row < len(self.history):
            pokemon_name = self.history[row].pokemon.name
            self.history_item_selected.emit(pokemon_name)
    
    def _clear_history(self):
        """Efface l'historique"""
        if self.ask_confirmation(
            "Confirmation",
            "Êtes-vous sûr de vouloir effacer tout l'historique ?"
        ):
            self.history.clear()
            self.tree_history.clear()
            self.show_info("Effacement", "Historique effacé !")
    
    def _export_history(self):
        """Exporte l'historique"""
        if not self.history:
            self.show_warning("Attention", "Aucun historique à exporter")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exporter l'historique", 
            "pokemon_history.json",
            "Fichiers JSON (*.json)"
        )
        
        if file_path:
            # Prépare les données
            export_data = []
            for item in self.history:
                export_data.append({
                    'timestamp': item.timestamp.isoformat(),
                    'pokemon_name': item.pokemon.name,
                    'pokemon_number': item.pokemon.number,
                    'types': item.pokemon.types,
                    'confidence': item.confidence,
                    'method': item.method
                })
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.show_info("Export", f"Historique exporté:\n{file_path}")
            except Exception as e:
                self.show_error("Erreur", f"Erreur lors de l'export:\n{e}")

