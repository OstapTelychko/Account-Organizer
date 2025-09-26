from PySide6.QtWidgets import QListWidget, QWidget, QGraphicsDropShadowEffect
from GUI.gui_constants import BASIC_FONT, SHADOW_EFFECT_ARGUMENTS



def create_list_widget(parent:QWidget|None = None) -> QListWidget:
    """This function is used to create a default QListWidget with some basic properties set."""
    list_widget = QListWidget(parent)
    list_widget.setFont(BASIC_FONT)
    list_widget.setWordWrap(True)
    list_widget.setGraphicsEffect(QGraphicsDropShadowEffect(list_widget, **SHADOW_EFFECT_ARGUMENTS))
    return list_widget
