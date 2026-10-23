from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QHeaderView, QVBoxLayout, QWidget, QLabel

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.table_widget import CustomTableWidget
from DesktopQtToolkit.default_drop_shadow_effect import DefaultDropShadowEffect

from GUI.gui_constants import BASIC_FONT, ALIGN_H_CENTER

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow



class DelayedPaymentsWindow(SubWindow):
    """Represents Delayed payments window structure. It lists future expenses that explain the projected balance."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.transactions_table = CustomTableWidget()
        self.transactions_table.setProperty("class", "category_data")
        self.transactions_table.setColumnCount(4)
        self.transactions_table.setMinimumSize(650, 300)

        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)# Category
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)# Name
        header.setFont(BASIC_FONT)

        self.total_label = QLabel()
        self.total_label.setFont(BASIC_FONT)
        self.total_label.setProperty("class", "light-text")

        self.table_layout = QVBoxLayout()
        self.table_layout.addWidget(self.transactions_table)
        self.table_layout.addWidget(self.total_label, alignment=ALIGN_H_CENTER)

        self.table_wrapper = QWidget()
        self.table_wrapper.setProperty("class", "wrapper")
        self.table_wrapper.setLayout(self.table_layout)
        self.table_wrapper.setGraphicsEffect(DefaultDropShadowEffect(self.table_wrapper))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(25)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.table_wrapper)
        self.main_layout.setContentsMargins(20, 10, 20, 20)

        self.window_container.setLayout(self.main_layout)
