from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel

class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)  # Signal that emits the index of the clicked image
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index  # Store the index of the image

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)  # Emit the index when clicked
