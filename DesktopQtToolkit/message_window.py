from __future__ import annotations
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from sys import platform

from GUI.gui_constants import DWMWA_USE_IMMERSIVE_DARK_MODE
from AppObjects.app_core import AppCore




class MessageWindow(QMessageBox):
    """This class is used to create a message window that can be used to display messages to the user.
    It inherits from QMessageBox and adds some additional functionality."""

    _MSG_ICON_CACHE:dict[QMessageBox.Icon, QPixmap] = {}#On windows for some reason QPixmap icons assignment works way faster than setting Icon directly


    def __init__(
            self,
            main_window:QWidget,
            message_windows_container:dict[int, MessageWindow],
            type_confirm:bool,
            message_icon:QMessageBox.Icon | QPixmap,
            title:str
        ) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        message_windows_container[id(self)] = self

        self.setWindowFlags(Qt.WindowType.Tool)
        self.ok_button = self.addButton(QMessageBox.StandardButton.Ok)
        self.setDefaultButton(QMessageBox.StandardButton.Ok)
        self.setWindowTitle(title)

        if type_confirm:
            self.addButton(QMessageBox.StandardButton.Cancel)  
            self.setDefaultButton(QMessageBox.StandardButton.Cancel)

        if isinstance(message_icon, QPixmap):
            self.setIconPixmap(message_icon)
        else:
            if message_icon not in MessageWindow._MSG_ICON_CACHE:
                self.setIcon(message_icon)
                icon_pixmap = self.iconPixmap()
                MessageWindow._MSG_ICON_CACHE[message_icon] = icon_pixmap
            else:
                self.setIconPixmap(MessageWindow._MSG_ICON_CACHE[message_icon])
    

    def exec(self) -> int:
        """This method is used to show the message window and center it on the main window.
        It also sets the theme of the message window to match the main window theme on windows OS."""

        if platform == "win32":
            import ctypes

            if AppCore.instance().config.theme == "Dark":
                value = ctypes.c_int(2)
            else:
                value = ctypes.c_int(0)

            ctypes.windll.dwmapi.DwmSetWindowAttribute( # type: ignore[attr-defined]  #Mypy doesn't understand that this attribute exists only on windows
                self.winId(), DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))

        def center_message() -> None:
            """This method is used to center the message window on the main window."""

            main_window_center = self.main_window.geometry().center()
            message_window_geometry = self.geometry()

            main_window_center.setX(int(main_window_center.x()-message_window_geometry.width()/2))
            main_window_center.setY(int(main_window_center.y()-message_window_geometry.height()/2))

            self.move(main_window_center)
            self.activateWindow()


        QTimer.singleShot(10, center_message)
        return super().exec()