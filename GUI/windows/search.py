from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QWidget, QGridLayout

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.create_date_input import create_date_input
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget
from DesktopQtToolkit.list_widget import CustomListWidget

from GUI.gui_constants import ALIGN_H_CENTER

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow



class SearchWindow(SubWindow):
    """Represents Search window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)


        self.search_name = QLineEdit()
        self.search_name.setMinimumWidth(180)
        self.search_name.setPlaceholderText("Transaction name")

        self.search_value = QLineEdit()
        self.search_value.setMinimumWidth(180)
        self.search_value.setPlaceholderText("Transaction value")

        self.transactions_parameters_layout = QVBoxLayout()
        self.transactions_parameters_layout.addWidget(self.search_name)
        self.transactions_parameters_layout.addWidget(self.search_value)

        self.search_from_date = create_date_input()
        self.search_to_date = create_date_input()

        self.select_month_range_button = create_button("Month", (100, 40))
        self.select_year_range_button = create_button("Year", (100, 40))

        self.date_range_layout = QGridLayout()
        self.date_range_layout.addWidget(self.select_month_range_button, 0, 0)
        self.date_range_layout.addWidget(self.select_year_range_button, 0, 1)
        self.date_range_layout.addWidget(self.search_from_date, 1, 0)
        self.date_range_layout.addWidget(self.search_to_date, 1, 1)

        self.date_range_wrapper = create_wrapper_widget(self.date_range_layout)

        self.search_parameters_layout = QHBoxLayout()
        self.search_parameters_layout.addLayout(self.transactions_parameters_layout)
        self.search_parameters_layout.addSpacing(20)
        self.search_parameters_layout.addWidget(self.date_range_wrapper)


        self.search_parameters_wrapper = create_wrapper_widget(self.search_parameters_layout)

        self.search = create_button("Search", (100, 40))

        self.transactions_list = CustomListWidget()

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.search_parameters_wrapper)
        self.main_layout.addWidget(self.search, alignment=ALIGN_H_CENTER)
        self.main_layout.addSpacing(40)
        self.main_layout.addWidget(self.transactions_list)

        self.window_container.setLayout(self.main_layout)