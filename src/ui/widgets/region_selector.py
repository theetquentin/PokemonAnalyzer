"""
Widget de sélection de région d'écran (remplace Tkinter)
"""
from PySide6.QtWidgets import QWidget, QApplication, QRubberBand
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QCursor

class RegionSelector(QWidget):
    """
    Overlay plein écran transparent pour sélectionner une zone
    """
    selection_confirmed = Signal(dict)  # {left, top, width, height}
    selection_cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)  # Assure la fermeture propre
        self.setCursor(Qt.CrossCursor)
        self.setWindowState(Qt.WindowFullScreen)
        
        # Active le focus clavier pour capturer les événements comme Echap
        self.setFocusPolicy(Qt.StrongFocus)
        
        # État de la sélection
        self.start_point = None
        self.end_point = None
        self.is_selecting = False
        
        # Instructions
        self.info_text = "Cliquez et glissez pour sélectionner la zone • ESC pour annuler"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fond semi-transparent gris
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # Zone de sélection (claire)
        if self.start_point and self.end_point:
            rect = QRect(self.start_point, self.end_point).normalized()
            
            # "Trou" transparent pour la sélection
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # Bordure rouge
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # Dimensions
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect.topLeft() - QPoint(0, 5), f"{rect.width()} x {rect.height()}")

        # Texte d'instruction (centré en haut)
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        text_rect = painter.fontMetrics().boundingRect(self.info_text)
        x = (self.width() - text_rect.width()) // 2
        y = 50
        
        # Fond noir pour le texte
        bg_rect = QRect(x - 10, y - text_rect.height(), text_rect.width() + 20, text_rect.height() + 10)
        painter.fillRect(bg_rect, QColor(0, 0, 0, 180))
        painter.drawText(x, y, self.info_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.end_point = event.pos()
            self.confirm_selection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.selection_cancelled.emit()
            self.close()

    def confirm_selection(self):
        if self.start_point and self.end_point:
            rect = QRect(self.start_point, self.end_point).normalized()
            # Seuil de 5 pixels minimum pour éviter les clics accidentels
            if rect.width() > 5 and rect.height() > 5:
                result = {
                    'left': rect.left(),
                    'top': rect.top(),
                    'width': rect.width(),
                    'height': rect.height()
                }
                # Cache immédiatement pour feedback visuel instantané
                self.hide()
                # Emit après hide pour éviter blocage visuel
                self.selection_confirmed.emit(result)
                self.close()
            else:
                # Sélection trop petite, ignore
                pass
