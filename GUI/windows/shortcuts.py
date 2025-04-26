from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from AppObjects.user_config import UserConfig
from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class ShortcutsWindow(SubWindow):

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.shortcuts_scroll = QScrollArea()
        self.shortcuts_scroll.setWidgetResizable(True)
        self.shortcuts_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.shortcuts_scroll.setGraphicsEffect(QGraphicsDropShadowEffect(self, **SHADOW_EFFECT_ARGUMENTS)) 
        self.shortcuts_scroll.setMinimumHeight(400)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.shortcuts_scroll)
        self.main_layout.setContentsMargins(30, 10, 30, 30)

        self.window_container.setLayout(self.main_layout)
