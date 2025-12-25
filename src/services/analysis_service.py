"""
Service d'analyse des Pokémon
Gère toute la logique d'analyse des types et des faiblesses
"""
from typing import List, Dict
from core.entities import Pokemon, TypeAnalysis


class AnalysisService:
    """Service pour analyser les types et faiblesses des Pokémon"""
    
    def __init__(self, type_calculator):
        """
        Args:
            type_calculator: Instance de TypeCalculator pour les calculs d'efficacité
        """
        self.calc = type_calculator
    
    def analyze_pokemon_types(self, pokemon: Pokemon) -> TypeAnalysis:
        """
        Analyse complète des types d'un Pokémon
        
        Args:
            pokemon: Pokémon à analyser
            
        Returns:
            TypeAnalysis contenant faiblesses, résistances, immunités et vulnérabilités
        """
        weaknesses = []
        resistances = []
        immunities = []
        vulnerabilities = []
        
        # Analyse des types reçus (défense)
        for attack_type in self.calc.types:
            effectiveness = self.calc.calculate_damage_multiplier(attack_type, pokemon.types)
            
            if effectiveness == 0:
                immunities.append(attack_type)
            elif effectiveness < 1:
                resistances.append(attack_type)
            elif effectiveness > 1:
                weaknesses.append(attack_type)
        
        # Analyse des types efficaces en attaque
        vulnerabilities = self._get_vulnerable_types(pokemon.types)
        
        return TypeAnalysis(
            weaknesses=weaknesses,
            resistances=resistances,
            immunities=immunities,
            vulnerabilities=vulnerabilities
        )
    
    def _get_vulnerable_types(self, pokemon_types: List[str]) -> List[str]:
        """
        Trouve les types contre lesquels le Pokémon est efficace en attaque
        
        Args:
            pokemon_types: Types du Pokémon
            
        Returns:
            Liste des types vulnérables
        """
        vulnerable = []
        
        for target_type in self.calc.types:
            effectiveness = self.calc.calculate_damage_multiplier(pokemon_types[0], [target_type])
            
            if len(pokemon_types) > 1:
                eff2 = self.calc.calculate_damage_multiplier(pokemon_types[1], [target_type])
                effectiveness = max(effectiveness, eff2)
            
            if effectiveness > 1:
                vulnerable.append(target_type)
        
        return vulnerable[:10]  # Limite à 10 types
    
    def get_damage_multiplier(self, attack_type: str, pokemon: Pokemon) -> float:
        """
        Calcule le multiplicateur de dégâts d'un type contre un Pokémon
        
        Args:
            attack_type: Type de l'attaque
            pokemon: Pokémon défenseur
            
        Returns:
            Multiplicateur de dégâts
        """
        return self.calc.calculate_damage_multiplier(attack_type, pokemon.types)
    
    def format_type_with_multiplier(self, type_name: str, pokemon: Pokemon, emoji_func) -> str:
        """
        Formate un type avec son emoji et multiplicateur
        
        Args:
            type_name: Nom du type
            pokemon: Pokémon pour calculer le multiplicateur
            emoji_func: Fonction pour obtenir l'emoji du type
            
        Returns:
            Chaîne formatée (ex: "🔥 Feu (×2)")
        """
        mult = self.get_damage_multiplier(type_name, pokemon)
        emoji = emoji_func(type_name)
        return f"{emoji} {type_name} (×{mult})"
    
    def generate_text_report(self, pokemon: Pokemon, analysis: TypeAnalysis) -> str:
        """
        Génère un rapport textuel d'analyse
        
        Args:
            pokemon: Pokémon analysé
            analysis: Résultat de l'analyse
            
        Returns:
            Rapport textuel formaté
        """
        report = f"=== ANALYSE POKÉMON ===\n"
        report += f"Nom: {pokemon.name.title()}\n"
        report += f"Numéro: #{pokemon.number:03d}\n"
        report += f"Type(s): {' | '.join(pokemon.types)}\n"
        report += f"Gen: {pokemon.generation}\n\n"
        
        report += f"=== FAIBLESSES ===\n"
        for weakness in analysis.weaknesses:
            mult = self.calc.calculate_damage_multiplier(weakness, pokemon.types)
            report += f"• {weakness} (×{mult})\n"
        
        report += f"\n=== RÉSISTANCES ===\n"
        for resistance in analysis.resistances:
            mult = self.calc.calculate_damage_multiplier(resistance, pokemon.types)
            report += f"• {resistance} (×{mult})\n"
        
        report += f"\n=== IMMUNITÉS ===\n"
        for immunity in analysis.immunities:
            report += f"• {immunity} (×0)\n"
        
        return report

    def analyze_team_weaknesses(self, pokemons: List[Pokemon]) -> Dict[str, any]:
        """
        Analyse les faiblesses communes d'une équipe de Pokémon

        Args:
            pokemons: Liste des Pokémon à analyser

        Returns:
            Dictionnaire avec faiblesses communes, couverture et recommandations
        """
        if not pokemons:
            return {}

        # Analyse chaque pokémon
        individual_analyses = []
        for pokemon in pokemons:
            analysis = self.analyze_pokemon_types(pokemon)
            individual_analyses.append({
                'pokemon': pokemon,
                'analysis': analysis
            })

        # Faiblesses communes (types qui affectent TOUS les pokémons de l'équipe)
        common_weaknesses = set(individual_analyses[0]['analysis'].weaknesses)
        for item in individual_analyses[1:]:
            common_weaknesses &= set(item['analysis'].weaknesses)

        # Faiblesses partagées (types qui affectent AU MOINS 2 pokémons)
        shared_weaknesses = {}
        for attack_type in self.calc.types:
            affected_pokemon = []
            for item in individual_analyses:
                if attack_type in item['analysis'].weaknesses:
                    mult = self.calc.calculate_damage_multiplier(attack_type, item['pokemon'].types)
                    affected_pokemon.append({
                        'pokemon': item['pokemon'].name,
                        'multiplier': mult
                    })

            if len(affected_pokemon) >= 2:
                shared_weaknesses[attack_type] = affected_pokemon

        # Immunités communes
        common_immunities = set(individual_analyses[0]['analysis'].immunities)
        for item in individual_analyses[1:]:
            common_immunities &= set(item['analysis'].immunities)

        # Couverture offensive (types que l'équipe peut contrer efficacement)
        offensive_coverage = set()
        for item in individual_analyses:
            offensive_coverage.update(item['analysis'].vulnerabilities)

        return {
            'individual_analyses': individual_analyses,
            'common_weaknesses': list(common_weaknesses),
            'shared_weaknesses': shared_weaknesses,
            'common_immunities': list(common_immunities),
            'offensive_coverage': list(offensive_coverage)
        }

