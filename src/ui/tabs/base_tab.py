"""
Classe de base pour tous les onglets
Fournit des fonctionnalités communes
"""
from PySide6.QtWidgets import QWidget, QMessageBox


class BaseTab(QWidget):
    """Classe de base pour tous les onglets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """À implémenter par les classes filles"""
        raise NotImplementedError("init_ui doit être implémentée")
    
    def show_error(self, title: str, message: str):
        """Affiche un message d'erreur"""
        QMessageBox.critical(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Affiche un avertissement"""
        QMessageBox.warning(self, title, message)
    
    def show_info(self, title: str, message: str):
        """Affiche une information"""
        QMessageBox.information(self, title, message)
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        Demande une confirmation à l'utilisateur
        
        Returns:
            True si l'utilisateur confirme
        """
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes

