"""
Entités métier de l'application Pokémon Analyzer
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Pokemon:
    """Entité représentant un Pokémon"""
    number: int
    pokedex_number: int  # Numéro de Pokédex (peut être différent de number si form)
    name: str # Nom traduit (ex: Dracaufeu)
    api_name: str # Nom API/Anglais (ex: charizard)
    types: List[str]
    generation: int
    description: Optional[str] = None  # Description du Pokémon dans la langue courante
    height: Optional[int] = None  # Taille en décimètres
    weight: Optional[int] = None  # Poids en hectogrammes
    abilities: List[Dict] = None  # Liste des talents [{'name': '...', 'is_hidden': bool}]

    def __str__(self) -> str:
        return f"#{self.pokedex_number:03d} - {self.name.title()}"


@dataclass
class TypeAnalysis:
    """Résultat d'analyse des types"""
    weaknesses: List[str]
    resistances: List[str]
    immunities: List[str]
    vulnerabilities: List[str]
    
    def __str__(self) -> str:
        return f"Faiblesses: {len(self.weaknesses)}, Résistances: {len(self.resistances)}"


@dataclass
class AnalysisResult:
    """Résultat complet d'une analyse de Pokémon"""
    pokemon: Pokemon
    type_analysis: TypeAnalysis
    confidence: float
    timestamp: datetime
    method: str
    
    def __str__(self) -> str:
        return f"{self.pokemon.name} - {self.confidence:.1%} ({self.method})"


@dataclass
class OCRResult:
    """Résultat d'une reconnaissance OCR"""
    success: bool
    pokemon_name: Optional[str]
    confidence: float
    detected_text: Optional[str]
    alternatives: List[Dict]
    error: Optional[str] = None
    
    def is_valid(self) -> bool:
        return self.success and self.pokemon_name is not None


@dataclass
class CaptureRegion:
    """Région de capture d'écran"""
    left: int
    top: int
    width: int
    height: int
    
    def to_dict(self) -> dict:
        return {
            'left': self.left,
            'top': self.top,
            'width': self.width,
            'height': self.height
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CaptureRegion':
        return cls(
            left=data['left'],
            top=data['top'],
            width=data['width'],
            height=data['height']
        )

