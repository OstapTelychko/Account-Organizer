from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import Qt, QPropertyAnimation

if TYPE_CHECKING:
    from PySide6.QtGui import QWheelEvent




class HorizontalScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.default_duration = 200
        self.animation = QPropertyAnimation(self.horizontalScrollBar(), b"value")
        self.animation.setDuration(self.default_duration)


    def wheelEvent(self, event:QWheelEvent):
        if event.angleDelta().x() == 0:
            delta = event.angleDelta().y()

            if delta < 0:
                speed_factor = max(1, -(delta / 100))
            else:
                speed_factor = max(1, (delta / 50))#it's harder to scroll up than down so we need to increase the speed
            delta *= speed_factor
            new_value = self.horizontalScrollBar().value() - delta

            self.animation.stop()
            self.animation.setEndValue(new_value)
            self.animation.start()
        else:
            super().wheelEvent(event)