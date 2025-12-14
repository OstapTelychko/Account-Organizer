from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout

from DesktopQtToolkit.create_date_input import create_date_input
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget

from GUI.gui_constants import ALIGN_H_CENTER



class DateSelection(QWidget):
    """A widget for selecting a from and to date. With quick select buttons for month and year."""


    def __init__(self) -> None:
        super().__init__()

        self.search_from_date = create_date_input()
        self.search_to_date = create_date_input()

        self.select_month_range_button = create_button("Month", (100, 40))
        self.select_year_range_button = create_button("Year", (100, 40))

        self.date_range_layout = QGridLayout()
        self.date_range_layout.addWidget(self.select_month_range_button, 0, 0, alignment=ALIGN_H_CENTER)
        self.date_range_layout.addWidget(self.select_year_range_button, 0, 1, alignment=ALIGN_H_CENTER)
        self.date_range_layout.addWidget(self.search_from_date, 1, 0)
        self.date_range_layout.addWidget(self.search_to_date, 1, 1)

        self.date_range_wrapper = create_wrapper_widget(self.date_range_layout)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.date_range_wrapper)
        self.setLayout(self.main_layout)

        self.select_month_range_button.clicked.connect(self.select_month_range)
        self.select_year_range_button.clicked.connect(self.select_year_range)
    

    def select_month_range(self) -> None:
        """Select the current month as date range."""
        
        current_date = self.search_from_date.date()
        month_start = current_date.addDays(1 - current_date.day())
        month_end = month_start.addMonths(1).addDays(-1)

        self.search_from_date.setDate(month_start)
        self.search_to_date.setDate(month_end)
    

    def select_year_range(self) -> None:
        """Select the current year as date range."""
        
        current_date = self.search_from_date.date()
        year_start = current_date.addDays(1 - current_date.dayOfYear())
        year_end = year_start.addYears(1).addDays(-1)

        self.search_from_date.setDate(year_start)
        self.search_to_date.setDate(year_end)