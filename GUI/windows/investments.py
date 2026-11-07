from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QHeaderView, QAbstractItemView
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from project_configuration import MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, TRANSACTION_DAY_REGEX

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.table_widget import CustomTableWidget
from DesktopQtToolkit.strict_double_validator import StrictDoubleValidator
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget

from GUI.gui_constants import ALIGN_H_CENTER, ALIGN_V_CENTER, BASIC_FONT

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow



class MonthlyInvestmentsWindow(SubWindow):
    """Represents Monthly investments window structure.
    It allows to deposit money into several Investments categories and revaluate them at once.

        Table columns
        -------------
        0 - category name, 1 - current value, 2 - deposit (editable), 3 - new value (editable), 4 - category ID (hidden).
    """

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.operations_day = QLineEdit()
        self.operations_day.setFont(BASIC_FONT)
        self.day_regular_expression = QRegularExpression(TRANSACTION_DAY_REGEX)
        self.operations_day.setValidator(QRegularExpressionValidator(self.day_regular_expression))

        self.total_amount = QLineEdit()
        self.total_amount.setFont(BASIC_FONT)
        self.total_amount.setMinimumWidth(250)
        self.total_amount_validator = StrictDoubleValidator(MIN_TRANSACTION_VALUE, MAX_TRANSACTION_VALUE, 2)
        self.total_amount_validator.setNotation(StrictDoubleValidator.Notation.StandardNotation)
        self.total_amount.setValidator(self.total_amount_validator)

        self.remaining_amount = QLabel()
        self.remaining_amount.setFont(BASIC_FONT)

        self.fields_layout = QHBoxLayout()
        self.fields_layout.setSpacing(20)
        self.fields_layout.addWidget(self.operations_day, alignment=ALIGN_V_CENTER)
        self.fields_layout.addWidget(self.total_amount, alignment=ALIGN_V_CENTER)
        self.fields_layout.addWidget(self.remaining_amount, alignment=ALIGN_V_CENTER)

        self.investments_table = CustomTableWidget()
        self.investments_table.setProperty("class", "category_data")
        self.investments_table.setColumnCount(5)
        self.investments_table.setColumnHidden(4, True)
        self.investments_table.setMinimumSize(750, 250)
        self.investments_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self.investments_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)# Category
        header.setFont(BASIC_FONT)

        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(self.investments_table)

        self.save_button = create_button("Save", (160, 40))
        self.save_button.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(25)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(create_wrapper_widget(self.fields_layout))
        self.main_layout.addWidget(create_wrapper_widget(self.table_layout))
        self.main_layout.addWidget(self.save_button, alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(20, 10, 20, 20)

        self.window_container.setLayout(self.main_layout)
