from PySide6.QtWidgets import QLayout, QWidget, QGraphicsDropShadowEffect
from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS



def create_wrapper_widget(layout:QLayout, css_class:str="wrapper") -> QWidget:
    """Create a wrapper widget with a given layout and shadow effect.
    
        Arguments
        ---------
            `layout` : (QLayoutChild) - The layout to be set for the wrapper widget.
            `css_class` : (str) - CSS class for styling the wrapper widget.
        Returns
        -------
            `QWidget` - The created wrapper widget with the specified layout and shadow effect.
    """

    wrapper = QWidget()
    wrapper.setProperty("class", css_class)
    wrapper.setLayout(layout)
    wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(wrapper, **SHADOW_EFFECT_ARGUMENTS))

    return wrapper