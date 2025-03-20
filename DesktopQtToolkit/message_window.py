from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from sys import platform
if platform == "win32":
    import ctypes

from GUI.gui_constants import DWMWA_USE_IMMERSIVE_DARK_MODE
from AppObjects.session import Session

if TYPE_CHECKING:
    from PySide6.QtGui import QIcon


class MessageWindow(QMessageBox):
    
    def __init__(self, main_window:QWidget, message_windows_container:dict, type_confirm:bool, message_icon:QMessageBox.Icon | QPixmap, title:str, window_icon:QIcon, ) -> None:
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

        if type(message_icon) is QPixmap:
            self.setIconPixmap(message_icon)
        else:
            self.setIcon(message_icon)

        self.setWindowIcon(window_icon)
    

    def exec(self):
        if platform == "win32":
            if Session.theme == "Dark":
                value = ctypes.c_int(2)
            else:
                value = ctypes.c_int(0)

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                self.winId(), DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
            )

        def center_message():
            main_window_center = self.main_window.geometry().center()
            message_window_geometry = self.geometry()

            main_window_center.setX(main_window_center.x()-message_window_geometry.width()/2)
            main_window_center.setY(main_window_center.y()-message_window_geometry.height()/2)

            self.move(main_window_center)
            self.activateWindow()


        QTimer.singleShot(10, center_message)
        super().exec()