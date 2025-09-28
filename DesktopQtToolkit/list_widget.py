from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QListWidget, QGraphicsDropShadowEffect, QScroller

from GUI.gui_constants import BASIC_FONT, SHADOW_EFFECT_ARGUMENTS
from DesktopQtToolkit.qrich_text_delegate import QRichTextDelegate

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QWheelEvent



class CustomListWidget(QListWidget):
    """A QListWidget subclass with enhanced scrolling behavior and rich text support."""

    def __init__(self, parent:QWidget|None = None):
        super().__init__(parent)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(12)  # smaller step for smoother feel

        self.setFont(BASIC_FONT)
        self.setSpacing(0)

        self.setWordWrap(True)
        self.setGraphicsEffect(QGraphicsDropShadowEffect(self, **SHADOW_EFFECT_ARGUMENTS))
        self.setItemDelegate(QRichTextDelegate(self))

        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(12)
        QScroller.grabGesture(self.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
    

    def wheelEvent(self, event:QWheelEvent) -> None:
        "Prevents scrolling out of widget when TableWidget run out of rows and is nested into a ScrollArea"

        vertical_scrollbar = self.verticalScrollBar()
        if vertical_scrollbar.isVisible() and vertical_scrollbar.minimum() < vertical_scrollbar.maximum():
            super().wheelEvent(event)
            event.accept()
        else:
            event.ignore()