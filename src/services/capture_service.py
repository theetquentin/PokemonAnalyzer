"""
Service de capture d'écran et OCR
Gère la capture en temps réel et l'analyse OCR
"""
import json
from typing import Optional, Callable
from pathlib import Path
from core.entities import CaptureRegion, OCRResult


class CaptureService:
    """Service pour gérer la capture d'écran et l'OCR"""
    
    CONFIG_FILE = "screen_region.json"
    
    def __init__(self, ocr_module=None):
        """
        Args:
            ocr_module: Module OCR pour la reconnaissance
        """
        self.ocr = ocr_module
        self.region: Optional[CaptureRegion] = None
        self.live_capture_instance = None
    
    def set_region(self, region: CaptureRegion):
        """Définit la région de capture"""
        self.region = region
    
    def save_region(self) -> bool:
        """
        Sauvegarde la région de capture dans un fichier
        
        Returns:
            True si succès, False sinon
        """
        if not self.region:
            return False
        
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.region.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde région: {e}")
            return False
    
    def load_region(self) -> bool:
        """
        Charge la région de capture depuis le fichier
        
        Returns:
            True si succès, False sinon
        """
        try:
            config_path = Path(self.CONFIG_FILE)
            if not config_path.exists():
                return False
            
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.region = CaptureRegion.from_dict(data)
            return True
        except Exception as e:
            print(f"Erreur chargement région: {e}")
            return False
    
    def select_region_interactive(self) -> bool:
        """
        Sélectionne interactivement une région d'écran
        
        Returns:
            True si succès, False sinon
        """
        try:
            from infrastructure.ocr.screen_capture import LiveScreenOCR
            
            if self.live_capture_instance is None:
                self.live_capture_instance = LiveScreenOCR(self.ocr, lambda *args: None)
            
            success = self.live_capture_instance.select_region_interactive()
            
            if success and self.live_capture_instance.region:
                region_dict = self.live_capture_instance.region
                self.region = CaptureRegion(
                    left=region_dict['left'],
                    top=region_dict['top'],
                    width=region_dict['width'],
                    height=region_dict['height']
                )
            
            return success
        except Exception as e:
            print(f"Erreur sélection région: {e}")
            return False
    
    def start_live_capture(self, interval: float, callback: Callable,
                          sensitivity: int = 1, confidence: float = 0.6) -> bool:
        """
        Démarre la capture en temps réel

        Args:
            interval: Intervalle entre les captures (secondes)
            callback: Fonction appelée lors d'une détection
            sensitivity: Sensibilité de détection
            confidence: Seuil de confiance minimal

        Returns:
            True si démarré avec succès
        """
        try:
            from infrastructure.ocr.screen_capture import LiveScreenOCR

            if not self.region:
                print("Erreur: Aucune region de capture definie")
                return False

            # Note: L'OCR peut être None, la capture fonctionnera mais l'analyse OCR sera désactivée
            if self.live_capture_instance is None:
                self.live_capture_instance = LiveScreenOCR(self.ocr, callback)
            else:
                # Met à jour le callback si l'instance existe déjà
                self.live_capture_instance.callback = callback

            # Configure la région
            self.live_capture_instance.region = self.region.to_dict()
            self.live_capture_instance.set_sensitivity(sensitivity)
            self.live_capture_instance.set_confidence_threshold(confidence)

            return self.live_capture_instance.start_live_capture(interval)
        except Exception as e:
            print(f"Erreur démarrage capture: {e}")
            return False
    
    def stop_live_capture(self):
        """Arrête la capture en temps réel"""
        if self.live_capture_instance:
            self.live_capture_instance.stop_live_capture()
    
    def capture_single(self) -> Optional[any]:
        """
        Effectue une capture unique
        
        Returns:
            Image capturée ou None
        """
        if not self.live_capture_instance or not self.region:
            return None
        
        return self.live_capture_instance.capture_region()
    
    def analyze_image(self, image_path: str, confidence_threshold: float = 0.6) -> OCRResult:
        """
        Analyse une image avec l'OCR
        
        Args:
            image_path: Chemin de l'image
            confidence_threshold: Seuil de confiance minimal
            
        Returns:
            OCRResult avec les résultats
        """
        if not self.ocr:
            return OCRResult(
                success=False,
                pokemon_name=None,
                confidence=0.0,
                detected_text=None,
                alternatives=[],
                error="OCR non disponible"
            )
        
        try:
            result = self.ocr.recognize_pokemon(image_path, confidence_threshold)
            
            return OCRResult(
                success=result.get('success', False),
                pokemon_name=result.get('pokemon_name'),
                confidence=result.get('confidence', 0.0),
                detected_text=result.get('detected_text'),
                alternatives=result.get('alternatives', []),
                error=result.get('error')
            )
        except Exception as e:
            return OCRResult(
                success=False,
                pokemon_name=None,
                confidence=0.0,
                detected_text=None,
                alternatives=[],
                error=str(e)
            )
    
    def is_capturing(self) -> bool:
        """Vérifie si une capture est en cours"""
        return (self.live_capture_instance is not None and 
                hasattr(self.live_capture_instance, 'is_running') and
                self.live_capture_instance.is_running)

