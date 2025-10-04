from __future__ import annotations
from typing import NamedTuple, TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGraphicsDropShadowEffect,\
    QDateEdit
from PySide6.QtCore import Qt, QDate

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.list_widget import CustomListWidget
from DesktopQtToolkit.horizontal_scroll_area import HorizontalScrollArea

from project_configuration import QCALENDAR_DATE_FORMAT

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, SHADOW_EFFECT_ARGUMENTS, BASIC_FONT

if TYPE_CHECKING:
    from PySide6.QtCore import QEvent
    from AppObjects.category import Category
    from GUI.windows.main_window import MainWindow


class StatisticsWindow(SubWindow):
    """Represents Statistics window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.monthly_statistics = create_button("Monthly", (150,40))
        self.quarterly_statistics = create_button("Quarterly", (150,40))
        self.yearly_statistics = create_button("Yearly", (150,40))

        self.statistics_wrapper_layout = QVBoxLayout()
        self.statistics_wrapper_layout.setSpacing(40)
        self.statistics_wrapper_layout.addWidget(self.monthly_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.statistics_wrapper_layout.addWidget(self.quarterly_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.statistics_wrapper_layout.addWidget(self.yearly_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.statistics_wrapper_layout.setContentsMargins(30, 30, 30, 30)
        
        self.statistics_wrapper = QWidget()
        self.statistics_wrapper.setLayout(self.statistics_wrapper_layout)
        self.statistics_wrapper.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.statistics_wrapper, **SHADOW_EFFECT_ARGUMENTS)
        )
        self.statistics_wrapper.setProperty("class", "wrapper")

        self.custom_range_statistics = create_button("Custom date range", (180, 40))

        self.custom_statistics_wrapper_layout = QVBoxLayout()
        self.custom_statistics_wrapper_layout.addWidget(
            self.custom_range_statistics, alignment=ALIGN_V_CENTER | ALIGN_H_CENTER
        )
        self.custom_statistics_wrapper_layout.setContentsMargins(17, 30, 17, 30)

        self.custom_statistics_wrapper = QWidget()
        self.custom_statistics_wrapper.setLayout(self.custom_statistics_wrapper_layout)
        self.custom_statistics_wrapper.setProperty("class", "wrapper")
        self.custom_statistics_wrapper.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.custom_statistics_wrapper, **SHADOW_EFFECT_ARGUMENTS)
        )

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.statistics_wrapper, alignment=ALIGNMENT.AlignRight)
        self.main_layout.addWidget(self.custom_statistics_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addStretch(1)
        self.main_layout.setContentsMargins(50, 10, 50, 20)

        self.window_container.setLayout(self.main_layout)


class MonthlyStatistic(SubWindow):
    """Represents Monthly statistics window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.setStyleSheet(""" 
        QListWidget::item:hover,
        QListWidget::item:disabled:hover,
        QListWidget::item:hover:!active,
        QListWidget::item:focus
        {background: transparent}""")#Disable background color change on mouseover
        
        self.statistics = CustomListWidget()
        self.statistics.setMinimumWidth(500)
        self.statistics.setMinimumHeight(450)

        self.copy_statistics = create_button("Copy month statistics", (275,40))
        self.copy_statistics_layout = QHBoxLayout()
        self.copy_statistics_layout.addWidget(self.copy_statistics,alignment=ALIGNMENT.AlignCenter)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.statistics)
        self.main_layout.addLayout(self.copy_statistics_layout)
        self.main_layout.setContentsMargins(50, 10, 50, 20)

        self.window_container.setLayout(self.main_layout)


