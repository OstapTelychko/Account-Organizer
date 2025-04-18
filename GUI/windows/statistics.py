from __future__ import annotations
from typing import NamedTuple, TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QListWidget, QGraphicsDropShadowEffect, QDateEdit
from PySide6.QtCore import Qt, QDate

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button

from project_configuration import QCALENDAR_DATE_FORMAT

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, SHADOW_EFFECT_ARGUMENTS, BASIC_FONT
from GUI.windows.main_window import MainWindow

if TYPE_CHECKING:
    from AppObjects.category import Category



class StatisticsWindow():
    """Represents Statistics window structure."""

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    monthly_statistics = create_button("Monthly", (150,40))
    quarterly_statistics = create_button("Quarterly", (150,40))
    yearly_statistics = create_button("Yearly", (150,40))

    statistics_wrapper_layout = QVBoxLayout()
    statistics_wrapper_layout.setSpacing(40)
    statistics_wrapper_layout.addWidget(monthly_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    statistics_wrapper_layout.addWidget(quarterly_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    statistics_wrapper_layout.addWidget(yearly_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    statistics_wrapper_layout.setContentsMargins(30, 30, 30, 30)
    
    statistics_wrapper = QWidget()
    statistics_wrapper.setLayout(statistics_wrapper_layout)
    statistics_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(statistics_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    statistics_wrapper.setProperty("class", "wrapper")

    custom_range_statistics = create_button("Custom date range", (180, 40))

    custom_statistics_wrapper_layout = QVBoxLayout()
    custom_statistics_wrapper_layout.addWidget(custom_range_statistics, alignment=ALIGN_V_CENTER | ALIGN_H_CENTER)
    custom_statistics_wrapper_layout.setContentsMargins(17, 30, 17, 30)

    custom_statistics_wrapper = QWidget()
    custom_statistics_wrapper.setLayout(custom_statistics_wrapper_layout)
    custom_statistics_wrapper.setProperty("class", "wrapper")
    custom_statistics_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(custom_statistics_wrapper, **SHADOW_EFFECT_ARGUMENTS))

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addStretch(1)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(statistics_wrapper, alignment=ALIGNMENT.AlignRight)
    main_layout.addWidget(custom_statistics_wrapper, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(50, 10, 50, 20)

    window.window_container.setLayout(main_layout)



class MonthlyStatistics():
    """Represents Monthly statistics window structure."""

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on mouseover
    
    statistics = QListWidget()
    statistics.setMinimumWidth(500)
    statistics.setMinimumHeight(450)
    statistics.setFont(BASIC_FONT)

    copy_statistics = create_button("Copy month statistics", (275,40))
    copy_statistics_layout = QHBoxLayout()
    copy_statistics_layout.addWidget(copy_statistics,alignment=ALIGNMENT.AlignCenter)

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(statistics)
    main_layout.addLayout(copy_statistics_layout)
    main_layout.setContentsMargins(50, 10, 50, 20)

    window.window_container.setLayout(main_layout)



class QuarterlyStatistics():
    """Represents Quarterly statistics window structure.

        Warning
        -------
        This class contains non-GUI related objects, like NamedTuple variables.\n
        `TotalQuarterStatisticsView` - is a NamedTuple that contains the label and data for the total quarter statistics.\n
        `MonthlyStatisticsView` - is a NamedTuple that contains the month number, label and data for the monthly statistics in quarter.\n
        `QuarterStatisticsView` - is a NamedTuple that contains the quarter number, label, total quarter statistics and monthly statistics.\n
        `StatisticsView` - is a NamedTuple that contains all quarters statistics.
    """

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on hover

    statistics_layout = QVBoxLayout()
    statistics_window = QWidget()

    TotalQuarterStatisticsView = NamedTuple("TotalQuarterStatisticsView", [("label", QLabel), ("data", QListWidget)])
    MonthlyStatisticsView = NamedTuple("MonthlyStatisticsView", [("month_number", int), ("label", QLabel), ("data", QListWidget)])
    QuarterStatisticsView = NamedTuple("QuarterStatisticsView", [("quarter_number", int), ("label", QLabel), ("total_quarter_statistics", TotalQuarterStatisticsView), ("months", list[MonthlyStatisticsView])])
    StatisticsView = NamedTuple("StatisticsView", [("quarters", list[QuarterStatisticsView])])

    quarters_statistics_list = []
    for quarter in range(1,5):

        quarter_label = QLabel()
        quarter_label.setFont(BASIC_FONT)
        quarter_label.setContentsMargins(0,50,0,0)
        statistics_layout.addWidget(quarter_label,alignment=ALIGNMENT.AlignBottom)

        quarter_window = QWidget()
        quarter_layout = QHBoxLayout()
        quarter_layout.setSpacing(30)


        quarter_months_statistics_list:list[MonthlyStatisticsView] = []
        for statistic_list in range(4):              
            statistic_label = QLabel()
            statistic_label.setFont(BASIC_FONT)
            statistic_label_layout = QHBoxLayout()
            statistic_label_layout.addWidget(statistic_label, alignment=ALIGN_H_CENTER)

            statistic_data = QListWidget()
            statistic_data.setFont(BASIC_FONT)
            statistic_data.setWordWrap(True)
            statistic_data.setMinimumHeight(250)
            statistic_data.setMinimumWidth(500)

            statistic_layout = QVBoxLayout()
            statistic_layout.addLayout(statistic_label_layout)
            statistic_layout.addWidget(statistic_data, alignment=ALIGN_V_CENTER)

            quarter_layout.addLayout(statistic_layout)

            if statistic_list == 0:
                total_quarter_statistics = TotalQuarterStatisticsView(statistic_label, statistic_data)
            else:
                quarter_statistics_part = MonthlyStatisticsView((quarter -1)*3 + statistic_list, statistic_label, statistic_data)
                quarter_months_statistics_list.append(quarter_statistics_part)
        
        quarter_statistics = QuarterStatisticsView(quarter, quarter_label, total_quarter_statistics, quarter_months_statistics_list)
        quarters_statistics_list.append(quarter_statistics)

        quarter_window.setLayout(quarter_layout)

        quarter_scroll = QScrollArea()
        quarter_scroll.setWidget(quarter_window)
        quarter_scroll.setWidgetResizable(True)
        quarter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        quarter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        quarter_scroll.setMinimumHeight(350)
        quarter_scroll.setStyleSheet("QScrollArea{border:none}")
        statistics_layout.addWidget(quarter_scroll)

    statistics = StatisticsView(quarters_statistics_list)

    copy_statistics = create_button("Copy quarterly statistics",(300,40))
    copy_statistics_layout = QHBoxLayout()
    copy_statistics_layout.addWidget(copy_statistics,alignment=ALIGNMENT.AlignCenter)
    statistics_layout.addLayout(copy_statistics_layout)

    statistics_window.setLayout(statistics_layout)
    window_scroll = QScrollArea()
    window_scroll.setWidget(statistics_window)
    window_scroll.setWidgetResizable(True)
    window_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    window_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    window_scroll.setStyleSheet("QScrollArea{border:none}")

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(window_scroll)

    window.window_container.setLayout(main_layout)



class YearlyStatistics():
    """Represents Yearly statistics window structure.

        Warning
        -------
        This class contains non-GUI related objects, like NamedTuple variables.\n
        `TotalYearStatisticsView` - is a NamedTuple that contains the label and data for the total year statistics.\n
        `MonthlyStatisticsView` - is a NamedTuple that contains the month number, label and data for the monthly statistics in year.\n
        `StatisticsView` - is a NamedTuple that contains the total year statistics and monthly statistics.\n
    """

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on mouseover
    
    TotalYearStatisticsView = NamedTuple("TotalYearStatisticsView", [("label", QLabel), ("data", QListWidget)])
    MonthlyStatisticsView = NamedTuple("MonthlyStatisticsView", [("month_number", int), ("label", QLabel), ("data", QListWidget)])
    StatisticsView = NamedTuple("StatisticsView", [("total_year_statistics", TotalYearStatisticsView), ("months", list[MonthlyStatisticsView])])

    statistics_window = QWidget()
    statistics_window_layout = QVBoxLayout()

    yearly_statistics_parts_list:list[MonthlyStatisticsView] = []
    for statistics_list in range(13):
        statistics_label = QLabel()
        statistics_label.setFont(BASIC_FONT)
        statistics_label.setContentsMargins(0,50,0,0)
        statistics_label_layout = QHBoxLayout()
        statistics_label_layout.addWidget(statistics_label, alignment=ALIGN_H_CENTER)

        statistics_data = QListWidget()
        statistics_data.setFont(BASIC_FONT)
        statistics_data.setMinimumHeight(400)
        statistics_data.setMinimumWidth(500)
        statistics_data.setWordWrap(True)

        statistics_layout = QVBoxLayout()
        statistics_layout.addLayout(statistics_label_layout)
        statistics_layout.addWidget(statistics_data)

        statistics_window_layout.addLayout(statistics_layout)

        if statistics_list == 0:
            total_year_statistics = TotalYearStatisticsView(statistics_label, statistics_data)
        else:
            yearly_statistics_part = MonthlyStatisticsView(statistics_list, statistics_label, statistics_data)
            yearly_statistics_parts_list.append(yearly_statistics_part)

    statistics = StatisticsView(total_year_statistics, yearly_statistics_parts_list)

    
    copy_statistics = create_button("Copy yearly statistics", (275,40))
    copy_statistics_layout = QHBoxLayout()
    copy_statistics_layout.addWidget(copy_statistics,alignment=ALIGNMENT.AlignCenter)

    statistics_window_layout.addLayout(copy_statistics_layout)
    statistics_window.setLayout(statistics_window_layout)

    statistics_scroll = QScrollArea()
    statistics_scroll.setWidget(statistics_window)
    statistics_scroll.setWidgetResizable(True)
    statistics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    statistics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    statistics_scroll.setStyleSheet("QScrollArea{border:none}")

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(statistics_scroll)
    main_layout.setContentsMargins(30, 10, 30, 20)

    window.window_container.setLayout(main_layout)



class CustomRangeStatistics():
    """Represents Custom range statistics window structure.

        Warning
        -------
        This class contains non-GUI related objects, like `selected_categories_data`.\n
        `selected_categories_data` - is a dictionary that contains the selected categories data. Used to create custom statistics based on selection\n
    """

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    selected_categories_data:dict[int, tuple[Category, str]] = {}

    selected_categories_list = QListWidget()
    selected_categories_list.setFont(BASIC_FONT)
    selected_categories_list.setMinimumWidth(400)
    selected_categories_list.setMinimumHeight(225)
    selected_categories_list.setGraphicsEffect(QGraphicsDropShadowEffect(selected_categories_list, **SHADOW_EFFECT_ARGUMENTS))
    selected_categories_list.setWordWrap(True)

    add_all_incomes_categories = create_button("Add all", (150, 40))
    remove_all_incomes_categories = create_button("Remove all", (150, 40))

    incomes_buttons_layout = QHBoxLayout()
    incomes_buttons_layout.addWidget(add_all_incomes_categories, alignment=ALIGN_H_CENTER)
    incomes_buttons_layout.addWidget(remove_all_incomes_categories, alignment=ALIGN_H_CENTER)

    incomes_categories_list_layout = QVBoxLayout()
    incomes_categories_list_layout.setSpacing(20)
    incomes_categories_list_layout.setContentsMargins(10, 10, 20, 10)

    incomes_categories_layout = QVBoxLayout()
    incomes_categories_layout.addLayout(incomes_buttons_layout)
    incomes_categories_layout.addLayout(incomes_categories_list_layout)

    incomes_categories_list_window = QWidget()
    incomes_categories_list_window.setLayout(incomes_categories_layout)

    incomes_categories_list_scroll = QScrollArea()
    incomes_categories_list_scroll.setWidget(incomes_categories_list_window)
    incomes_categories_list_scroll.setWidgetResizable(True)
    incomes_categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    incomes_categories_list_scroll.setMinimumHeight(350)
    incomes_categories_list_scroll.setMaximumHeight(350)
    incomes_categories_list_scroll.setMinimumWidth(430)
    incomes_categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
    incomes_categories_list_scroll.setProperty("class", "wrapper")
    incomes_categories_list_scroll.setGraphicsEffect(QGraphicsDropShadowEffect(incomes_categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS))

    add_all_expenses_categories = create_button("Add all", (150, 40))
    remove_all_expenses_categories = create_button("Remove all", (150, 40))

    expenses_buttons_layout = QHBoxLayout()
    expenses_buttons_layout.addWidget(add_all_expenses_categories, alignment=ALIGN_H_CENTER)
    expenses_buttons_layout.addWidget(remove_all_expenses_categories, alignment=ALIGN_H_CENTER)

    expenses_categories_list_layout = QVBoxLayout()
    expenses_categories_list_layout.setSpacing(20)
    expenses_categories_list_layout.setContentsMargins(10, 10, 20, 10)

    expenses_categories_layout = QVBoxLayout()
    expenses_categories_layout.addLayout(expenses_buttons_layout)
    expenses_categories_layout.addLayout(expenses_categories_list_layout)

    expenses_categories_list_window = QWidget()
    expenses_categories_list_window.setLayout(expenses_categories_layout)
    
    expenses_categories_list_scroll = QScrollArea()
    expenses_categories_list_scroll.setWidget(expenses_categories_list_window)
    expenses_categories_list_scroll.setWidgetResizable(True)
    expenses_categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    expenses_categories_list_scroll.setMinimumHeight(350)
    expenses_categories_list_scroll.setMaximumHeight(350)
    expenses_categories_list_scroll.setMinimumWidth(430)
    expenses_categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
    expenses_categories_list_scroll.setProperty("class", "wrapper")
    expenses_categories_list_scroll.setGraphicsEffect(QGraphicsDropShadowEffect(expenses_categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS))

    categoriels_lists_layout = QHBoxLayout()
    categoriels_lists_layout.addWidget(incomes_categories_list_scroll)
    categoriels_lists_layout.addWidget(expenses_categories_list_scroll)

    from_date = QDateEdit()
    from_date.setDisplayFormat(QCALENDAR_DATE_FORMAT)
    from_date.setCalendarPopup(True)
    from_date.setDate(QDate.currentDate())

    to_date = QDateEdit()
    to_date.setDisplayFormat(QCALENDAR_DATE_FORMAT)
    to_date.setCalendarPopup(True)
    to_date.setDate(QDate.currentDate())

    date_inputs_layout = QHBoxLayout()
    date_inputs_layout.setSpacing(20)
    date_inputs_layout.addStretch(1)
    date_inputs_layout.addWidget(from_date, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    date_inputs_layout.addWidget(to_date, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    date_inputs_layout.addStretch(1)
    
    show_statistics = create_button("Statistics", (150, 40))
    show_statistics.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(30)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(selected_categories_list, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    main_layout.addLayout(categoriels_lists_layout)
    main_layout.addLayout(date_inputs_layout)
    main_layout.addWidget(show_statistics, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
    main_layout.setContentsMargins(30, 10, 30, 20)

    window.window_container.setLayout(main_layout)



class CustomRangeStatisticsView:
    """Represents Custom range statistics view structure."""

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)
    window.closeEvent = lambda event: (event.accept(), CustomRangeStatistics.window.raise_()) #type: ignore[method-assign, assignment, func-returns-value]  #This will be solved in the future when class will be written properly

    statistics_list = QListWidget()
    statistics_list.setFont(BASIC_FONT)
    statistics_list.setMinimumWidth(500)
    statistics_list.setMinimumHeight(350)
    statistics_list.setGraphicsEffect(QGraphicsDropShadowEffect(statistics_list, **SHADOW_EFFECT_ARGUMENTS))

    copy_statistics = create_button("Copy statistics", (200, 40))

    statistics_layout = QVBoxLayout()
    statistics_layout.addWidget(statistics_list)
    statistics_layout.addWidget(copy_statistics, alignment=ALIGN_H_CENTER)

    transactions_list = QListWidget()
    transactions_list.setFont(BASIC_FONT)
    transactions_list.setMinimumWidth(650)
    transactions_list.setMinimumHeight(350)
    transactions_list.setGraphicsEffect(QGraphicsDropShadowEffect(transactions_list, **SHADOW_EFFECT_ARGUMENTS))

    copy_transactions = create_button("Copy transactions", (200, 40))

    transactions_layout = QVBoxLayout()
    transactions_layout.addWidget(transactions_list)
    transactions_layout.addWidget(copy_transactions, alignment=ALIGN_H_CENTER)

    content_layout = QHBoxLayout()
    content_layout.setSpacing(20)
    content_layout.addStretch(1)
    content_layout.addLayout(statistics_layout)
    content_layout.addStretch(2)
    content_layout.addLayout(transactions_layout)
    content_layout.addStretch(1)

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addLayout(content_layout)
    main_layout.setContentsMargins(30, 10, 30, 20)


    window.window_container.setLayout(main_layout)
