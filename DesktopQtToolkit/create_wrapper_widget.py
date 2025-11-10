from PySide6.QtWidgets import QLayout, QWidget, QGraphicsDropShadowEffect, QHBoxLayout

from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS



def create_wrapper_widget(layout:QLayout) -> QWidget:
    """Create a wrapper widget with a given layout and shadow effect.
    
        Arguments
        ---------
            `layout` : (QLayoutChild) - The layout to be set for the wrapper widget.
        Returns
        -------
            `QWidget` - The created wrapper widget with the specified layout and shadow effect.
    """

    wrapper = QWidget()
    wrapper.setProperty("class", "wrapper")
    wrapper.setLayout(layout)
    wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(wrapper, **SHADOW_EFFECT_ARGUMENTS))

    return wrapper


create_wrapper_widget(QHBoxLayout())