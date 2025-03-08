from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent





class HorizontalScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().x() == 0:
            delta = event.angleDelta().y()
            new_value = self.horizontalScrollBar().value() - delta
            self.horizontalScrollBar().setValue(new_value)
        else:
            super().wheelEvent(event)