class QuarterlyStatistics(SubWindow):
    """Represents Quarterly statistics window structure.

        Warning
        -------
        This class contains non-GUI related objects, like NamedTuple variables.\n
        `TotalQuarterStatisticsView` - is a NamedTuple that contains the label and data for the total quarter statistics.\n
        `MonthlyStatisticsView` - is a NamedTuple that contains the month number, label and data for the monthly statistics in quarter.\n
        `QuarterStatisticsView` - is a NamedTuple that contains the quarter number, label, total quarter statistics and monthly statistics.\n
        `StatisticsView` - is a NamedTuple that contains all quarters statistics.
    """

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.setStyleSheet(""" 
        QListWidget::item:hover,
        QListWidget::item:disabled:hover,
        QListWidget::item:hover:!active,
        QListWidget::item:focus
        {background: transparent}""")#Disable background color change on hover

        self.statistics_layout = QVBoxLayout()
        self.statistics_window = QWidget()

        TotalQuarterStatisticsView = NamedTuple(
            "TotalQuarterStatisticsView", [("label", QLabel), ("data", CustomListWidget)]
        )
        QMonthlyStatisticsView = NamedTuple(
            "QMonthlyStatisticsView", [("month_number", int), ("label", QLabel), ("data", CustomListWidget)]
        )
        QuarterStatisticsView = NamedTuple(
            "QuarterStatisticsView", [
                ("quarter_number", int),
                ("label", QLabel),
                ("total_quarter_statistics", TotalQuarterStatisticsView), ("months", list[QMonthlyStatisticsView])
            ]
        )
        StatisticsView = NamedTuple("StatisticsView", [("quarters", list[QuarterStatisticsView])])

        self.quarters_statistics_list = []
        for quarter in range(1,5):

            quarter_label = QLabel()
            quarter_label.setFont(BASIC_FONT)
            quarter_label.setContentsMargins(0,50,0,0)
            self.statistics_layout.addWidget(quarter_label,alignment=ALIGNMENT.AlignBottom)

            self.quarter_window = QWidget()
            quarter_layout = QHBoxLayout()
            quarter_layout.setSpacing(30)
            total_quarter_statistics:TotalQuarterStatisticsView = TotalQuarterStatisticsView(QLabel(), CustomListWidget())

            quarter_months_statistics_list:list[QMonthlyStatisticsView] = []
            for statistic_list in range(4):              
                statistic_label = QLabel()
                statistic_label.setFont(BASIC_FONT)
                statistic_label_layout = QHBoxLayout()
                statistic_label_layout.addWidget(statistic_label, alignment=ALIGN_H_CENTER)

                statistic_data = CustomListWidget()
                statistic_data.setMinimumHeight(250)
                statistic_data.setMinimumWidth(500)

                statistic_layout = QVBoxLayout()
                statistic_layout.addLayout(statistic_label_layout)
                statistic_layout.addWidget(statistic_data, alignment=ALIGN_V_CENTER)

                quarter_layout.addLayout(statistic_layout)

                if statistic_list == 0:
                    total_quarter_statistics = TotalQuarterStatisticsView(statistic_label, statistic_data)
                else:
                    quarter_statistics_part = QMonthlyStatisticsView(
                        (quarter -1)*3 + statistic_list, statistic_label, statistic_data
                    )
                    quarter_months_statistics_list.append(quarter_statistics_part)
            
            quarter_statistics = QuarterStatisticsView(
                quarter, quarter_label, total_quarter_statistics, quarter_months_statistics_list
            )
            self.quarters_statistics_list.append(quarter_statistics)

            self.quarter_window.setLayout(quarter_layout)

            self.quarter_scroll = HorizontalScrollArea()
            self.quarter_scroll.setWidget(self.quarter_window)
            self.quarter_scroll.setWidgetResizable(True)
            self.quarter_scroll.setMinimumHeight(350)
            self.quarter_scroll.setStyleSheet("QScrollArea{border:none}")
            self.statistics_layout.addWidget(self.quarter_scroll)

        self.statistics = StatisticsView(self.quarters_statistics_list)

        self.copy_statistics = create_button("Copy quarterly statistics",(300,40))
        self.copy_statistics_layout = QHBoxLayout()
        self.copy_statistics_layout.addWidget(self.copy_statistics,alignment=ALIGNMENT.AlignCenter)
        self.statistics_layout.addLayout(self.copy_statistics_layout)

        self.statistics_window.setLayout(self.statistics_layout)
        self.window_scroll = QScrollArea()
        self.window_scroll.setWidget(self.statistics_window)
        self.window_scroll.setWidgetResizable(True)
        self.window_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.window_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.window_scroll.setStyleSheet("QScrollArea{border:none}")

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.window_scroll)

        self.window_container.setLayout(self.main_layout)


