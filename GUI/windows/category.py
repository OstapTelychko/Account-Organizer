from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QScrollArea, QSizePolicy
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.default_drop_shadow_effect import DefaultDropShadowEffect
from DesktopQtToolkit.strict_double_validator import StrictDoubleValidator
from DesktopQtToolkit.default_label import DefaultLabel
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER
from project_configuration import MAX_TRANSACTION_VALUE, MIN_TRANSACTION_VALUE
from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER

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
        self.transactions_anomalous_values = create_button("Anomalous transaction values", (275, 40))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.rename_category, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.delete_category, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.change_category_position, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.copy_transactions,alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.transactions_anomalous_values, alignment=ALIGN_H_CENTER)
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
        self.preview_category_container.setGraphicsEffect(
            DefaultDropShadowEffect(self.preview_category_container)
        )

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
        self.categories_list_scroll.setGraphicsEffect(
            DefaultDropShadowEffect(self.categories_list_scroll)
        )

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


class AnomalousTransactionValuesWindow(SubWindow):
    """Represents Anomalous transaction values settings window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.description_label = DefaultLabel(set_light_text=True)
        self.description_label.setMinimumSize(350, 200)
        self.min_value = QLineEdit()
        self.min_value.setValidator(StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2))

        self.max_value = QLineEdit()
        self.max_value.setValidator(StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2))

        self.values_layout = QHBoxLayout()
        self.values_layout.addWidget(self.min_value)
        self.values_layout.addWidget(self.max_value)

        self.wrapper_layout = QVBoxLayout()
        self.wrapper_layout.addWidget(self.description_label)
        self.wrapper_layout.addLayout(self.values_layout)
        self.wrapper = create_wrapper_widget(self.wrapper_layout)

        self.save_button = create_button("Save", (140, 30))
        self.save_button.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.wrapper, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.save_button, alignment=ALIGN_H_CENTER)

        self.window_container.setLayout(self.main_layout)