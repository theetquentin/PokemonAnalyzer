"""
Module OCR pour la reconnaissance de noms de Pokémon dans les images
Utilise Tesseract et OpenCV pour le préprocessing d'images
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import difflib
from typing import List, Tuple, Optional, Dict
import os
import unicodedata

# Configure le chemin de Tesseract depuis l'environnement
import sys
from pathlib import Path as PathLib

# Priorité 1: TESSERACT_CMD (défini par le runtime hook PyInstaller)
if 'TESSERACT_CMD' in os.environ:
    pytesseract.pytesseract.tesseract_cmd = os.environ['TESSERACT_CMD']
# Priorité 2: Détection automatique si exécutable compilé (PyInstaller/Nuitka)
elif getattr(sys, 'frozen', False):
    # Mode exécutable compilé
    print("[DEBUG] Mode exécutable détecté")

    if hasattr(sys, '_MEIPASS'):
        # PyInstaller (--onefile ou --onedir)
        exe_dir = PathLib(sys._MEIPASS)
        print(f"[DEBUG] PyInstaller détecté, dossier extraction: {exe_dir}")
    else:
        # Nuitka (--onefile ou --standalone)
        # En mode --onefile, les fichiers sont extraits dans un dossier temporaire
        print(f"[DEBUG] Nuitka détecté")
        
        # DEBUG: Affiche tous les chemins pour comprendre où on est
        print(f"[DEBUG] sys.executable = {sys.executable}")
        print(f"[DEBUG] __file__ = {__file__}")
        print(f"[DEBUG] sys.argv[0] = {sys.argv[0] if sys.argv else 'N/A'}")
        
        # En mode --onefile Nuitka, il faut trouver le dossier d'extraction temporaire
        # Plusieurs méthodes à essayer :
        
        # Méthode 1: Dossier basé sur __file__ (le plus fiable pour --onefile)
        # __file__ pointe vers le fichier .pyc dans le dossier temporaire
        # Structure probable: TEMP/onefile_XXX/infrastructure/ocr/tesseract_ocr.pyc
        # Donc on remonte de 3 niveaux pour atteindre la racine
        exe_dir_1 = PathLib(__file__).resolve().parent.parent.parent
        print(f"[DEBUG] Méthode 1 (__file__.parent x3): {exe_dir_1}")
        print(f"[DEBUG]   - Contenu: {list(exe_dir_1.iterdir())[:10] if exe_dir_1.exists() else 'N/A'}")
        
        # Méthode 2: Dossier de sys.executable
        exe_dir_2 = PathLib(sys.executable).parent
        print(f"[DEBUG] Méthode 2 (sys.executable.parent): {exe_dir_2}")
        
        # Méthode 3: Dossier courant (certaines versions de Nuitka l'utilisent)
        exe_dir_3 = PathLib.cwd()
        print(f"[DEBUG] Méthode 3 (cwd): {exe_dir_3}")
        
        # Méthode 4: Dossier de sys.argv[0]
        exe_dir_4 = PathLib(sys.argv[0]).parent if sys.argv else None
        print(f"[DEBUG] Méthode 4 (sys.argv[0].parent): {exe_dir_4}")
        
        # Méthode 5: Variable d'environnement NUITKA_ONEFILE_PARENT (si définie)
        exe_dir_5 = PathLib(os.environ['NUITKA_ONEFILE_PARENT']) if 'NUITKA_ONEFILE_PARENT' in os.environ else None
        print(f"[DEBUG] Méthode 5 (NUITKA_ONEFILE_PARENT): {exe_dir_5}")
        
        # Teste chaque méthode pour voir laquelle contient 'tesseract/'
        possible_base_dirs = [d for d in [exe_dir_1, exe_dir_2, exe_dir_3, exe_dir_4, exe_dir_5] if d]
        
        exe_dir = None
        print(f"[DEBUG] Recherche de 'tesseract/' dans {len(possible_base_dirs)} emplacements...")
        for i, base_dir in enumerate(possible_base_dirs, 1):
            tesseract_subdir = base_dir / 'tesseract'
            print(f"[DEBUG] Essai {i}: {tesseract_subdir} -> {'EXISTE' if tesseract_subdir.exists() else 'N/A'}")
            if tesseract_subdir.exists():
                exe_dir = base_dir
                print(f"[DEBUG] ✓ Dossier d'extraction trouvé: {exe_dir}")
                break
        
        if not exe_dir:
            # Fallback: utilise le premier dossier de la liste
            exe_dir = exe_dir_1
            print(f"[DEBUG] ⚠ Aucun dossier avec 'tesseract/' trouvé")
            print(f"[DEBUG] Utilisation du dossier par défaut: {exe_dir}")

    # Cherche Tesseract dans plusieurs emplacements possibles
    possible_locations = [
        exe_dir / 'tesseract' / 'tesseract.exe',
        exe_dir / 'tesseract.exe',  # Directement dans le dossier de l'exe
        exe_dir.parent / 'tesseract' / 'tesseract.exe',
    ]

    print(f"[DEBUG] Recherche de Tesseract dans :")
    tesseract_found = False
    for tesseract_path in possible_locations:
        print(f"  - {tesseract_path}")
        if tesseract_path.exists():
            print(f"[DEBUG] ✓ Tesseract trouvé : {tesseract_path}")
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_path)

            # Cherche tessdata
            tessdata_locations = [
                tesseract_path.parent / 'tessdata',
                tesseract_path.parent.parent / 'tessdata',
            ]
            for tessdata_dir in tessdata_locations:
                if tessdata_dir.exists():
                    print(f"[DEBUG] ✓ tessdata trouvé : {tessdata_dir}")
                    os.environ['TESSDATA_PREFIX'] = str(tessdata_dir)
                    break
            tesseract_found = True
            break

    if not tesseract_found:
        print(f"[DEBUG] ✗ Tesseract NON trouvé dans l'exécutable")
        print(f"[DEBUG] Contenu du dossier exe: {list(exe_dir.iterdir()) if exe_dir.exists() else 'N/A'}")
# Priorité 3: TESSERACT_PATH (défini manuellement par l'utilisateur)
elif 'TESSERACT_PATH' in os.environ:
    pytesseract.pytesseract.tesseract_cmd = os.environ['TESSERACT_PATH']
# Priorité 4: Chemins standards sur Windows
else:
    import platform
    if platform.system() == "Windows":
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

class TesseractOCR:
    """Classe principale pour la reconnaissance OCR de noms Pokémon"""
    
    def __init__(self, pokemon_names_list: List[str] = None):
        """
        Initialise le module OCR
        
        Args:
            pokemon_names_list: Liste des noms de Pokémon pour la correction
        """
        self.pokemon_names = pokemon_names_list or []
        self.normalized_names = {self._normalize_name(name): name for name in self.pokemon_names}
        
        # Configuration Tesseract
        self.tesseract_config = {
            'default': '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ♀♂.-',
            'single_line': '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ♀♂.-',
            'single_word': '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ♀♂.-',
            'french': '--oem 3 --psm 6 -l fra',
            'japanese': '--oem 3 --psm 6 -l jpn',
            'multi': '--oem 3 --psm 6 -l eng+fra+jpn'
        }
        
        # Patterns de nettoyage du texte
        self.cleanup_patterns = [
            (r'[^\w\sÀ-ÿ♀♂.-]', ''),  # Supprime les caractères spéciaux sauf accents
            (r'\s+', ' '),              # Normalise les espaces
            (r'^\s+|\s+$', ''),         # Supprime espaces début/fin
            (r'(?i)^(n°|no|#)\s*\d+\s*', ''),  # Supprime numéros Pokédex
            (r'(?i)\b(niveau?|lv|lvl)\s*\d+\b', ''),  # Supprime niveaux
            (r'(?i)\b(cp|pc)\s*\d+\b', ''),  # Supprime CP/PC
            (r'\d+', ''),               # Supprime les chiffres restants
        ]
    
    def update_pokemon_names(self, pokemon_names_list: List[str]):
        """
        Met à jour la liste des noms de Pokémon pour la reconnaissance OCR
        Utilisé lors du changement de langue

        Args:
            pokemon_names_list: Nouvelle liste des noms de Pokémon
        """
        self.pokemon_names = pokemon_names_list or []
        self.normalized_names = {self._normalize_name(name): name for name in self.pokemon_names}
        
    def check_language_availability(self, lang_code: str) -> bool:
        """Vérifie si le pack de langue est installé"""
        try:
            available_langs = pytesseract.get_languages()
            # Mapping code custom -> code tesseract
            tess_code = {
                'ja': 'jpn',
                'jp': 'jpn',
                'fr': 'fra',
                'en': 'eng'
            }.get(lang_code, lang_code)
            
            if tess_code not in available_langs:
                print(f"[ATTENTION] Pack de langue '{tess_code}' manquant pour Tesseract! (Disponibles: {available_langs})")
                return False
            return True
        except Exception as e:
            print(f"[ERREUR] Impossible de vérifier les langues Tesseract: {e}")
            return False

    def _normalize_name(self, name: str) -> str:
        """Normalise un nom pour la comparaison (gère tous les accents français)"""
        # Remplacements spéciaux avant normalisation (caractères qui ne se normalisent pas bien)
        replacements = {
            'ç': 'c', 'Ç': 'c',
            'œ': 'oe', 'Œ': 'oe',
            'æ': 'ae', 'Æ': 'ae',
            '♀': 'f', '♂': 'm'
        }

        for old, new in replacements.items():
            name = name.replace(old, new)

        # Supprime les accents (NFD décompose les accents, puis on supprime les marques diacritiques)
        # Cela gère: à â é è ê ë î ï ô ù û ü ÿ, etc.
        name = unicodedata.normalize('NFD', name)
        name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')

        # Minuscules et suppression des caractères spéciaux
        name = name.lower()
        name = name.replace(".", "").replace(" ", "").replace("-", "").replace("'", "")
        return name
    
    def preprocess_image(self, image_path: str, method: str = 'adaptive') -> np.ndarray:
        """
        Préprocesse l'image pour améliorer la reconnaissance OCR
        
        Args:
            image_path: Chemin vers l'image
            method: Méthode de préprocessing ('adaptive', 'threshold', 'enhanced', 'all')
        
        Returns:
            Image préprocessée
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image non trouvée: {image_path}")
        
        # Lecture de l'image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Impossible de lire l'image: {image_path}")
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if method == 'adaptive':
            # Seuillage adaptatif
            processed = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        
        elif method == 'threshold':
            # Seuillage d'Otsu
            _, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        elif method == 'enhanced':
            # Amélioration avancée
            # Égalisation d'histogramme
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Débruitage
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            # Seuillage adaptatif
            processed = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphologie pour nettoyer
            kernel = np.ones((2,2), np.uint8)
            processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
        
        else:  # method == 'all'
            # Retourne multiple versions pour test
            return {
                'adaptive': self.preprocess_image(image_path, 'adaptive'),
                'threshold': self.preprocess_image(image_path, 'threshold'),
                'enhanced': self.preprocess_image(image_path, 'enhanced')
            }
        
        return processed
    
    def enhance_with_pil(self, image_path: str) -> Image:
        """Améliore l'image avec PIL pour une meilleure reconnaissance"""
        img = Image.open(image_path)
        
        # Conversion en niveaux de gris
        if img.mode != 'L':
            img = img.convert('L')
        
        # Redimensionnement si trop petite
        width, height = img.size
        if width < 200 or height < 50:
            scale_factor = max(200/width, 50/height, 2.0)
            new_size = (int(width * scale_factor), int(height * scale_factor))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Amélioration du contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Amélioration de la netteté
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        
        # Filtre pour réduire le bruit
        img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img
    
    def extract_text_multiple_methods(self, image_path: str) -> List[Dict[str, str]]:
        """
        Extrait le texte avec plusieurs méthodes pour maximiser la réussite
        
        Returns:
            Liste des résultats avec méthode utilisée et confiance
        """
        results = []
        try:
            # OPTIMISATION: Test dans l'ordre et arrêt dès qu'un résultat est trouvé
            
            # Méthode 1 (RAPIDE): PIL enhancement + multi-langue (fonctionne 80% du temps)
            try:
                enhanced_img = self.enhance_with_pil(image_path)
                text = pytesseract.image_to_string(enhanced_img, config=self.tesseract_config['multi']).strip()
                if text:
                    results.append({
                        'text': text,
                        'method': 'pil_enhanced_multi',
                        'confidence': 0.9
                    })
                    return results  # STOP ICI si trouvé! (1 seul appel OCR)
            except Exception:
                pass
            
            # Méthode 2 (FALLBACK): Adaptive threshold
            try:
                processed_img = self.preprocess_image(image_path, 'adaptive')
                text = pytesseract.image_to_string(processed_img, config=self.tesseract_config['multi']).strip()
                if text:
                    results.append({
                        'text': text,
                        'method': 'opencv_adaptive_multi',
                        'confidence': 0.8
                    })
                    return results  # STOP ICI (2 appels OCR max)
            except Exception:
                pass
            
            # Méthode 3 (LAST RESORT): Image originale
            try:
                from PIL import Image
                original_img = Image.open(image_path)
                text = pytesseract.image_to_string(original_img, config=self.tesseract_config['multi']).strip()
                if text:
                    results.append({
                        'text': text,
                        'method': 'original_multi',
                        'confidence': 0.7
                    })
            except Exception:
                pass
        except Exception as e:
            print(f"Erreur lors de l'extraction OCR: {e}")
        return results
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte extrait par OCR"""
        cleaned = text
        
        # Applique les patterns de nettoyage
        for pattern, replacement in self.cleanup_patterns:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # Corrections spécifiques OCR
        ocr_corrections = {
            '0': 'o', '1': 'l', '5': 's', '8': 'b',
            'rn': 'm', 'vv': 'w', 'ii': 'n',
            '|': 'l', '¡': 'i', '§': 's'
        }
        
        for wrong, correct in ocr_corrections.items():
            cleaned = cleaned.replace(wrong, correct)
        
        return cleaned.strip()
    
    def find_best_pokemon_match(self, text: str, max_suggestions: int = 5) -> List[Dict[str, any]]:
        """
        Trouve le meilleur match de nom Pokémon dans le texte
        
        Returns:
            Liste des matches avec scores de confiance
        """
        if not self.pokemon_names:
            return []
        
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        matches = []
        
        # Test avec le texte complet
        normalized_text = self._normalize_name(cleaned_text)
        text_matches = difflib.get_close_matches(
            normalized_text, self.normalized_names.keys(), n=max_suggestions, cutoff=0.6
        )
        
        for match in text_matches:
            original_name = self.normalized_names[match]
            similarity = difflib.SequenceMatcher(None, normalized_text, match).ratio()
            matches.append({
                'name': original_name,
                'similarity': similarity,
                'method': 'full_text',
                'original_text': cleaned_text
            })
        
        # Test avec chaque mot individuellement
        for word in words:
            if len(word) >= 3:  # Ignore les mots trop courts
                normalized_word = self._normalize_name(word)
                word_matches = difflib.get_close_matches(
                    normalized_word, self.normalized_names.keys(), n=3, cutoff=0.7
                )
                
                for match in word_matches:
                    original_name = self.normalized_names[match]
                    similarity = difflib.SequenceMatcher(None, normalized_word, match).ratio()
                    matches.append({
                        'name': original_name,
                        'similarity': similarity * 0.9,  # Légèrement pénalisé car partiel
                        'method': 'word_match',
                        'original_text': word
                    })
        
        # Supprime les doublons et trie par similarité
        unique_matches = {}
        for match in matches:
            name = match['name']
            if name not in unique_matches or match['similarity'] > unique_matches[name]['similarity']:
                unique_matches[name] = match
        
        final_matches = list(unique_matches.values())
        final_matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return final_matches[:max_suggestions]
    
    def recognize_pokemon(self, image_path: str, confidence_threshold: float = 0.6) -> Dict[str, any]:
        """
        Fonction principale pour reconnaître un Pokémon dans une image
        
        Returns:
            Dictionnaire avec le résultat de la reconnaissance
        """
        result = {
            'success': False,
            'pokemon_name': None,
            'confidence': 0.0,
            'alternatives': [],
            'ocr_results': [],
            'error': None
        }
        
        try:
            # Extraction du texte avec plusieurs méthodes
            ocr_results = self.extract_text_multiple_methods(image_path)
            result['ocr_results'] = ocr_results
            
            if not ocr_results:
                result['error'] = "Aucun texte détecté dans l'image"
                return result
            
            # Analyse de chaque résultat OCR
            all_matches = []
            
            for ocr_result in ocr_results:
                text = ocr_result['text']
                method_confidence = ocr_result['confidence']
                
                pokemon_matches = self.find_best_pokemon_match(text)
                
                for match in pokemon_matches:
                    # Score combiné: similarité * confiance méthode
                    combined_score = match['similarity'] * method_confidence
                    all_matches.append({
                        **match,
                        'ocr_method': ocr_result['method'],
                        'combined_confidence': combined_score
                    })
            
            if not all_matches:
                result['error'] = "Aucun nom de Pokémon reconnu"
                return result
            
            # Trie par confiance combinée
            all_matches.sort(key=lambda x: x['combined_confidence'], reverse=True)
            
            # Meilleur match
            best_match = all_matches[0]
            
            if best_match['combined_confidence'] >= confidence_threshold:
                result['success'] = True
                result['pokemon_name'] = best_match['name']
                result['confidence'] = best_match['combined_confidence']
            
            # Alternatives (top 5)
            result['alternatives'] = all_matches[:5]
            
        except Exception as e:
            result['error'] = f"Erreur lors de la reconnaissance: {str(e)}"
        
        return result
    
    def recognize_multiple_pokemon(self, image_path: str, max_pokemon: int = 3,
                                   confidence_threshold: float = 0.6) -> Dict[str, any]:
        """
        Reconnaît jusqu'à plusieurs Pokémon dans une même image (pour combats duo/trio)

        Args:
            image_path: Chemin de l'image
            max_pokemon: Nombre maximum de Pokémon à détecter (défaut: 3)
            confidence_threshold: Seuil de confiance minimal

        Returns:
            Dictionnaire avec liste des Pokémon détectés
        """
        result = {
            'success': False,
            'pokemon_count': 0,
            'pokemons': [],
            'ocr_results': [],
            'error': None
        }

        try:
            # Extraction du texte avec plusieurs méthodes
            ocr_results = self.extract_text_multiple_methods(image_path)
            result['ocr_results'] = ocr_results

            if not ocr_results:
                result['error'] = "Aucun texte détecté dans l'image"
                return result

            # Collecte tous les matches possibles
            # IMPORTANT: Ne prend que le MEILLEUR match par texte OCR pour éviter Rattata + Rattatac du même texte
            all_matches = []
            detected_names = set()

            print(f"\n📝 Textes OCR détectés: {len(ocr_results)}")
            for i, ocr_result in enumerate(ocr_results):
                text = ocr_result['text']
                method = ocr_result['method']
                method_confidence = ocr_result['confidence']
                print(f"  {i+1}. [{method}] '{text}' (conf: {method_confidence:.2%})")

                # IMPORTANT: Stratégie intelligente pour gérer les textes multi-mots
                # 1. D'abord, essaie de matcher le texte complet (pour "M. Mime", "Mime Jr.", etc.)
                # 2. Si pas de match satisfaisant ET plusieurs mots, essaie mot par mot (pour "Rattata Keldeo")

                # Essaie d'abord le texte complet
                pokemon_matches_full = self.find_best_pokemon_match(text, max_suggestions=max_pokemon * 2)

                best_match_full = None
                best_score_full = 0

                for match in pokemon_matches_full:
                    pokemon_name = match['name']
                    combined_score = match['similarity'] * method_confidence

                    if combined_score >= confidence_threshold and pokemon_name.lower() not in detected_names:
                        if combined_score > best_score_full:
                            best_match_full = {
                                **match,
                                'ocr_method': ocr_result['method'],
                                'ocr_text': text,
                                'combined_confidence': combined_score
                            }
                            best_score_full = combined_score

                # Si bon match trouvé avec le texte complet OU un seul mot, on l'utilise
                words = self.clean_text(text).split()

                if best_match_full and (len(words) == 1 or best_score_full >= 0.75):
                    # Bon match avec texte complet ou texte simple
                    print(f"     → Match texte complet: {best_match_full['name']} ({best_score_full:.2%})")
                    all_matches.append(best_match_full)
                    detected_names.add(best_match_full['name'].lower())

                elif len(words) > 1:
                    # Plusieurs mots ET pas de bon match complet → analyse mot par mot (mode duo/trio)
                    print(f"     ⚡ Texte multi-mots sans bon match complet, analyse par mot...")
                    for word in words:
                        if len(word) < 3:  # Ignore les mots trop courts
                            continue

                        pokemon_matches = self.find_best_pokemon_match(word, max_suggestions=1)

                        for match in pokemon_matches:
                            pokemon_name = match['name']
                            combined_score = match['similarity'] * method_confidence

                            if combined_score >= confidence_threshold and pokemon_name.lower() not in detected_names:
                                print(f"        → Mot '{word}' → {pokemon_name} ({combined_score:.2%})")
                                all_matches.append({
                                    **match,
                                    'ocr_method': ocr_result['method'],
                                    'ocr_text': word,
                                    'combined_confidence': combined_score
                                })
                                detected_names.add(pokemon_name.lower())
                                break  # Un seul match par mot

                elif best_match_full:
                    # Match moyen avec texte complet, mais on le prend quand même
                    print(f"     → Match: {best_match_full['name']} ({best_score_full:.2%})")
                    all_matches.append(best_match_full)
                    detected_names.add(best_match_full['name'].lower())
                else:
                    print(f"     → Aucun match au-dessus du seuil")

            if not all_matches:
                result['error'] = "Aucun Pokémon reconnu avec confiance suffisante"
                return result

            # Trie par confiance et prend les N meilleurs
            all_matches.sort(key=lambda x: x['combined_confidence'], reverse=True)

            # Debug: affiche les matches trouvés
            print(f"\n🔍 Matches trouvés (triés par confiance):")
            for i, m in enumerate(all_matches[:5]):  # Affiche les 5 premiers
                print(f"  {i+1}. {m['name']} - Confiance: {m['combined_confidence']:.2%}")

            # Filtre les noms similaires (évite Rattata + Rattatac)
            # Si un nom est contenu dans un autre, garde celui avec la meilleure confiance
            filtered_matches = []
            for match in all_matches:
                should_add = True
                match_name = match['name'].lower()

                # Vérifie si ce match est similaire à un match déjà ajouté
                for existing in filtered_matches:
                    existing_name = existing['name'].lower()

                    # Si l'un est contenu dans l'autre (sous-chaîne)
                    if (match_name in existing_name or existing_name in match_name) and \
                       match_name != existing_name:
                        print(f"  [FILTER] '{match['name']}' (conf: {match['combined_confidence']:.2%}) ressemble à '{existing['name']}' (conf: {existing['combined_confidence']:.2%}) - Ignoré")
                        # Le match actuel a forcément une confiance plus faible car liste triée
                        # Donc on ne l'ajoute pas
                        should_add = False
                        break

                if should_add:
                    filtered_matches.append(match)
                    print(f"  [OK] Ajouté: {match['name']} (conf: {match['combined_confidence']:.2%})")

                # Limite au nombre max de Pokémon
                if len(filtered_matches) >= max_pokemon:
                    break

            selected_pokemon = filtered_matches
            print(f"\n[RESULT] Pokémon sélectionnés finaux: {[p['name'] for p in selected_pokemon]}\n")

            # Formate les résultats
            result['success'] = True
            result['pokemon_count'] = len(selected_pokemon)
            result['pokemons'] = [
                {
                    'pokemon_name': p['name'],
                    'confidence': p['combined_confidence'],
                    'alternatives': [m for m in all_matches if m['name'] != p['name']][:3]
                }
                for p in selected_pokemon
            ]

        except Exception as e:
            result['error'] = f"Erreur lors de la reconnaissance: {str(e)}"

        return result

    def batch_recognize(self, image_paths: List[str], confidence_threshold: float = 0.6) -> List[Dict[str, any]]:
        """Reconnaît plusieurs images en lot"""
        results = []

        for i, image_path in enumerate(image_paths):
            print(f"Traitement {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
            result = self.recognize_pokemon(image_path, confidence_threshold)
            result['image_path'] = image_path
            results.append(result)

        return results
    
    def save_debug_images(self, image_path: str, output_dir: str = "debug_ocr"):
        """Sauvegarde les images préprocessées pour debug"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Sauvegarde des différentes versions preprocessing
        methods = ['adaptive', 'threshold', 'enhanced']
        
        for method in methods:
            try:
                processed = self.preprocess_image(image_path, method)
                output_path = os.path.join(output_dir, f"{base_name}_{method}.png")
                cv2.imwrite(output_path, processed)
                print(f"Debug image sauvée: {output_path}")
            except Exception as e:
                print(f"Erreur sauvegarde {method}: {e}")
        
        # Sauvegarde version PIL
        try:
            enhanced = self.enhance_with_pil(image_path)
            output_path = os.path.join(output_dir, f"{base_name}_pil_enhanced.png")
            enhanced.save(output_path)
            print(f"Debug image sauvée: {output_path}")
        except Exception as e:
            print(f"Erreur sauvegarde PIL: {e}")


def test_ocr_setup():
    """Teste si Tesseract est correctement installé"""
    try:
        # Test basique
        test_image = np.ones((100, 300), dtype=np.uint8) * 255
        cv2.putText(test_image, "TEST", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
        
        result = pytesseract.image_to_string(test_image)
        
        if "TEST" in result.upper():
            print("Tesseract fonctionne correctement")
            return True
        else:
            print("Tesseract installe mais reconnaissance imparfaite")
            return False
    
    except Exception as e:
        print(f"Erreur Tesseract: {e}")
        print("Installez Tesseract: https://github.com/tesseract-ocr/tesseract")
        return False
