"""
Système de calcul des efficacités de types Pokémon CORRIGÉ
Basé sur le tableau officiel Pokémon
"""

from typing import Dict, List, Tuple
from enum import Enum
import json
import os
import sys
from pathlib import Path

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

class TypeEffectiveness(Enum):
    """Énumération des efficacités possibles"""
    NO_EFFECT = 0.0      # Aucun effet (immunité)
    NOT_VERY = 0.5       # Pas très efficace
    NORMAL = 1.0         # Efficacité normale
    SUPER = 2.0          # Super efficace

class TypeCalculator:
    """Calculateur d'efficacité des types Pokémon"""

    def __init__(self):
        self.types = [
            'Normal', 'Feu', 'Eau', 'Électrik', 'Plante', 'Glace',
            'Combat', 'Poison', 'Sol', 'Vol', 'Psy', 'Insecte',
            'Roche', 'Spectre', 'Dragon', 'Ténèbres', 'Acier', 'Fée'
        ]

        # Charge les traductions depuis le JSON
        self.type_translations = self._load_type_translations()

        # Construit le mapping inverse: n'importe quelle langue → français
        self.type_to_french = self._build_reverse_mapping()

        # Emojis pour les types
        self.type_emojis = {
            'Normal': '⚪', 'Feu': '🔥', 'Eau': '💧', 'Électrik': '⚡',
            'Plante': '🌱', 'Glace': '❄️', 'Combat': '👊', 'Poison': '☠️',
            'Sol': '🏔️', 'Vol': '🕊️', 'Psy': '🔮', 'Insecte': '🐛',
            'Roche': '🪨', 'Spectre': '👻', 'Dragon': '🐉', 'Ténèbres': '🌑',
            'Acier': '⚙️', 'Fée': '🧚'
        }

        self.effectiveness_chart = self._create_effectiveness_chart()

    def _load_type_translations(self) -> Dict:
        """Charge les traductions de types depuis le fichier JSON"""
        try:
            # Utilise get_resource_path pour fonctionner en dev et avec PyInstaller
            json_path = get_resource_path('infrastructure/api/type_translations.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Erreur chargement type_translations.json: {e}")
            return {}

    def _build_reverse_mapping(self) -> Dict[str, str]:
        """Construit un mapping inversé: n'importe quelle traduction → français"""
        reverse_map = {}

        for type_key, translations in self.type_translations.items():
            # Ajoute toutes les traductions qui pointent vers le français
            french_name = translations.get('fr', '')
            
            # Ajoute la clé brute (souvent en anglais minuscule, ex: 'fire')
            if type_key:
                reverse_map[type_key.lower()] = french_name
            
            for lang_code, translated_name in translations.items():
                if lang_code != 'fr' and translated_name and isinstance(translated_name, str):
                    reverse_map[translated_name] = french_name
                    # Ajoute aussi la version minuscule pour être robuste
                    reverse_map[translated_name.lower()] = french_name

            # Ajoute aussi l'identité française
            if french_name:
                reverse_map[french_name] = french_name
                reverse_map[french_name.lower()] = french_name

        return reverse_map

    def get_canonical_key(self, type_name: str) -> str:
        """
        Récupère la clé canonique (anglais minuscule) pour un type donné (français ou autre)
        Utile pour la traduction via translate_type()
        """
        # Si c'est déjà une clé connue (ex: 'fire')
        if type_name.lower() in self.type_translations:
            return type_name.lower()
            
        # Cherche la clé correspondante à la valeur française
        # Note: C'est un peu inefficace, on pourrait cacher ce mapping si c'est trop lent
        for key, data in self.type_translations.items():
            if data.get('fr') == type_name:
                return key
                
        return type_name.lower()

    def _normalize_type(self, type_name: str) -> str:
        """Convertit un nom de type (n'importe quelle langue) vers le français"""
        normalized = self.type_to_french.get(type_name, type_name)
        return normalized
    
    def _create_effectiveness_chart(self) -> Dict[str, Dict[str, float]]:
        """Crée le tableau d'efficacité officiel des types Pokémon (corrigé selon chart officiel)"""

        chart = {}
        for attacker in self.types:
            chart[attacker] = {}
            for defender in self.types:
                chart[attacker][defender] = TypeEffectiveness.NORMAL.value

        # === NORMAL ===
        chart["Normal"]["Roche"] = 0.5
        chart["Normal"]["Acier"] = 0.5
        chart["Normal"]["Spectre"] = 0.0

        # === FEU ===
        chart["Feu"]["Feu"] = 0.5
        chart["Feu"]["Eau"] = 0.5
        chart["Feu"]["Plante"] = 2.0
        chart["Feu"]["Glace"] = 2.0
        chart["Feu"]["Insecte"] = 2.0
        chart["Feu"]["Roche"] = 0.5
        chart["Feu"]["Dragon"] = 0.5
        chart["Feu"]["Acier"] = 2.0

        # === EAU ===
        chart["Eau"]["Feu"] = 2.0
        chart["Eau"]["Eau"] = 0.5
        chart["Eau"]["Plante"] = 0.5
        chart["Eau"]["Sol"] = 2.0
        chart["Eau"]["Roche"] = 2.0
        chart["Eau"]["Dragon"] = 0.5

        # === ÉLECTRIK ===
        chart["Électrik"]["Eau"] = 2.0
        chart["Électrik"]["Électrik"] = 0.5
        chart["Électrik"]["Plante"] = 0.5
        chart["Électrik"]["Sol"] = 0.0
        chart["Électrik"]["Vol"] = 2.0
        chart["Électrik"]["Dragon"] = 0.5

        # === PLANTE ===
        chart["Plante"]["Feu"] = 0.5
        chart["Plante"]["Eau"] = 2.0
        chart["Plante"]["Plante"] = 0.5
        chart["Plante"]["Poison"] = 0.5
        chart["Plante"]["Sol"] = 2.0
        chart["Plante"]["Vol"] = 0.5
        chart["Plante"]["Insecte"] = 0.5
        chart["Plante"]["Roche"] = 2.0
        chart["Plante"]["Dragon"] = 0.5
        chart["Plante"]["Acier"] = 0.5

        # === GLACE ===
        chart["Glace"]["Feu"] = 0.5
        chart["Glace"]["Eau"] = 0.5
        chart["Glace"]["Plante"] = 2.0
        chart["Glace"]["Glace"] = 0.5
        chart["Glace"]["Sol"] = 2.0
        chart["Glace"]["Vol"] = 2.0
        chart["Glace"]["Dragon"] = 2.0
        chart["Glace"]["Acier"] = 0.5

        # === COMBAT ===
        chart["Combat"]["Normal"] = 2.0
        chart["Combat"]["Glace"] = 2.0
        chart["Combat"]["Roche"] = 2.0
        chart["Combat"]["Acier"] = 2.0
        chart["Combat"]["Ténèbres"] = 2.0
        chart["Combat"]["Fée"] = 0.5
        chart["Combat"]["Poison"] = 0.5
        chart["Combat"]["Vol"] = 0.5
        chart["Combat"]["Psy"] = 0.5
        chart["Combat"]["Insecte"] = 0.5
        chart["Combat"]["Spectre"] = 0.0

        # === POISON ===
        chart["Poison"]["Plante"] = 2.0
        chart["Poison"]["Fée"] = 2.0
        chart["Poison"]["Poison"] = 0.5
        chart["Poison"]["Sol"] = 0.5
        chart["Poison"]["Roche"] = 0.5
        chart["Poison"]["Spectre"] = 0.5
        chart["Poison"]["Acier"] = 0.0

        # === SOL ===
        chart["Sol"]["Feu"] = 2.0
        chart["Sol"]["Électrik"] = 2.0
        chart["Sol"]["Plante"] = 0.5
        chart["Sol"]["Poison"] = 2.0
        chart["Sol"]["Vol"] = 0.0
        chart["Sol"]["Insecte"] = 0.5
        chart["Sol"]["Roche"] = 2.0
        chart["Sol"]["Acier"] = 2.0

        # === VOL ===
        chart["Vol"]["Plante"] = 2.0
        chart["Vol"]["Combat"] = 2.0
        chart["Vol"]["Insecte"] = 2.0
        chart["Vol"]["Électrik"] = 0.5
        chart["Vol"]["Roche"] = 0.5
        chart["Vol"]["Acier"] = 0.5

        # === PSY ===
        chart["Psy"]["Combat"] = 2.0
        chart["Psy"]["Poison"] = 2.0
        chart["Psy"]["Psy"] = 0.5
        chart["Psy"]["Acier"] = 0.5
        chart["Psy"]["Ténèbres"] = 0.0

        # === INSECTE ===
        chart["Insecte"]["Plante"] = 2.0
        chart["Insecte"]["Psy"] = 2.0
        chart["Insecte"]["Ténèbres"] = 2.0
        chart["Insecte"]["Feu"] = 0.5
        chart["Insecte"]["Combat"] = 0.5
        chart["Insecte"]["Poison"] = 0.5
        chart["Insecte"]["Vol"] = 0.5
        chart["Insecte"]["Spectre"] = 0.5
        chart["Insecte"]["Acier"] = 0.5
        chart["Insecte"]["Fée"] = 0.5

        # === ROCHE ===
        chart["Roche"]["Feu"] = 2.0
        chart["Roche"]["Glace"] = 2.0
        chart["Roche"]["Vol"] = 2.0
        chart["Roche"]["Insecte"] = 2.0
        chart["Roche"]["Combat"] = 0.5
        chart["Roche"]["Sol"] = 0.5
        chart["Roche"]["Acier"] = 0.5

        # === SPECTRE ===
        chart["Spectre"]["Psy"] = 2.0
        chart["Spectre"]["Spectre"] = 2.0
        chart["Spectre"]["Ténèbres"] = 0.5
        chart["Spectre"]["Normal"] = 0.0

        # === DRAGON ===
        chart["Dragon"]["Dragon"] = 2.0
        chart["Dragon"]["Acier"] = 0.5
        chart["Dragon"]["Fée"] = 0.0

        # === TÉNÈBRES ===
        chart["Ténèbres"]["Psy"] = 2.0
        chart["Ténèbres"]["Spectre"] = 2.0
        chart["Ténèbres"]["Combat"] = 0.5
        chart["Ténèbres"]["Ténèbres"] = 0.5
        chart["Ténèbres"]["Fée"] = 0.5

        # === ACIER ===
        chart["Acier"]["Glace"] = 2.0
        chart["Acier"]["Roche"] = 2.0
        chart["Acier"]["Fée"] = 2.0
        chart["Acier"]["Feu"] = 0.5
        chart["Acier"]["Eau"] = 0.5
        chart["Acier"]["Électrik"] = 0.5
        chart["Acier"]["Acier"] = 0.5

        # === FÉE ===
        chart["Fée"]["Combat"] = 2.0
        chart["Fée"]["Dragon"] = 2.0
        chart["Fée"]["Ténèbres"] = 2.0
        chart["Fée"]["Feu"] = 0.5
        chart["Fée"]["Poison"] = 0.5
        chart["Fée"]["Acier"] = 0.5

        return chart

    
    def get_effectiveness(self, attacker_type: str, defender_type: str) -> float:
        """Récupère l'efficacité d'un type attaquant contre un type défenseur"""
        # Normalise les types vers le français (langue interne)
        attacker_fr = self._normalize_type(attacker_type)
        defender_fr = self._normalize_type(defender_type)

        if attacker_fr not in self.types or defender_fr not in self.types:
            return TypeEffectiveness.NORMAL.value

        return self.effectiveness_chart[attacker_fr][defender_fr]
    
    def calculate_damage_multiplier(self, attacker_type: str, defender_types: List[str]) -> float:
        """Calcule le multiplicateur de dégâts total contre un Pokémon (mono ou double type)"""
        multiplier = 1.0
        
        for defender_type in defender_types:
            effectiveness = self.get_effectiveness(attacker_type, defender_type)
            multiplier *= effectiveness
        
        return multiplier
    
    def analyze_pokemon_weaknesses(self, pokemon_types: List[str]) -> Dict[str, List[str]]:
        """Analyse les faiblesses et résistances d'un Pokémon"""
        # Normalise les types du Pokémon vers le français
        normalized_pokemon_types = [self._normalize_type(t) for t in pokemon_types]

        results = {
            "weaknesses": [],        # Types super efficaces (x2 ou x4)
            "resistances": [],       # Types pas très efficaces (x0.5 ou x0.25)
            "immunities": [],        # Types sans effet (x0)
            "normal": []            # Types normaux (x1)
        }

        for attacking_type in self.types:
            multiplier = self.calculate_damage_multiplier(attacking_type, normalized_pokemon_types)

            if multiplier == 0:
                results["immunities"].append(attacking_type)
            elif multiplier >= 2:
                results["weaknesses"].append(attacking_type)
            elif multiplier <= 0.5:
                results["resistances"].append(attacking_type)
            else:
                results["normal"].append(attacking_type)

        return results
    
    def get_best_counters(self, pokemon_types: List[str], limit: int = 5) -> List[Dict[str, any]]:
        """Trouve les meilleurs types pour contrer un Pokémon"""
        # Normalise les types du Pokémon vers le français
        normalized_pokemon_types = [self._normalize_type(t) for t in pokemon_types]

        counter_effectiveness = []

        for attacking_type in self.types:
            multiplier = self.calculate_damage_multiplier(attacking_type, normalized_pokemon_types)
            if multiplier > 1:  # Seulement les types efficaces
                counter_effectiveness.append({
                    "type": attacking_type,
                    "multiplier": multiplier,
                    "description": self._get_effectiveness_description(multiplier),
                    "emoji": self.type_emojis.get(attacking_type, "❓")
                })

        # Trie par efficacité décroissante
        counter_effectiveness.sort(key=lambda x: x["multiplier"], reverse=True)
        return counter_effectiveness[:limit]
    
    def _get_effectiveness_description(self, multiplier: float) -> str:
        """Retourne une description textuelle de l'efficacité"""
        if multiplier == 0:
            return "Aucun effet"
        elif multiplier <= 0.5:
            return "Pas très efficace"
        elif multiplier == 1.0:
            return "Efficacité normale"
        elif multiplier >= 2.0:
            return "Super efficace"
        else:
            return "Efficacité normale"
    
    def format_analysis_report(self, pokemon_name: str, pokemon_types: List[str]) -> str:
        """Génère un rapport d'analyse formaté pour un Pokémon"""
        analysis = self.analyze_pokemon_weaknesses(pokemon_types)
        counters = self.get_best_counters(pokemon_types)
        
        report = f"\n🎯 ANALYSE DE TYPE - {pokemon_name.upper()} 🎯\n"
        report += "=" * 50 + "\n"
        
        # Types du Pokémon
        type_display = " | ".join([f"{t} {self.type_emojis.get(t, '❓')}" for t in pokemon_types])
        report += f"📋 Type(s): {type_display}\n\n"
        
        # Affichage en colonnes pour les faiblesses
        if analysis["weaknesses"]:
            report += "🔻 FAIBLESSES:\t"
            weakness_items = []
            for weakness in analysis["weaknesses"]:
                multiplier = self.calculate_damage_multiplier(weakness, pokemon_types)
                emoji = self.type_emojis.get(weakness, "❓")
                weakness_items.append(f"{weakness} {emoji} (x{multiplier})")
            report += " | ".join(weakness_items) + "\n"
        
        # Affichage en colonnes pour les résistances
        if analysis["resistances"]:
            report += "🛡️ RÉSISTANCES:\t"
            resistance_items = []
            for resistance in analysis["resistances"]:
                multiplier = self.calculate_damage_multiplier(resistance, pokemon_types)
                emoji = self.type_emojis.get(resistance, "❓")
                resistance_items.append(f"{resistance} {emoji} (x{multiplier})")
            report += " | ".join(resistance_items) + "\n"
        
        # Affichage en colonnes pour les immunités
        if analysis["immunities"]:
            report += "🚫 IMMUNITÉS:\t"
            immunity_items = []
            for immunity in analysis["immunities"]:
                emoji = self.type_emojis.get(immunity, "❓")
                immunity_items.append(f"{immunity} {emoji} (x0)")
            report += " | ".join(immunity_items) + "\n"
        
        # Affichage en colonnes pour les meilleurs contres
        if counters:
            report += "⚔️ CONTRES:\t"
            counter_items = []
            for counter in counters:
                counter_items.append(f"{counter['type']} {counter['emoji']} (x{counter['multiplier']})")
            report += " | ".join(counter_items) + "\n"
        
        return report
    
    def get_type_chart_summary(self) -> str:
        """Retourne un résumé du tableau des types"""
        summary = "\n📊 RÉSUMÉ DU TABLEAU DES TYPES\n"
        summary += "=" * 40 + "\n"
        summary += f"Types disponibles: {len(self.types)}\n"
        summary += f"Interactions: {len(self.types) * len(self.types)}\n"
        summary += "Basé sur les données officielles Pokémon\n"
        return summary
