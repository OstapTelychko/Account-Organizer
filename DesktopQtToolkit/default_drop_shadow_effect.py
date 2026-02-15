from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget



class DefaultDropShadowEffect(QGraphicsDropShadowEffect):
    """Default drop shadow effect for the application."""

    def __init__(self, parent: QWidget | None = None, focused: bool = False) -> None:
        super().__init__(parent)

        if focused:
            blur_radius = 20.0
            color = QColor(70, 120, 255)
        else:
            blur_radius = 15.0
            color = QColor(0, 0, 0)
            
        x_offset = 0.0
        y_offset = 0.0


        self.setBlurRadius(blur_radius)
        self.setXOffset(x_offset)
        self.setYOffset(y_offset)
        self.setColor(color)


