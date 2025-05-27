from __future__ import annotations
from typing import TYPE_CHECKING
from sys import platform
import ctypes

from PySide6.QtGui import QIcon
from qdarktheme._style_loader import load_stylesheet#type: ignore[import-untyped] #I don't want to write a stub for this library

from project_configuration import THEME_DIRECTORY

from AppObjects.session import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger

from GUI.gui_constants import app, DWMWA_USE_IMMERSIVE_DARK_MODE

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = get_logger(__name__)

DARK_THEME_ICON = QIcon(f"{THEME_DIRECTORY}/Dark theme.png")
DARK_THEME = load_stylesheet("dark")+"""
.category{
    background-color:rgb(42, 42, 42);
    border-radius:10px;
    padding-right:50px;
}
.category_list_item{
    border-radius:10px;
    background-color:rgb(37, 37, 37);
}
.category > QPushButton{
    background-color:rgb(50, 50, 50);
}

.category_data{
    background-color:rgb(45,45,45);
}

.information_message{
    background-color:rgb(40, 40, 40);
    border-radius:15px;
}

.sub_window{
    background-color:rgb(32, 33, 36);
    border-radius:15px;
}
.sub_window_title{
    background-color:rgb(45, 45, 45);
    border-radius:10px;
}

.wrapper{
    background-color:rgb(45,45,45);
    border-radius:10px;
}

.button, .button:active, .button:focus, .button:default{
    background-color:rgb(50, 50, 50);
    border:1px solid black;
    color:rgb(130, 170, 255)
}

.close_window, .close_window:active, .close_window:focus, .close_window:default{
    background-color:rgb(50, 50, 50);
    color:rgb(130, 170, 255)
}

.button:disabled, .close_window:disabled{
    background-color:rgb(100, 100, 100);
    color:rgb(150, 150, 150);
}

.button:hover, .button:focus:hover, .button:active:hover, .button:default:hover
.close_window:hover, .close_window:active:hover, .close_window:focus:hover, .close_window:default:hover{
    background-color:rgb(45, 45, 45)
}

.backups_table{
    background-color:rgb(45, 45, 45)
}
"""


LIGHT_THEME_ICON = QIcon(f"{THEME_DIRECTORY}/Light theme.png")
LIGHT_THEME = load_stylesheet("light",custom_colors={"background":"#ebeef0","foreground":"#191a1b"})+"""
.category{
    background-color:rgb(100, 120, 100);
    border-radius:15px;
    color:rgb(240, 240, 240);
}

.category_list_item{
    border-radius:15px;
    background-color:rgb(130, 150, 130);
    color:rgb(240, 240, 240);
}

.category_data{
    background-color:rgb(205,205,205);
}

.category > QPushButton{
    background-color:rgb(120, 140, 120);
    color:rgb(240, 240, 240);
    border-color:rgb(60, 60, 60)
}

.category > QLabel{
    color:rgb(240, 240, 240);
}

.information_message{
    background-color:rgb(200,200,200);
    color:white;
    border-radius:15px;
}
.sub_window{
    background-color:rgb(225, 228, 230);
    color:white;
    border-radius:15px;
}
.sub_window_title{
    background-color:rgb(100, 120, 100);
    border-radius:10px;
    color:rgb(240, 240, 240)
}

.wrapper{
    background-color:rgb(100, 120, 100);
    border-radius:10px;
}

.light-text{
    color:rgb(240, 240, 240);
}

.button, .button:active, .button:focus, .button:default{
    background-color:rgb(100, 130, 100);
    color:rgb(240, 240, 240);
    border:1px solid black;
}

.close_window, .close_window:active, .close_window:focus, .close_window:default{
    background-color:rgb(100, 130, 100);
    color:rgb(240, 240, 240);
    border:none;
}

.button:disabled, .close_window{
    background-color:rgb(100, 100, 100);
    color:rgb(150, 150, 150);
}

.button:hover, .button:focus:hover, .button:active:hover, .button:default:hover, 
.close_window:hover, .close_window:active:hover, .close_window:focus:hover, .close_window:default:hover{
    background-color:rgb(90, 120, 90);
}
"""


def switch_theme() -> None:
    """Switch theme between dark and light. If current theme is dark, switch to light and vice versa."""

    app_core = AppCore.instance()
    if app_core.config.theme == "Dark":
        app.setStyleSheet(LIGHT_THEME)
        WindowsRegistry.SettingsWindow.switch_themes_button.setIcon(LIGHT_THEME_ICON)
        app_core.config.theme = "Light"

        if platform == "win32":
            set_theme_mode_on_window(WindowsRegistry.MainWindow, ctypes.c_uint(0))
        logger.info("Theme switched to Light")

    elif app_core.config.theme == "Light":
        app.setStyleSheet(DARK_THEME)
        WindowsRegistry.SettingsWindow.switch_themes_button.setIcon(DARK_THEME_ICON)
        app_core.config.theme = "Dark"

        if platform == "win32":
            set_theme_mode_on_window(WindowsRegistry.MainWindow, ctypes.c_uint(2))
        logger.info("Theme switched to Dark")

    app_core.config.update_user_config()


def load_theme() -> None:
    """Load theme from user config."""

    logger.info("Loading theme")
    app_core = AppCore.instance()
    if app_core.config.theme == "Dark":
        app.setStyleSheet(DARK_THEME)
        WindowsRegistry.SettingsWindow.switch_themes_button.setIcon(DARK_THEME_ICON)

        if platform == "win32":
            set_theme_mode_on_window(WindowsRegistry.MainWindow, ctypes.c_uint(2))
        logger.info("Dark theme loaded")
            
    if app_core.config.theme == "Light":
        app.setStyleSheet(LIGHT_THEME)
        WindowsRegistry.SettingsWindow.switch_themes_button.setIcon(LIGHT_THEME_ICON)

        if platform == "win32":
            set_theme_mode_on_window(WindowsRegistry.MainWindow, ctypes.c_uint(0))
        logger.info("Light theme loaded")


if platform == "win32":
    def set_theme_mode_on_window(window:QWidget, value:ctypes.c_uint) -> None:
        """Set theme mode on window. This is used to set the theme mode on windows OS."""

        ctypes.windll.dwmapi.DwmSetWindowAttribute(# type: ignore[attr-defined]  #Mypy doesn't understand that this attribute exists only on windows
            window.winId(), DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
        )