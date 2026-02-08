from PySide6.QtWidgets import QLabel
from GUI.gui_constants import BASIC_FONT



class DefaultLabel(QLabel):
    """A QLabel with default styling applied."""

    def __init__(self, text:str="", set_light_text: bool = False) -> None:
        super().__init__(text)
        self.setFont(BASIC_FONT)
        self.setWordWrap(True)

        if set_light_text:
            self.setProperty("class", "light-text")