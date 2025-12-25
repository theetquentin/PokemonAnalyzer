"""
Service pour l'API PokeAPI
Remplace la base de données locale avec des données complètes de l'API
"""
import requests
import unicodedata
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import logging

# Import de la fonction utilitaire pour les chemins
try:
    from core.utils import get_resource_path
except ImportError:
    # Fallback si l'import échoue
    def get_resource_path(relative_path):
        try:
            base_path = Path(sys._MEIPASS)
        except AttributeError:
            base_path = Path(__file__).parent.parent.parent
        return base_path / relative_path

logger = logging.getLogger(__name__)


class PokeAPIService:
    """Service pour interroger l'API PokeAPI avec cache et traduction française"""

    BASE_URL = "https://pokeapi.co/api/v2"

    # Mapping des noms de types anglais vers leurs IDs dans l'API
    TYPE_IDS = {
        "normal": 1,
        "fighting": 2,
        "flying": 3,
        "poison": 4,
        "ground": 5,
        "rock": 6,
        "bug": 7,
        "ghost": 8,
        "steel": 9,
        "fire": 10,
        "water": 11,
        "grass": 12,
        "electric": 13,
        "psychic": 14,
        "ice": 15,
        "dragon": 16,
        "dark": 17,
        "fairy": 18
    }

    # Mapping des codes de langue PokeAPI
    LANGUAGE_CODES_API = {
        'fr': 5,   # français
        'en': 9,   # english
        'de': 6,   # deutsch
        'es': 7,   # español
        'it': 8,   # italiano
        'jp': 1    # japanese (ja-Hrkt)
    }

    def __init__(self):
        """Initialise le service PokeAPI"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pokemon-Analyzer/1.0'
        })
        self._name_cache = {}  # Cache pour les noms français
        self._pokemon_cache = {}  # Cache pour les données Pokémon
        self._names_db = {}  # Base de tous les noms (chargée depuis le JSON)
        self._type_translations_cache = {}  # Cache pour les traductions de types

        # Langue courante (par défaut: français) - DOIT être défini AVANT _load_names_database
        self.current_language = 'fr'

        # Charge la base de noms si disponible
        self._load_names_database()

        # Charge les traductions de types
        self._load_type_translations()

        logger.info("PokeAPI Service initialized")

    def set_language(self, language_code: str):
        """
        Change la langue courante de l'API

        Args:
            language_code: Code langue ('fr', 'en', 'de', 'es', 'it', 'jp')
        """
        if language_code in ['fr', 'en', 'de', 'es', 'it', 'jp']:
            self.current_language = language_code
            # Reconstruit le cache de recherche avec la nouvelle langue
            self._rebuild_search_cache(language_code)
            # Vide les caches pour forcer le rechargement avec la nouvelle langue
            self.get_pokemon_by_number.cache_clear()
            self.get_pokemon_by_name.cache_clear()
            self._get_localized_name.cache_clear()
            self._get_pokemon_description.cache_clear()
            logger.info(f"Language set to: {language_code}")

    def _load_names_database(self):
        """Charge le fichier pokemon_names.json avec tous les noms FR/EN/DE/JP"""
        try:
            # Utilise get_resource_path pour fonctionner en dev et avec PyInstaller
            names_file = get_resource_path('infrastructure/api/pokemon_names.json')

            if not names_file.exists():
                logger.warning(f"Fichier {names_file} non trouvé. Générez-le avec generate_pokemon_names.py")
                return

            with open(names_file, 'r', encoding='utf-8') as f:
                self._names_db = json.load(f)

            logger.info(f"Base de noms chargée: {len(self._names_db)} entrées")

            # Construit le cache de recherche pour la langue par défaut
            self._rebuild_search_cache(self.current_language)

        except Exception as e:
            logger.error(f"Erreur lors du chargement de pokemon_names.json: {e}")

    def _rebuild_search_cache(self, language_code: str):
        """
        Reconstruit le cache de recherche pour TOUTES les langues
        Permet de chercher un Pokémon dans n'importe quelle langue

        Args:
            language_code: Code de langue courante (pour info uniquement)
        """
        self._search_cache = {}

        # Inclut TOUTES les langues dans le cache de recherche
        for pokemon_id, data in self._names_db.items():
            if 'names' in data:
                for lang_code, name in data['names'].items():
                    if name:
                        slug = self._slugify(name)
                        # Si plusieurs langues ont le même slug, garde le premier
                        if slug not in self._search_cache:
                            self._search_cache[slug] = int(pokemon_id)

        logger.info(f"Cache de recherche reconstruit (toutes langues): {len(self._search_cache)} entrées")

    def _load_type_translations(self):
        """Charge les traductions de tous les types depuis le fichier JSON"""
        # Utilise get_resource_path pour fonctionner en dev et avec PyInstaller
        translations_file = get_resource_path('infrastructure/api/type_translations.json')

        try:
            with open(translations_file, 'r', encoding='utf-8') as f:
                self._type_translations_cache = json.load(f)
            logger.info(f"Traductions de types chargées: {len(self._type_translations_cache)} types")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des traductions de types: {e}")
            # Fallback: utilise les noms anglais capitalisés
            self._type_translations_cache = {
                type_name: {
                    'fr': type_name.capitalize(),
                    'en': type_name.capitalize(),
                    'de': type_name.capitalize(),
                    'es': type_name.capitalize(),
                    'it': type_name.capitalize(),
                    'jp': type_name.capitalize()
                }
                for type_name in self.TYPE_IDS.keys()
            }

    def get_type_translation(self, type_name_en: str, language_code: str = None) -> str:
        """
        Récupère la traduction d'un type

        Args:
            type_name_en: Nom du type en anglais (minuscule)
            language_code: Code de langue ('fr', 'en', 'de', 'jp'). Si None, utilise current_language

        Returns:
            Nom traduit du type
        """
        if language_code is None:
            language_code = self.current_language

        type_name_lower = type_name_en.lower()

        # Cherche dans le cache
        if type_name_lower in self._type_translations_cache:
            translations = self._type_translations_cache[type_name_lower]
            return translations.get(language_code, type_name_en.capitalize())

        # Fallback
        return type_name_en.capitalize()

    @lru_cache(maxsize=1000)
    def get_pokemon_by_number(self, number: int) -> Optional[Dict]:
        """
        Récupère les informations d'un Pokémon par son numéro

        Args:
            number: Numéro du Pokédex national

        Returns:
            Dictionnaire avec les données du Pokémon ou None
        """
        try:
            # Vérifie si on a les données locales (nom FR, etc.)
            local_data = self._names_db.get(str(number))
            
            url = f"{self.BASE_URL}/pokemon/{number}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            return self._parse_pokemon_data(data, local_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Pokemon #{number}: {e}")
            return None

    @lru_cache(maxsize=1000)
    def get_pokemon_forms(self, pokemon_id: int) -> Optional[Dict]:
        """
        Récupère les formes alternatives d'un Pokémon

        Args:
            pokemon_id: ID du Pokémon

        Returns:
            Dictionnaire avec:
            - has_forms: bool (True si le Pokémon a plusieurs formes)
            - default_form: str (nom de la forme par défaut)
            - forms: List[Dict] (liste des formes avec name, url, is_default)
        """
        try:
            url = f"{self.BASE_URL}/pokemon-species/{pokemon_id}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            varieties = data.get('varieties', [])

            if len(varieties) <= 1:
                return {
                    'has_forms': False,
                    'default_form': varieties[0]['pokemon']['name'] if varieties else None,
                    'forms': []
                }

            # Il y a plusieurs formes
            forms_list = []
            default_form = None
            species_name = data.get('name') # Le nom de l'espèce (ex: charizard)

            for variety in varieties:
                form_name = variety['pokemon']['name']
                is_default = variety.get('is_default', False)

                if is_default:
                    default_form = form_name

                forms_list.append({
                    'name': form_name,
                    'url': variety['pokemon']['url'],
                    'is_default': is_default
                })

            return {
                'has_forms': True,
                'default_form': default_form,
                'species_name': species_name,
                'forms': forms_list
            }

        except requests.exceptions.RequestException as e:
            # Si erreur 404, c'est peut-être un ID de forme (ex: 10034)
            # On essaie de récupérer l'ID de l'espèce parente
            response = getattr(e, 'response', None)
            if response is not None and response.status_code == 404:
                try:
                    # Appel vers /pokemon/{id} pour avoir l'espèce
                    url_pokemon = f"{self.BASE_URL}/pokemon/{pokemon_id}"
                    resp_pokemon = self.session.get(url_pokemon, timeout=5)
                    resp_pokemon.raise_for_status()
                    
                    data_pokemon = resp_pokemon.json()
                    species_url = data_pokemon['species']['url']
                    species_id = int(species_url.split('/')[-2])
                    
                    # Réessaie avec l'ID de l'espèce
                    return self.get_pokemon_forms(species_id)
                    
                except Exception as e2:
                     logger.warning(f"Could not resolve species for form {pokemon_id}: {e2}")
                     pass

            return None

    def get_pokemon_form_data(self, form_name: str) -> Optional[Dict]:
        """
        Récupère les données d'une forme spécifique de Pokémon

        Args:
            form_name: Nom de la forme (ex: "deoxys-attack", "charizard-mega-x")

        Returns:
            Dictionnaire avec les données de cette forme
        """
        try:
            url = f"{self.BASE_URL}/pokemon/{form_name}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            # Pour les formes, on essaie de trouver l'ID parent pour les données locales
            # L'API renvoie l'ID du Pokémon parent dans 'species'
            species_url = data['species']['url']
            species_id = int(species_url.split('/')[-2])
            local_data = self._names_db.get(str(species_id))
            
            pokemon_data = self._parse_pokemon_data(data, local_data, species_id=species_id)

            # Ajoute l'information de forme
            if pokemon_data:
                pokemon_data['form'] = form_name

            return pokemon_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching form '{form_name}': {e}")
            return None

    @lru_cache(maxsize=1000)
    def get_pokemon_by_name(self, name: str) -> Optional[Dict]:
        """
        Récupère les informations d'un Pokémon par son nom
        Accepte les noms dans toutes les langues supportées (FR, EN, DE, JP)

        Args:
            name: Nom du Pokémon

        Returns:
            Dictionnaire avec les données du Pokémon ou None
        """
        # Normalise le nom pour la recherche
        slug = self._slugify(name)

        # Cherche dans le cache de recherche (rapide, hors ligne)
        if slug in self._search_cache:
            pokemon_id = self._search_cache[slug]
            return self.get_pokemon_by_number(pokemon_id)

        # Fallback: cherche dans le cache legacy (si utilisé ailleurs)
        if slug in self._name_cache:
            return self.get_pokemon_by_number(self._name_cache[slug])
            
        # Fallback API (anglais seulement)
        # Si le nom ressemble à un slug anglais, on tente l'API
        return self._fetch_by_english_name(name.lower())

    def _fetch_by_english_name(self, name_en: str) -> Optional[Dict]:
        """
        Récupère un Pokémon depuis l'API en utilisant son nom anglais

        Args:
            name_en: Nom anglais du Pokémon

        Returns:
            Dictionnaire avec les données du Pokémon ou None
        """
        try:
            url = f"{self.BASE_URL}/pokemon/{name_en}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            
            # Récupère les données locales via l'ID
            pokemon_id = data['id']
            
            # Tente de récupérer l'ID de l'espèce si possible pour mapper correctement les données locales
            species_id = None
            if 'species' in data and 'url' in data['species']:
                 try:
                     species_url = data['species']['url']
                     species_id = int(species_url.split('/')[-2])
                 except:
                     pass
            
            target_id = species_id if species_id else pokemon_id
            local_data = self._names_db.get(str(target_id))
            
            pokemon_data = self._parse_pokemon_data(data, local_data, species_id=species_id)

            return pokemon_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Pokemon '{name_en}': {e}")
            return None

    def _parse_pokemon_data(self, api_data: dict, local_data: dict = None, species_id: int = None) -> Dict:
        """
        Parse les données de l'API et les convertit au format de l'application

        Args:
            api_data: Données brutes de l'API
            local_data: Données locales (noms traduits)
            species_id: ID de l'espèce (optionnel, utiliser si différent de api_data['id'] comme pour les formes via get_pokemon_form_data)

        Returns:
            Dictionnaire formaté
        """
        # Determine the real pokedex number (species ID) first!
        pokedex_number = species_id
        if pokedex_number is None:
             # Try to extract from species URL if available
             if 'species' in api_data and 'url' in api_data['species']:
                 try:
                     pokedex_number = int(api_data['species']['url'].split('/')[-2])
                 except (ValueError, IndexError):
                     pokedex_number = api_data['id']
             else:
                 pokedex_number = api_data['id']

        # Récupère le nom dans la langue courante depuis les données locales si dispo
        localized_name = None
        if local_data and 'names' in local_data and self.current_language in local_data['names']:
            localized_name = local_data['names'][self.current_language]

        # Sinon fallback sur l'API species (lent)
        if not localized_name:
            # On utilise le pokedex_number (Species ID) pour chercher le nom localisé
            # Cela corrige le bug où l'ID de forme (ex: 10034) est utilisé et échoue
            localized_name = self._get_localized_name(pokedex_number)

        # Récupère les types EN ANGLAIS (ils seront traduits à l'affichage)
        types = [t['type']['name'] for t in api_data['types']]

        # Détermine la génération basée sur l'ID (espèce)
        generation = self._get_generation_from_id(pokedex_number)

        # --- Name formatting based on form ---
        # Si on a un species_id (donc une forme spécifique) ou si le nom API a un tiret (forme)
        # On essaie de formater le nom pour inclure la forme (ex: Méga Dracaufeu X)
        
        # 1. On récupère le nom le plus précis disponible (Nom de forme localisé ou Nom API)
        final_name = localized_name or api_data['name']
        
        # 2. On prépare le nom de l'ESPÈCE pour le formatage (Base propre)
        # Cela évite d'avoir "Mega charizard-mega-y Y" si on n'a pas la traduction de la forme
        species_localized_name = self._get_localized_name(pokedex_number)
        if not species_localized_name:
             # Fallback sur le nom API de l'espèce
             if 'species' in api_data:
                 species_localized_name = api_data['species']['name']
             else:
                 species_localized_name = api_data['name'].split('-')[0]

        # On importe ici pour éviter import circulaire potentiel en top-level
        from core.translations import format_form_name
        
        # Il faut récupérer le nom de l'espèce API si possible pour la comparaison
        species_api_name = api_data['species']['name'] if 'species' in api_data else api_data['name'].split('-')[0]
        
        full_formatted_name = format_form_name(
            pokemon_name=species_api_name, 
            form_name=api_data['name'], 
            translated_pokemon_name=species_localized_name # Usage du nom d'espèce propre
        )
        
        # Si le formatage retourne "Base" ou "Normal" (c'est la forme de base), on garde juste le nom l'espèce
        if full_formatted_name in ["Base", "Normal", "もと"]:
             # C'est la forme de base, on garde le nom de l'espèce (ex: Dracaufeu)
             # Si on avait un localized_name spécifique (rare pour base), on le garde, sinon species_localized_name
             final_name = species_localized_name
        else:
             # C'est une forme spéciale, on utilise le nom formaté complet
             final_name = full_formatted_name

        # Récupère la description du Pokémon
        description = self._get_pokemon_description(pokedex_number)

        return {
            "number": api_data['id'],
            "pokedex_number": pokedex_number,
            "name": final_name,
            "api_name": api_data['name'],
            "types": types,
            "generation": generation,
            "height": api_data['height'],
            "weight": api_data['weight'],
            "abilities": [{'name': a['ability']['name'], 'is_hidden': a['is_hidden']} for a in api_data['abilities']],
            "base_experience": api_data.get('base_experience', 0),
            "sprite": api_data['sprites']['front_default'],
            "description": description
        }

    @lru_cache(maxsize=1000)
    def _get_localized_name(self, pokemon_id: int) -> Optional[str]:
        """
        Récupère le nom localisé d'un Pokémon depuis l'API species
        (Utilisé uniquement si pas dans le JSON local)

        Args:
            pokemon_id: ID du Pokémon

        Returns:
            Nom localisé ou None
        """
        try:
            # Vérifie d'abord le JSON local
            if str(pokemon_id) in self._names_db:
                names = self._names_db[str(pokemon_id)].get('names', {})
                if self.current_language in names:
                    return names[self.current_language]

            url = f"{self.BASE_URL}/pokemon-species/{pokemon_id}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()

            # Cherche le nom dans la langue courante
            for name_entry in data.get('names', []):
                if name_entry['language']['name'] == self.current_language:
                    return name_entry['name']

            return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch localized name for Pokemon #{pokemon_id}: {e}")
            return None

    @lru_cache(maxsize=1000)
    def _get_pokemon_description(self, pokemon_id: int) -> Optional[str]:
        """
        Récupère la description du Pokémon depuis l'API pokemon-species
        Prend la dernière version de jeu disponible pour ce Pokémon dans la langue courante

        Args:
            pokemon_id: ID du Pokémon

        Returns:
            Description du Pokémon ou None
        """
        try:
            # Récupère les données de l'espèce
            url = f"{self.BASE_URL}/pokemon-species/{pokemon_id}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            species_data = response.json()

            # Récupère le code de langue pour l'API
            lang_code = self.LANGUAGE_CODES_API.get(self.current_language, 9)  # 9 = english par défaut

            # Récupère les flavor_text_entries
            flavor_texts = species_data.get('flavor_text_entries', [])

            # Filtre pour la langue courante
            matching_entries = [
                entry for entry in flavor_texts
                if entry.get('language', {}).get('url', '').endswith(f'/{lang_code}/')
            ]

            if not matching_entries:
                logger.warning(f"No flavor text found for Pokemon #{pokemon_id} in language {self.current_language}")
                return None

            # Prend la dernière version de jeu (la plus récente dans la liste)
            latest_entry = matching_entries[-1]
            flavor_text = latest_entry.get('flavor_text', '')

            # Nettoie le texte (remplace les retours à la ligne)
            flavor_text = flavor_text.replace('\n', ' ').replace('\f', ' ').strip()

            return flavor_text

        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch description for Pokemon #{pokemon_id}: {e}")
            return None

    def _get_generation_from_id(self, pokemon_id: int) -> int:
        """
        Détermine la génération basée sur l'ID du Pokémon

        Args:
            pokemon_id: ID du Pokémon

        Returns:
            Numéro de génération (1-9)
        """
        if pokemon_id <= 151:
            return 1
        elif pokemon_id <= 251:
            return 2
        elif pokemon_id <= 386:
            return 3
        elif pokemon_id <= 493:
            return 4
        elif pokemon_id <= 649:
            return 5
        elif pokemon_id <= 721:
            return 6
        elif pokemon_id <= 809:
            return 7
        elif pokemon_id <= 905:
            return 8
        else:
            return 9

    def _slugify(self, text: str) -> str:
        """
        Normalise un texte pour la recherche (slugify)
        - Minuscules
        - Pas d'accents
        - Pas de caractères spéciaux (sauf apostrophes qui sont supprimées)
        """
        if not isinstance(text, str):
            return str(text)
            
        # Minuscules
        text = text.lower()

        # Supprime les accents (NFD décompose les accents)
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')

        # Supprime caractères spéciaux
        text = text.replace(".", "").replace(" ", "").replace("-", "").replace("'", "").replace("’", "")
        
        # Cas particuliers
        text = text.replace("♀", "f").replace("♂", "m")

        return text

    def _normalize_name(self, name: str) -> str:
        """Alias pour _slugify (rétrocompatibilité)"""
        return self._slugify(name)

    def search_pokemon(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Recherche des Pokémon par nom partiel (recherche dans le cache uniquement)
        Pour une recherche complète, utilisez search_all_pokemon

        Args:
            query: Requête de recherche
            limit: Nombre maximum de résultats (défaut: 20)

        Returns:
            Liste des Pokémon trouvés
        """
        slug = self._slugify(query)

        # Collecte les IDs correspondants dans un set pour éviter les doublons
        matching_ids = set()
        for search_slug, pokemon_id in self._search_cache.items():
            if slug in search_slug:
                matching_ids.add(pokemon_id)

        # Convertit en liste et trie par ordre croissant (ordre du Pokédex)
        matching_ids = sorted(matching_ids)

        # Limite à 20 résultats AVANT de charger les données
        matching_ids = matching_ids[:limit]

        # Charge uniquement les données des Pokémon limités
        results = []
        for pokemon_id in matching_ids:
            pokemon_data = self.get_pokemon_by_number(pokemon_id)
            if pokemon_data:
                results.append(pokemon_data)

        return results

    def get_pokemon_by_type(self, pokemon_type: str) -> List[Dict]:
        """
        Récupère tous les Pokémon d'un type donné
        Note: Cette méthode fait un appel API pour récupérer la liste

        Args:
            pokemon_type: Type en français

        Returns:
            Liste des Pokémon de ce type
        """
        # Si le type est une clé connue (anglais), on l'utilise directement
        if pokemon_type.lower() in self.TYPE_IDS:
            english_type = pokemon_type.lower()
        else:
            # Sinon on essaie de trouver via les traductions (TODO: implémenter si nécessaire)
            # Pour l'instant on assume que c'est l'anglais
            english_type = pokemon_type.lower()

        if not english_type:
            return []

        try:
            url = f"{self.BASE_URL}/type/{english_type}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            # Récupère uniquement les 20 premiers pour ne pas surcharger
            for pokemon_entry in data['pokemon'][:20]:
                pokemon_name = pokemon_entry['pokemon']['name']
                pokemon_data = self.get_pokemon_by_name(pokemon_name)
                if pokemon_data:
                    results.append(pokemon_data)

            # Trie par numéro
            results.sort(key=lambda x: x["number"])
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Pokemon by type '{pokemon_type}': {e}")
            return []

    def get_pokemon_by_generation(self, generation: int, limit: int = 20) -> List[Dict]:
        """
        Récupère les Pokémon d'une génération

        Args:
            generation: Numéro de génération (1-9)
            limit: Nombre maximum de résultats (défaut: 20)

        Returns:
            Liste des Pokémon de cette génération (limité)
        """
        ranges = self.get_generation_ranges()
        if generation not in ranges:
            return []

        start, end = ranges[generation]
        results = []

        # Limite le nombre de Pokémon chargés
        max_number = min(start + limit, end + 1)

        for number in range(start, max_number):
            pokemon_data = self.get_pokemon_by_number(number)
            if pokemon_data:
                results.append(pokemon_data)

        return results

    def get_all_types(self) -> List[str]:
        """
        Récupère tous les types disponibles (en français)

        Returns:
            Liste des types
        """
        return sorted(list(self.TYPE_TRANSLATIONS.values()))

    def get_total_count(self) -> int:
        """
        Récupère le nombre total de Pokémon disponibles
        Note: Retourne une estimation basée sur la dernière génération

        Returns:
            Nombre total de Pokémon
        """
        return 1025  # Nombre actuel de Pokémon dans l'API (Gen 1-9)

    def get_all_pokemon_names(self) -> List[str]:
        """
        Récupère tous les noms de Pokémon connus (toutes langues confondues)
        Utile pour l'initialisation de l'OCR

        Returns:
            Liste de tous les noms
        """
        all_names = set()
        for data in self._names_db.values():
            if 'names' in data:
                for name in data['names'].values():
                    if name:
                        all_names.add(name)
        return list(all_names)

    def get_generation_ranges(self) -> Dict[int, Tuple[int, int]]:
        """
        Récupère les plages de numéros pour chaque génération

        Returns:
            Dictionnaire generation -> (debut, fin)
        """
        return {
            1: (1, 151),      # Kanto
            2: (152, 251),    # Johto
            3: (252, 386),    # Hoenn
            4: (387, 493),    # Sinnoh
            5: (494, 649),    # Unys
            6: (650, 721),    # Kalos
            7: (722, 809),    # Alola
            8: (810, 905),    # Galar
            9: (906, 1025)    # Paldea
        }

    def get_generation_info(self) -> Dict[int, Dict[str, str]]:
        """
        Récupère les informations sur chaque génération

        Returns:
            Dictionnaire avec les infos de génération
        """
        return {
            1: {"region": "Kanto", "games": "Rouge/Bleu/Jaune"},
            2: {"region": "Johto", "games": "Or/Argent/Cristal"},
            3: {"region": "Hoenn", "games": "Rubis/Saphir/Émeraude"},
            4: {"region": "Sinnoh", "games": "Diamant/Perle/Platine"},
            5: {"region": "Unys", "games": "Noir/Blanc"},
            6: {"region": "Kalos", "games": "X/Y"},
            7: {"region": "Alola", "games": "Soleil/Lune"},
            8: {"region": "Galar", "games": "Épée/Bouclier"},
            9: {"region": "Paldea", "games": "Écarlate/Violet"}
        }

    def preload_generation(self, generation: int, callback=None):
        """
        Précharge les données d'une génération dans le cache
        Utile pour améliorer les performances

        Args:
            generation: Numéro de génération
            callback: Fonction appelée pour chaque Pokémon chargé (optionnel)
        """
        ranges = self.get_generation_ranges()
        if generation not in ranges:
            return

        start, end = ranges[generation]
        logger.info(f"Preloading generation {generation} (Pokemon #{start}-#{end})")

        for number in range(start, end + 1):
            pokemon_data = self.get_pokemon_by_number(number)
            if callback and pokemon_data:
                callback(pokemon_data)

        logger.info(f"Generation {generation} preloaded successfully")

    @property
    def pokemon_data(self):
        """
        Propriété pour compatibilité avec l'ancienne PokemonDatabase
        Retourne le cache actuel
        """
        return self._pokemon_cache


