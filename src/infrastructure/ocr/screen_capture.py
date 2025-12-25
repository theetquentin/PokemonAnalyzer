# screen_capture_ocr.py
"""
Module de capture d'écran en temps réel - Version minimale pour PyQt5
"""

import json
import time
import threading
from typing import Optional, Dict, Callable
from PIL import Image, ImageGrab
import tkinter as tk
from tkinter import Canvas


class LiveScreenOCR:
    """Gestionnaire de capture d'écran en temps réel"""
    
    def __init__(self, ocr_module=None, pokemon_analyzer_callback=None):
        """
        Initialise le module de capture
        
        Args:
            ocr_module: Instance du module OCR
            pokemon_analyzer_callback: Fonction callback pour les détections
        """
        self.ocr = ocr_module
        self.callback = pokemon_analyzer_callback
        self.region = None
        self.is_running = False
        self.capture_thread = None
        self.min_consecutive = 1
        self.confidence_threshold = 0.6
        self.max_pokemon = 1  # Nombre max de pokémon à détecter (1, 2 ou 3)
        self.last_detection = None
        self.consecutive_count = 0
        self.save_debug_images = False
        self.use_mss = False

        # Compteur de détections
        self.detection_count = {}
        self.last_confirmed_detection = None  # Dernière détection confirmée et envoyée au callback
    
    def select_region_interactive(self) -> bool:
        """Sélectionne une région d'écran de manière interactive"""
        try:
            # Crée une fenêtre transparente en plein écran
            root = tk.Tk()
            root.attributes('-fullscreen', True)
            root.attributes('-alpha', 0.3)
            root.attributes('-topmost', True)
            root.configure(background='gray')
            
            # Variables pour stocker la sélection
            self.selection_start = None
            self.selection_end = None
            self.selection_rect = None
            
            # Canvas pour dessiner la sélection
            canvas = Canvas(root, cursor="cross", highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            canvas.configure(background='gray')
            
            def on_mouse_down(event):
                self.selection_start = (event.x, event.y)
                if self.selection_rect:
                    canvas.delete(self.selection_rect)
            
            def on_mouse_drag(event):
                if self.selection_start:
                    if self.selection_rect:
                        canvas.delete(self.selection_rect)
                    
                    x1, y1 = self.selection_start
                    x2, y2 = event.x, event.y
                    
                    self.selection_rect = canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline='red',
                        width=3
                    )
            
            def on_mouse_up(event):
                self.selection_end = (event.x, event.y)
                
                if self.selection_start and self.selection_end:
                    x1, y1 = self.selection_start
                    x2, y2 = self.selection_end
                    
                    # Normalise les coordonnées
                    left = min(x1, x2)
                    top = min(y1, y2)
                    right = max(x1, x2)
                    bottom = max(y1, y2)
                    
                    self.region = {
                        'left': left,
                        'top': top,
                        'width': right - left,
                        'height': bottom - top
                    }
                    
                    root.quit()
            
            # Bind des événements souris
            canvas.bind('<Button-1>', on_mouse_down)
            canvas.bind('<B1-Motion>', on_mouse_drag)
            canvas.bind('<ButtonRelease-1>', on_mouse_up)
            
            # Bind ESC pour annuler
            root.bind('<Escape>', lambda e: root.quit())
            
            # Instructions
            label = tk.Label(
                root,
                text="Cliquez et glissez pour sélectionner la zone • ESC pour annuler",
                font=('Arial', 14, 'bold'),
                bg='black',
                fg='white',
                padx=20,
                pady=10
            )
            label.place(relx=0.5, rely=0.05, anchor='center')
            
            # Lance la boucle
            root.mainloop()
            root.destroy()
            
            return self.region is not None
            
        except Exception as e:
            print(f"[ERREUR] Erreur sélection région: {e}")
            return False
    
    def save_region_config(self, filename: str = "screen_region.json") -> bool:
        """Sauvegarde la configuration de région"""
        if not self.region:
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.region, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERREUR] Erreur sauvegarde région: {e}")
            return False
    
    def load_region_config(self, filename: str = "screen_region.json") -> bool:
        """Charge la configuration de région"""
        try:
            import os
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                self.region = json.load(f)
            return True
        except Exception as e:
            print(f"[ERREUR] Erreur chargement région: {e}")
            return False
    
    def capture_region(self) -> Optional[Image.Image]:
        """Capture la région sélectionnée"""
        if not self.region:
            return None
        
        try:
            # Utilise PIL ImageGrab
            bbox = (
                self.region['left'],
                self.region['top'],
                self.region['left'] + self.region['width'],
                self.region['top'] + self.region['height']
            )
            
            image = ImageGrab.grab(bbox)
            return image
            
        except Exception as e:
            print(f"[ERREUR] Erreur capture: {e}")
            return None
    
    def analyze_capture(self, image: Image.Image, multi_pokemon: bool = True, max_pokemon: int = 2) -> Dict:
        """
        Analyse une capture avec OCR

        Args:
            image: Image à analyser
            multi_pokemon: Si True, essaie de détecter plusieurs Pokémon (défaut: True)
            max_pokemon: Nombre maximum de Pokémon à détecter (1-3, défaut: 2)
        """
        if not self.ocr:
            return {
                'success': False,
                'error': 'Module OCR non disponible - Tesseract n\'est pas installé'
            }

        try:
            # Sauvegarde temporaire pour OCR
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                image.save(tmp.name)
                tmp_path = tmp.name

            # Analyse OCR - essaie d'abord multiple, puis simple si échec
            if multi_pokemon and max_pokemon > 1:
                result = self.ocr.recognize_multiple_pokemon(
                    tmp_path,
                    max_pokemon=max_pokemon,
                    confidence_threshold=self.confidence_threshold
                )

                # Si plusieurs Pokémon détectés, retourne ce format
                if result['success'] and result['pokemon_count'] > 1:
                    # Supprime le fichier temporaire
                    import os
                    os.unlink(tmp_path)
                    return result

                # Si un seul Pokémon détecté, convertit au format simple
                if result['success'] and result['pokemon_count'] == 1:
                    pkmn = result['pokemons'][0]
                    import os
                    os.unlink(tmp_path)
                    return {
                        'success': True,
                        'pokemon_name': pkmn['pokemon_name'],
                        'confidence': pkmn['confidence'],
                        'alternatives': pkmn.get('alternatives', [])
                    }

            # Mode simple ou si multi a échoué
            result = self.ocr.recognize_pokemon(
                tmp_path,
                confidence_threshold=self.confidence_threshold
            )

            # Supprime le fichier temporaire
            import os
            os.unlink(tmp_path)

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_live_capture(self, interval: float = 2.0, callback=None,
                          sensitivity: int = 1, confidence: float = 0.6) -> bool:
        """Démarre la capture en temps réel"""
        if not self.region:
            return False

        # Note: L'OCR peut être None - dans ce cas la capture fonctionnera
        # mais l'analyse OCR sera désactivée

        if self.is_running:
            return False

        # Configure les paramètres
        if callback:
            self.callback = callback
        self.set_sensitivity(sensitivity)
        self.set_confidence_threshold(confidence)


        self.is_running = True
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            args=(interval,),
            daemon=True
        )
        self.capture_thread.start()
        return True
    
    def stop_live_capture(self):
        """Arrête la capture en temps réel"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
    
    def _capture_loop(self, interval: float):
        """Boucle de capture"""
        print(f"🔄 Démarrage de la boucle de capture (intervalle: {interval}s)")
        capture_count = 0

        while self.is_running:
            try:
                capture_count += 1
                print(f"\n📸 Capture #{capture_count}...")

                # Capture
                image = self.capture_region()

                if image:

                    # Analyse
                    print(f"[OCR] Analyse OCR en cours (mode: {self.max_pokemon} pokémon max)...")
                    result = self.analyze_capture(image, multi_pokemon=True, max_pokemon=self.max_pokemon)

                    print(f"[OCR] Résultat OCR: success={result.get('success')}")

                    if result['success']:
                        # Gère le cas multi-pokémon
                        if 'pokemon_count' in result and result['pokemon_count'] > 1:
                            count = result['pokemon_count']
                            mode_label = "DUO" if count == 2 else "TRIO" if count == 3 else f"{count} Pokémon"

                            detection_key = "_".join(sorted([p['pokemon_name'] for p in result['pokemons']]))

                            # Vérifie les détections consécutives
                            if detection_key == self.last_detection:
                                self.consecutive_count += 1
                            else:
                                self.consecutive_count = 1
                                self.last_detection = detection_key

                            print(f"[DETECT] Détections consécutives: {self.consecutive_count}/{self.min_consecutive}")

                            # Appelle le callback si suffisamment de détections ET si c'est une nouvelle détection
                            if self.consecutive_count >= self.min_consecutive:
                                # Vérifie si c'est la même détection que la dernière confirmée
                                if detection_key != self.last_confirmed_detection:
                                    if self.callback:
                                        result['image'] = image
                                        # Format spécial pour multi-pokémon
                                        self.callback(None, None, result)
                                        self.last_confirmed_detection = detection_key

                        # Cas simple (1 seul pokémon)
                        else:
                            pokemon_name = result['pokemon_name']
                            confidence = result['confidence']


                            # Vérifie les détections consécutives
                            if pokemon_name == self.last_detection:
                                self.consecutive_count += 1
                            else:
                                self.consecutive_count = 1
                                self.last_detection = pokemon_name

                            print(f"[DETECT] Détections consécutives: {self.consecutive_count}/{self.min_consecutive}")

                            # Appelle le callback si suffisamment de détections ET si c'est une nouvelle détection
                            if self.consecutive_count >= self.min_consecutive:
                                # Vérifie si c'est la même détection que la dernière confirmée
                                if pokemon_name != self.last_confirmed_detection:
                                    if self.callback:
                                        # Ajoute l'image au résultat pour l'affichage
                                        result['image'] = image
                                        self.callback(pokemon_name, confidence, result)
                                        self.last_confirmed_detection = pokemon_name
                    else:
                        error = result.get('error', 'Aucune détection')
                else:
                    print(f"[ERREUR] Échec de la capture d'image")

                # Attente
                time.sleep(interval)

            except Exception as e:
                print(f"[ERREUR] Erreur boucle capture: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(interval)
    
    def set_sensitivity(self, min_consecutive: int):
        """Configure la sensibilité (nombre de détections consécutives)"""
        self.min_consecutive = max(1, min_consecutive)
    
    def set_confidence_threshold(self, threshold: float):
        """Configure le seuil de confiance OCR"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))

    def set_max_pokemon(self, max_pokemon: int):
        """Configure le nombre maximum de Pokémon à détecter (1-3)"""
        self.max_pokemon = max(1, min(3, max_pokemon))

    def enable_mss_capture(self, enable: bool):
        """Active/désactive la capture MSS (non utilisé ici)"""
        self.use_mss = enable

    def enable_debug_mode(self, enable: bool):
        """Active/désactive le mode debug"""
        self.save_debug_images = enable
