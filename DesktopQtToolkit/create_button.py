from __future__ import annotations
from PySide6.QtWidgets import QPushButton
from GUI.gui_constants import BASIC_FONT


def create_button(button_text:str, size:tuple[int, int], css_class:str="button") -> QPushButton:
    """Create a button with the specified text, size, and CSS class.
    
        Arguments
        ---------
            `button_text` : (str) - Text to be displayed on the button.
            `size` : (tuple[int]) - Size of the button in pixels (width, height).
            `css_class` : (str) - CSS class for styling the button.
        Returns
        -------
            `QPushButton` - A button widget with the specified properties.
    """

    button = QPushButton(button_text)
    button.setFont(BASIC_FONT)
    button.setMinimumSize(*size)
    button.setMaximumSize(*size)
    button.setProperty("class", css_class)
    return button