class YearlyStatistics(SubWindow):
    """Represents Yearly statistics window structure.

        Warning
        -------
        This class contains non-GUI related objects, like NamedTuple variables.\n
        `TotalYearStatisticsView` - is a NamedTuple that contains the label and data for the total year statistics.\n
        `MonthlyStatisticsView` - is a NamedTuple that contains the month number, label and data for the monthly statistics in year.\n
        `StatisticsView` - is a NamedTuple that contains the total year statistics and monthly statistics.\n
    """

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.setStyleSheet(""" 
        QListWidget::item:hover,
        QListWidget::item:disabled:hover,
        QListWidget::item:hover:!active,
        QListWidget::item:focus
        {background: transparent}""")#Disable background color change on mouseover

        TotalYearStatisticsView = NamedTuple("TotalYearStatisticsView", [("label", QLabel), ("data", CustomListWidget)])
        YMonthlyStatisticsView = NamedTuple(
            "YMonthlyStatisticsView", [("month_number", int), ("label", QLabel), ("data", CustomListWidget)]
        )
        StatisticsView = NamedTuple(
            "StatisticsView", [("total_year_statistics", TotalYearStatisticsView), ("months", list[YMonthlyStatisticsView])]
        )

        self.statistics_window = QWidget()
        self.statistics_window_layout = QVBoxLayout()
        total_year_statistics:TotalYearStatisticsView = TotalYearStatisticsView(QLabel(), CustomListWidget())

        self.yearly_statistics_parts_list:list[YMonthlyStatisticsView] = []
        for statistics_list in range(13):
            statistics_label = QLabel()
            statistics_label.setFont(BASIC_FONT)
            statistics_label.setContentsMargins(0,50,0,0)
            statistics_label_layout = QHBoxLayout()
            statistics_label_layout.addWidget(statistics_label, alignment=ALIGN_H_CENTER)

            statistics_data = CustomListWidget()
            statistics_data.setMinimumHeight(400)
            statistics_data.setMinimumWidth(500)

            statistics_layout = QVBoxLayout()
            statistics_layout.addLayout(statistics_label_layout)
            statistics_layout.addWidget(statistics_data)

            self.statistics_window_layout.addLayout(statistics_layout)

            if statistics_list == 0:
                total_year_statistics = TotalYearStatisticsView(statistics_label, statistics_data)
            else:
                yearly_statistics_part = YMonthlyStatisticsView(statistics_list, statistics_label, statistics_data)
                self.yearly_statistics_parts_list.append(yearly_statistics_part)

        self.statistics = StatisticsView(total_year_statistics, self.yearly_statistics_parts_list)
        
        self.copy_statistics = create_button("Copy yearly statistics", (275,40))
        self.copy_statistics_layout = QHBoxLayout()
        self.copy_statistics_layout.addWidget(self.copy_statistics,alignment=ALIGNMENT.AlignCenter)

        self.statistics_window_layout.addLayout(self.copy_statistics_layout)
        self.statistics_window.setLayout(self.statistics_window_layout)

        self.statistics_scroll = QScrollArea()
        self.statistics_scroll.setWidget(self.statistics_window)
        self.statistics_scroll.setWidgetResizable(True)
        self.statistics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.statistics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statistics_scroll.setStyleSheet("QScrollArea{border:none}")

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.statistics_scroll)
        self.main_layout.setContentsMargins(30, 10, 30, 20)

        self.window_container.setLayout(self.main_layout)