# Fonction de test
if __name__ == "__main__":
    import sys
    import io

    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    logging.basicConfig(level=logging.INFO)

    print("Test du service PokeAPI")
    print("=" * 50)

    service = PokeAPIService()

    # Test 1: Récupération par numéro
    print("\nTest 1: Récupération par numéro (Pikachu #25)")
    pikachu = service.get_pokemon_by_number(25)
    if pikachu:
        print(f"OK #{pikachu['number']:03d} - {pikachu['name'].title()}")
        print(f"   Type(s): {' | '.join(pikachu['types'])}")
        print(f"   Generation: {pikachu['generation']}")

    # Test 2: Récupération par nom anglais
    print("\nTest 2: Récupération par nom (ditto)")
    ditto = service.get_pokemon_by_name("ditto")
    if ditto:
        print(f"OK #{ditto['number']:03d} - {ditto['name'].title()}")
        print(f"   Type(s): {' | '.join(ditto['types'])}")

    # Test 3: Récupération par nom français (après avoir chargé le nom)
    print("\nTest 3: Récupération par nom français")
    if pikachu:
        pikachu_fr = service.get_pokemon_by_name("pikachu")
        if pikachu_fr:
            print(f"OK Trouve: {pikachu_fr['name']}")

    # Test 4: Types disponibles
    print(f"\nTest 4: Types disponibles")
    types = service.get_all_types()
    print(f"OK {len(types)} types: {', '.join(types[:5])}...")

    print("\nTests termines!")
