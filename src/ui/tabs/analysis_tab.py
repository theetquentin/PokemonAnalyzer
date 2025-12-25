"""
Onglet d'analyse des Pokémon
Affiche l'analyse détaillée des types et faiblesses
"""
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QPushButton,
    QFileDialog, QApplication
)
from PySide6.QtGui import QFont

from .base_tab import BaseTab
from ui.widgets import PokemonAnalysisTable
from core.entities import Pokemon
from ui.styles import get_type_emoji
from core.translations import translate_type


class AnalysisTab(BaseTab):
    """Onglet d'analyse détaillée"""
    
    def __init__(self, analysis_service, parent=None):
        self.analysis_service = analysis_service
        self.current_pokemon = None
        self.current_analysis = None
        super().__init__(parent)
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        
        # Groupe d'informations
        info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout()
        
        self.txt_info = QTextEdit()
        self.txt_info.setReadOnly(True)
        self.txt_info.setMaximumHeight(80)
        font = QFont("Consolas", 10)
        self.txt_info.setFont(font)
        # Message par défaut
        self.txt_info.setText(
            "📋 Informations du Pokémon\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📛 Nom\n"
            "🔢 Numéro\n"
            "🏆 Gen\n"
            "🎨 Type(s)"
        )
        info_layout.addWidget(self.txt_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Tableau d'analyse
        analysis_group = QGroupBox("📊 Analyse des Types")
        analysis_layout = QVBoxLayout()
        
        self.analysis_table = PokemonAnalysisTable()
        analysis_layout.addWidget(self.analysis_table)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group, 1)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 Sauvegarder Analyse")
        btn_save.clicked.connect(self._save_analysis)
        btn_layout.addWidget(btn_save)
        
        btn_copy = QPushButton("📋 Copier Rapport")
        btn_copy.clicked.connect(self._copy_report)
        btn_layout.addWidget(btn_copy)
        
        layout.addLayout(btn_layout)
    
    def display_pokemon(self, pokemon: Pokemon):
        """
        Affiche l'analyse d'un Pokémon
        
        Args:
            pokemon: Pokémon à analyser
        """
        self.current_pokemon = pokemon
        
        # Affiche les informations
        info_text = f"ANALYSE POKÉMON ✨\n"
        info_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        info_text += f"📛 Nom: {pokemon.name.upper()}\n"
        info_text += f"🔢 Numéro: #{pokemon.number:03d}\n"
        info_text += f"🏆 Gen: {pokemon.generation}\n"
        types_str = " | ".join([f"{translate_type(t)} {get_type_emoji(t)}" for t in pokemon.types])
        info_text += f"🎨 Type(s): {types_str}\n\n"
        info_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        info_text += f"📊 Analyse des types ci-dessous"

        self.txt_info.setText(info_text)
        
        # Analyse et affiche
        self.current_analysis = self.analysis_service.analyze_pokemon_types(pokemon)
        self.analysis_table.display_analysis(
            pokemon, 
            self.current_analysis,
            self.analysis_service.calc
        )
    
    def _save_analysis(self):
        """Sauvegarde l'analyse dans un fichier"""
        if not self.current_pokemon:
            self.show_warning("Attention", "Aucun Pokémon à analyser")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Sauvegarder l'analyse", 
            f"{self.current_pokemon.name}_analysis.txt",
            "Fichiers texte (*.txt)"
        )
        
        if file_path:
            report = self.analysis_service.generate_text_report(
                self.current_pokemon,
                self.current_analysis
            )
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                self.show_info("Sauvegarde", f"Analyse sauvegardée:\n{file_path}")
            except Exception as e:
                self.show_error("Erreur", f"Erreur lors de la sauvegarde:\n{e}")
    
    def _copy_report(self):
        """Copie le rapport dans le presse-papiers"""
        if not self.current_pokemon:
            self.show_warning("Attention", "Aucun Pokémon à copier")
            return
        
        report = self.analysis_service.generate_text_report(
            self.current_pokemon,
            self.current_analysis
        )
        
        clipboard = QApplication.clipboard()
        clipboard.setText(report)
        
        self.show_info("Copie", "Rapport copié dans le presse-papiers !")

