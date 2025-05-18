from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic
from sys import platform
from PySide6.QtWidgets import QDialog, QWidget, QLabel, QGraphicsDropShadowEffect, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QTimer, QRect, QByteArray

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, APP_ICON, SHADOW_EFFECT_ARGUMENTS
from DesktopQtToolkit.create_button import create_button

if TYPE_CHECKING:
    from typing import Any




QtMeta = type(QDialog)
SubWindowChild = TypeVar("SubWindowChild", bound="SubWindow")

class SubWindowSingleton(QtMeta, Generic[SubWindowChild]):#type: ignore[valid-type, misc] #Mypy doesn't support dynamic base classes
    """This is a metaclass that is used to ensure that only one instance of the SubWindow class is created. 
    It doest't mean that only one sub window can be created, but only one window with same structe can be created.
    For example, if you will create SettingsWindow and then will try to create another SettingsWindow, it will return an error."""

    _instances:dict[str, SubWindow] = dict()

    def __call__(cls, *args:Any, **kwargs:Any) -> SubWindowChild:
        if cls.__name__ in cls._instances:
            raise RuntimeError(f"Only one instance of {cls.__name__} can be created. Use WindowsRegistry to get window")

        instance:SubWindowChild = super().__call__(*args, **kwargs)
        cls._instances[instance.__class__.__name__] = instance
        return instance



# pyright: reportIncompatibleMethodOverride=false
class SubWindow(QDialog, metaclass=SubWindowSingleton):
    """This class is used to create a sub window that can be used to display sub windows."""

    def __init__(self, main_window:QWidget, sub_window_container:dict[int, SubWindow]) -> None:
        super().__init__(main_window)
        self.main_window = main_window
        sub_window_container[id(self)] = self

        self.setWindowIcon(APP_ICON)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.opacity_animation = QPropertyAnimation(self, QByteArray(b"windowOpacity"), self) 
        self.opacity_animation.setDuration(100)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)

        self.window_container = QWidget()
        self.window_container.setProperty("class", "sub_window")
        self.window_container.setGraphicsEffect(QGraphicsDropShadowEffect(self.window_container, **SHADOW_EFFECT_ARGUMENTS))

        self.size_animation = QPropertyAnimation(self.window_container, QByteArray(b"geometry"), self.window_container)
        self.size_animation.setDuration(100)

        self.animation_group = QParallelAnimationGroup(self)
        self.animation_group.addAnimation(self.opacity_animation)
        self.animation_group.addAnimation(self.size_animation)

        self.close_window = create_button("X", (30, 30), "close_window")
        self.close_window.clicked.connect(lambda: self.done(1))
        self.close_window.setGraphicsEffect(QGraphicsDropShadowEffect(self.close_window, **SHADOW_EFFECT_ARGUMENTS))

        self.sub_window_title = QLabel()
        self.sub_window_title.setContentsMargins(10, 5, 10, 5)
        self.sub_window_title.setProperty("class", "sub_window_title")

        move_sub_title = QSpacerItem(30, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.window_menu_layout = QHBoxLayout()
        self.window_menu_layout.addStretch(1)
        self.window_menu_layout.addSpacerItem(move_sub_title)
        self.window_menu_layout.addWidget(self.sub_window_title, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.window_menu_layout.addStretch(1)
        self.window_menu_layout.addWidget(self.close_window, alignment=ALIGNMENT.AlignRight | ALIGN_V_CENTER)
        self.window_menu_layout.setContentsMargins(0, 0, 0, 20)

        self.window_layout = QVBoxLayout()
        self.window_layout.addWidget(self.window_container)
        self.setLayout(self.window_layout)


    def exec(self) -> int:
        """This method is used to show the sub window and center it on the main window."""
        def show_window() -> None:
            main_window_center = self.main_window.geometry().center()
            sub_window_geometry = self.geometry()

            main_window_center.setX(int(main_window_center.x()-sub_window_geometry.width()/2))
            main_window_center.setY(int(main_window_center.y()-sub_window_geometry.height()/2))

            self.move(main_window_center)

            if platform != "win32":
                initial_size = self.window_container.geometry()
                window_width = initial_size.width()
                window_height = initial_size.height()

                start_width = window_width*0.8
                start_height = window_height*0.8
                
                smaller_size = QRect(initial_size)
                smaller_size.setWidth(int(start_width))
                smaller_size.setHeight(int(start_height))
                
                self.size_animation.setStartValue(smaller_size)
                self.size_animation.setEndValue(initial_size)

                self.animation_group.setDirection(QPropertyAnimation.Direction.Forward)
                self.animation_group.start()

            self.activateWindow()

        QTimer.singleShot(10, show_window)
        return super().exec()
    

    def done(self, return_code:int) -> None:
        """This method is used to close the sub window and hide it."""

        def hide_window() -> None:
            QDialog.done(self, return_code)
            self.window_container.setGeometry(self.size_animation.endValue())

        if platform != "win32":
            self.animation_group.setDirection(QPropertyAnimation.Direction.Backward)
            self.animation_group.start()
            QTimer.singleShot(200, hide_window)
        else:
            QDialog.done(self, return_code)


    def setWindowTitle(self, text:str) -> None:
        """This method is used to set the window title of the sub window."""
        
        self.sub_window_title.setText(text)
        super().setWindowTitle(text)
