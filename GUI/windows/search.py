from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget
from DesktopQtToolkit.list_widget import CustomListWidget
from DesktopQtToolkit.strict_double_validator import StrictDoubleValidator

from GUI.gui_constants import ALIGN_H_CENTER, BASIC_FONT
from GUI.ComplexWidgets.categories_select_by_type import CategoriesSelectionByType
from GUI.ComplexWidgets.date_selection import DateSelection

from project_configuration import MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow



class SearchWindow(SubWindow):
    """Represents Search window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.search_name = QLineEdit()
        self.search_name.setMinimumWidth(180)
        self.search_name.setPlaceholderText("Transaction name")

        self.value_operands = QComboBox()
        self.value_operands.setMinimumWidth(60)
        self.value_operands.addItems(["=", "!=", "<", ">", "<=", ">="])
        self.value_operands.setFont(BASIC_FONT)

        self.search_value = QLineEdit()
        self.search_value.setMinimumWidth(180)
        self.search_value.setPlaceholderText("Transaction value")
        self.search_value.setValidator(StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2))

        self.value_layout = QHBoxLayout()
        self.value_layout.addWidget(self.value_operands)
        self.value_layout.addWidget(self.search_value)

        self.transactions_parameters_layout = QVBoxLayout()
        self.transactions_parameters_layout.addWidget(self.search_name)
        self.transactions_parameters_layout.addLayout(self.value_layout)

        self.date_selection = DateSelection()

        self.categories_selection = CategoriesSelectionByType()
        self.categories_selection.setHidden(True)
        self.categories_selection_button = create_button("Categories", (150, 40))

        self.search_parameters_layout = QHBoxLayout()
        self.search_parameters_layout.addLayout(self.transactions_parameters_layout)
        self.search_parameters_layout.addSpacing(20)
        self.search_parameters_layout.addWidget(self.date_selection, alignment=ALIGN_H_CENTER)
        self.search_parameters_layout.addSpacing(20)
        self.search_parameters_layout.addWidget(self.categories_selection_button)

        self.search_parameters_wrapper_layout = QVBoxLayout()
        self.search_parameters_wrapper_layout.addLayout(self.search_parameters_layout)
        self.search_parameters_wrapper_layout.addWidget(self.categories_selection, alignment=ALIGN_H_CENTER)

        self.search_parameters_wrapper = create_wrapper_widget(self.search_parameters_wrapper_layout)

        self.search = create_button("Search", (100, 40))
        self.search.setDefault(True)

        self.transactions_list = CustomListWidget()

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.search_parameters_wrapper)
        self.main_layout.addWidget(self.search, alignment=ALIGN_H_CENTER)
        self.main_layout.addSpacing(40)
        self.main_layout.addWidget(self.transactions_list)

        self.window_container.setLayout(self.main_layout)
        self.setMinimumSize(1100, 850)

        self.categories_selection_button.clicked.connect(self.toggle_categories_selection)


    def toggle_categories_selection(self) -> None:
        """Show/hide categories selection widget."""
        if self.categories_selection.isHidden():
            self.categories_selection.setHidden(False)
            self.transactions_list.setHidden(True)
        else:
            self.categories_selection.setHidden(True)
            self.transactions_list.setHidden(False)
