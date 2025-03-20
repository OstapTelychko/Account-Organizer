from __future__ import annotations
from typing import TYPE_CHECKING
from GUI.gui_constants import BASIC_FONT

if TYPE_CHECKING:
    from PySide6.QtWidgets import QPushButton

def create_button(button_text:str, size:tuple[int], css_class:str="button") -> QPushButton:
    button = QPushButton(text=button_text)
    button.setFont(BASIC_FONT)
    button.setMinimumSize(*size)
    button.setMaximumSize(*size)
    button.setProperty("class", css_class)
    return button