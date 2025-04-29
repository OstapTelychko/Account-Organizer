from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QShortcut

if TYPE_CHECKING:
    from typing import Callable
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QKeySequence


class ShortcutsManager:
    """Manages shortcuts in the application and allows dynamic updates"""

    active_shortcuts:list[QShortcut] = []

    @staticmethod
    def add_shortcut(key_sequence:QKeySequence, parent:QWidget, action:Callable[[], None|int]) -> None:
        """Adds a shortcut to the application and connects it to an action"""

        shortcut = QShortcut(key_sequence, parent)
        shortcut.activated.connect(action)
        ShortcutsManager.active_shortcuts.append(shortcut)
    

    @staticmethod
    def clear_shortcuts() -> None:
        """Clears all active shortcuts"""
        
        for shortcut in ShortcutsManager.active_shortcuts:
            shortcut.setEnabled(False)
            shortcut.activated.disconnect()
            shortcut.setParent(None) #type: ignore[arg-type] #Mypy doesn't accept None as valid parent
            
        ShortcutsManager.active_shortcuts.clear()