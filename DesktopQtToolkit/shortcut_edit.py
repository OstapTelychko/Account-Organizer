from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QKeyEvent


QKey = Qt.Key
QModifier = Qt.KeyboardModifier

class ShortcutCaptureEdit(QLineEdit):
    """A line edit that captures keyboard shortcuts."""
        
    def __init__(self, parent:QWidget|None=None) -> None:
        super().__init__(parent)

        self.setReadOnly(True)
        self.setPlaceholderText("Press shortcut keys...")
        self.key_sequence = QKeySequence()
        

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Capture key press events and convert them to shortcut sequences."""

        if event.key() in (QKey.Key_Control, QKey.Key_Shift, QKey.Key_Alt, QKey.Key_Meta):
            return
            
        modifiers = event.modifiers()        
        key = event.key()
            
        if key:
            sequence = QKeySequence(modifiers | QKey(key))#type: ignore[operator] #Mypy doesn't allow the | operator for KeyboardModifier and Key
            self.key_sequence = sequence
            display_text = sequence.toString()
                
            self.setText(display_text)
            
        event.accept()
        

    def clear(self) -> None:
        """Clear the shortcut."""

        super().clear()
        self.key_sequence = QKeySequence()
        

    def getKeySequence(self) -> QKeySequence:
        """Return the current key sequence."""
    
        return self.key_sequence