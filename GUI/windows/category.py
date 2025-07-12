from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt


from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, SHADOW_EFFECT_ARGUMENTS

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class CategorySettingsWindow(SubWindow):
    """Represents Category settings window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.rename_category = create_button("Rename category",(255,40))
        self.delete_category = create_button("Delete category",(255,40))
        self.change_category_position = create_button("Change position", (255, 40))
        self.copy_transactions = create_button("Copy transactions",(275,40))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.rename_category, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.delete_category, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.change_category_position, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.copy_transactions,alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(30, 10, 30, 20)

        self.window_container.setLayout(self.main_layout)


class AddCategoryWindow(SubWindow):
    """Represents Add category window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.category_name = QLineEdit()
        self.category_name.setPlaceholderText("Category name")

        self.button = create_button("Add category", (160,40))
        self.button.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(30)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.category_name,alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.button,alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(30, 10, 30, 30)

        self.window_container.setLayout(self.main_layout)
        self.category_name.setFocus()



class ChangeCategoryPositionWindow(SubWindow):
    """Represents Change category position window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.preview_category_position = QLabel()
        self.preview_category_position.setProperty("class", "category_list_item")
        
        self.preview_category_name = QLabel()
        self.preview_category_name.setProperty("class", "light-text")

        self.preview_category_container = QWidget()
        self.preview_category_container.setProperty("class", "category_list_item")
        self.preview_category_container.setGraphicsEffect(QGraphicsDropShadowEffect(self.preview_category_container, **SHADOW_EFFECT_ARGUMENTS))

        self.preview_category_layout = QHBoxLayout()
        self.preview_category_layout.addWidget(self.preview_category_position, alignment=ALIGNMENT.AlignRight)
        self.preview_category_layout.addWidget(self.preview_category_name, alignment=ALIGNMENT.AlignLeft)
        self.preview_category_container.setLayout(self.preview_category_layout)

        self.new_position = QLineEdit()
        self.new_position_validator = QIntValidator(0, 1000)
        self.new_position.setValidator(self.new_position_validator)
        
        self.enter_new_position = create_button("Save", (140, 30))
        self.enter_new_position.setDefault(True)

        self.new_position_layout = QHBoxLayout()
        self.new_position_layout.addWidget(self.new_position, alignment=ALIGNMENT.AlignHorizontal_Mask)
        self.new_position_layout.addWidget(self.enter_new_position, alignment=ALIGNMENT.AlignLeft)
        self.new_position_layout.setContentsMargins(0, 50, 0, 50)

        self.categories_list_layout = QVBoxLayout()
        self.categories_list_window = QWidget()
        self.categories_list_window.setLayout(self.categories_list_layout)

        self.categories_list_scroll = QScrollArea()
        self.categories_list_scroll.setWidget(self.categories_list_window)
        self.categories_list_scroll.setWidgetResizable(True)
        self.categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.categories_list_scroll.setMinimumHeight(350)
        self.categories_list_scroll.setMinimumWidth(400)
        self.categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
        self.categories_list_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.categories_list_scroll.setProperty("class", "wrapper")
        self.categories_list_scroll.setGraphicsEffect(QGraphicsDropShadowEffect(self.categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS))

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.preview_category_container, alignment=ALIGN_H_CENTER)
        self.main_layout.addLayout(self.new_position_layout)
        self.main_layout.addWidget(self.categories_list_scroll, alignment=ALIGN_H_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(30, 10, 30, 20)

        self.window_container.setLayout(self.main_layout)
        self.new_position.setFocus()


class RenameCategoryWindow(SubWindow):
    """Represents Rename category window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.new_category_name = QLineEdit()
        self.new_category_name.setMinimumWidth(150)
        self.new_category_name.setPlaceholderText("New name")

        self.button = create_button("Rename", (170,40))
        self.button.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(30)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.new_category_name,alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.button,alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(40, 10, 40, 20)

        self.window_container.setLayout(self.main_layout)
        self.new_category_name.setFocus()