class CustomRangeStatistics(SubWindow):
    """Represents Custom range statistics window structure.

        Warning
        -------
        This class contains non-GUI related objects, like `selected_categories_data`.\n
        `selected_categories_data` - is a dictionary that contains the selected categories data.\
                                    Used to create custom statistics based on selection\n
    """
    
    class CategoryItem(QWidget):
        """Represents a category item in the categories list."""
    
        def __init__(self, category_name:str, remove_category_label:str, add_category_label:str) -> None:
            super().__init__()

            self.category_name = QLabel(category_name)
            self.category_name.setProperty("class", "light-text")
            self.category_name.setWordWrap(True)
            self.category_name.setMinimumWidth(200)

            self.remove_category_button = create_button(remove_category_label, (100, 40))
            self.remove_category_button.setDisabled(True)

            self.add_category_button = create_button(add_category_label, (100, 40))

            self.category_layout = QHBoxLayout()
            self.category_layout.addWidget(self.category_name, alignment=ALIGN_H_CENTER)
            self.category_layout.addWidget(self.add_category_button, alignment=ALIGNMENT.AlignRight)
            self.category_layout.addWidget(self.remove_category_button, alignment=ALIGNMENT.AlignRight)

            self.category_wrapper = QWidget()
            self.category_wrapper.setLayout(self.category_layout)
            self.category_wrapper.setProperty("class", "category_list_item")
            self.category_wrapper.setGraphicsEffect(
                QGraphicsDropShadowEffect(self.category_wrapper, **SHADOW_EFFECT_ARGUMENTS)
            )


    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.selected_categories_data:dict[int, tuple[Category, str]] = {}

        self.selected_categories_list = CustomListWidget()
        self.selected_categories_list.setMinimumWidth(400)
        self.selected_categories_list.setMinimumHeight(225)

        self.add_all_incomes_categories = create_button("Add all", (150, 40))
        self.remove_all_incomes_categories = create_button("Remove all", (150, 40))

        self.incomes_buttons_layout = QHBoxLayout()
        self.incomes_buttons_layout.addWidget(self.add_all_incomes_categories, alignment=ALIGN_H_CENTER)
        self.incomes_buttons_layout.addWidget(self.remove_all_incomes_categories, alignment=ALIGN_H_CENTER)

        self.incomes_categories_list_layout = QVBoxLayout()
        self.incomes_categories_list_layout.setSpacing(20)
        self.incomes_categories_list_layout.setContentsMargins(10, 10, 20, 10)

        self.incomes_categories_layout = QVBoxLayout()
        self.incomes_categories_layout.addLayout(self.incomes_buttons_layout)
        self.incomes_categories_layout.addLayout(self.incomes_categories_list_layout)

        self.incomes_categories_list_window = QWidget()
        self.incomes_categories_list_window.setLayout(self.incomes_categories_layout)

        self.incomes_categories_list_scroll = QScrollArea()
        self.incomes_categories_list_scroll.setWidget(self.incomes_categories_list_window)
        self.incomes_categories_list_scroll.setWidgetResizable(True)
        self.incomes_categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.incomes_categories_list_scroll.setMinimumHeight(350)
        self.incomes_categories_list_scroll.setMaximumHeight(350)
        self.incomes_categories_list_scroll.setMinimumWidth(530)
        self.incomes_categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
        self.incomes_categories_list_scroll.setProperty("class", "wrapper")
        self.incomes_categories_list_scroll.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.incomes_categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS)
        )

        self.add_all_expenses_categories = create_button("Add all", (150, 40))
        self.remove_all_expenses_categories = create_button("Remove all", (150, 40))

        self.expenses_buttons_layout = QHBoxLayout()
        self.expenses_buttons_layout.addWidget(self.add_all_expenses_categories, alignment=ALIGN_H_CENTER)
        self.expenses_buttons_layout.addWidget(self.remove_all_expenses_categories, alignment=ALIGN_H_CENTER)

        self.expenses_categories_list_layout = QVBoxLayout()
        self.expenses_categories_list_layout.setSpacing(20)
        self.expenses_categories_list_layout.setContentsMargins(10, 10, 20, 10)

        self.expenses_categories_layout = QVBoxLayout()
        self.expenses_categories_layout.addLayout(self.expenses_buttons_layout)
        self.expenses_categories_layout.addLayout(self.expenses_categories_list_layout)

        self.expenses_categories_list_window = QWidget()
        self.expenses_categories_list_window.setLayout(self.expenses_categories_layout)
        
        self.expenses_categories_list_scroll = QScrollArea()
        self.expenses_categories_list_scroll.setWidget(self.expenses_categories_list_window)
        self.expenses_categories_list_scroll.setWidgetResizable(True)
        self.expenses_categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.expenses_categories_list_scroll.setMinimumHeight(350)
        self.expenses_categories_list_scroll.setMaximumHeight(350)
        self.expenses_categories_list_scroll.setMinimumWidth(530)
        self.expenses_categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
        self.expenses_categories_list_scroll.setProperty("class", "wrapper")
        self.expenses_categories_list_scroll.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.expenses_categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS)
        )

        self.categories_lists_layout = QHBoxLayout()
        self.categories_lists_layout.addWidget(self.incomes_categories_list_scroll)
        self.categories_lists_layout.addWidget(self.expenses_categories_list_scroll)

        self.from_date = QDateEdit()
        self.from_date.setDisplayFormat(QCALENDAR_DATE_FORMAT)
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate())

        self.to_date = QDateEdit()
        self.to_date.setDisplayFormat(QCALENDAR_DATE_FORMAT)
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())

        self.date_inputs_layout = QHBoxLayout()
        self.date_inputs_layout.setSpacing(20)
        self.date_inputs_layout.addStretch(1)
        self.date_inputs_layout.addWidget(self.from_date, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.date_inputs_layout.addWidget(self.to_date, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.date_inputs_layout.addStretch(1)
        
        self.show_statistics = create_button("Statistics", (150, 40))
        self.show_statistics.setDefault(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(30)
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.selected_categories_list, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addLayout(self.categories_lists_layout)
        self.main_layout.addLayout(self.date_inputs_layout)
        self.main_layout.addWidget(self.show_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.setContentsMargins(30, 10, 30, 20)

        self.window_container.setLayout(self.main_layout)
        self.from_date.setFocus()


# pyright: reportIncompatibleMethodOverride=false
class CustomRangeStatisticsView(SubWindow):
    """Represents Custom range statistics view structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow], parent_window:CustomRangeStatistics) -> None:
        super().__init__(main_window, sub_windows)

        self.parent_window = parent_window

        self.statistics_list = CustomListWidget()
        self.statistics_list.setMinimumWidth(500)
        self.statistics_list.setMinimumHeight(350)

        self.copy_statistics = create_button("Copy statistics", (200, 40))

        self.statistics_layout = QVBoxLayout()
        self.statistics_layout.addWidget(self.statistics_list)
        self.statistics_layout.addWidget(self.copy_statistics, alignment=ALIGN_H_CENTER)

        self.transactions_list = CustomListWidget()
        self.transactions_list.setMinimumWidth(650)
        self.transactions_list.setMinimumHeight(350)

        self.copy_transactions = create_button("Copy transactions", (200, 40))

        self.transactions_layout = QVBoxLayout()
        self.transactions_layout.addWidget(self.transactions_list)
        self.transactions_layout.addWidget(self.copy_transactions, alignment=ALIGN_H_CENTER)

        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(20)
        self.content_layout.addStretch(1)
        self.content_layout.addLayout(self.statistics_layout)
        self.content_layout.addStretch(2)
        self.content_layout.addLayout(self.transactions_layout)
        self.content_layout.addStretch(1)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addLayout(self.content_layout)
        self.main_layout.setContentsMargins(30, 10, 30, 20)


        self.window_container.setLayout(self.main_layout)

    
    def closeEvent(self, event:QEvent) -> None:
        event.accept()
        self.parent_window.raise_()
            