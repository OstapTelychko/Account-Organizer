from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QLabel, QScrollArea, QTabWidget, QToolButton,
                               QSizePolicy)

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon, QFont

from project_configuration import ROOT_DIRECTORY
from GUI.gui_constants import ALIGMENT, ICON_SIZE, APP_ICON, BASIC_FONT

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button



class MainWindow():
    window = QWidget()
    window.resize(1500,750)
    window.setMinimumHeight(685)
    window.setMinimumWidth(900)
    window.setWindowTitle("Account Organizer")
    window.setWindowIcon(APP_ICON)
    window.setWindowFlags(Qt.WindowType.Window)
    window.setObjectName("main_window")
    window.setAttribute(Qt.WidgetAttribute.WA_StaticContents)

    #Account balance and settings
    General_info = QHBoxLayout()
    account_current_balance = QLabel("Balance: 0")
    account_current_balance.setFont(QFont("C059 [urw]",pointSize=15))
    settings = QToolButton()
    settings.setIcon(QIcon(f"{ROOT_DIRECTORY}/Images/Settings icon.png"))
    settings.setIconSize(ICON_SIZE)

    General_info.addStretch(7)
    General_info.addWidget(account_current_balance,alignment=ALIGMENT.AlignTop| ALIGMENT.AlignHCenter)
    General_info.addStretch(8)
    General_info.addWidget(settings,alignment=ALIGMENT.AlignTop | ALIGMENT.AlignRight)


    #Year and month
    previous_year_button = create_button("<",(32,30))

    next_year_button = create_button(">",(32,30))

    current_year = QLabel("2023")
    current_year.setFont(BASIC_FONT)

    Year_layout = QHBoxLayout()
    Year_layout.addStretch(4)
    Year_layout.addWidget(previous_year_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Year_layout.addWidget(current_year, 1, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    Year_layout.addWidget(next_year_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Year_layout.addStretch(5)

    previous_month_button = create_button("<",(30,30))

    next_month_button = create_button(">",(30,30))

    current_month = QLabel("April")
    current_month.setFont(BASIC_FONT)
    current_month.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

    Month_layout = QHBoxLayout()
    Month_layout.addStretch(4)
    Month_layout.addWidget(previous_month_button,alignment=ALIGMENT.AlignHCenter)
    Month_layout.addWidget(current_month, 1, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    Month_layout.addWidget(next_month_button,alignment=ALIGMENT.AlignHCenter)
    Month_layout.addStretch(5)

    #Income and expenses windows 
    Incomes_and_expenses = QTabWidget()
    Incomes_and_expenses.setFont(BASIC_FONT)

    Incomes_window = QWidget()
    Incomes_window.setContentsMargins(0, 10, 0, 10)
    Incomes_window.setMinimumHeight(350)
    
    add_incomes_category = create_button("Create category",(170,40))

    Incomes_window_layout = QHBoxLayout()
    Incomes_window_layout.addWidget(add_incomes_category)

    Incomes_window_layout.setSpacing(70)
    Incomes_window.setLayout(Incomes_window_layout)

    Incomes_scroll = QScrollArea()
    Incomes_scroll.setWidget(Incomes_window)
    Incomes_scroll.setWidgetResizable(True)
    Incomes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    Incomes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    Incomes_scroll.setObjectName("Income-window")
    Incomes_scroll.setStyleSheet("#Income-window{ border-color:rgba(0,205,0,100); border-width:2px }")
        
    Expenses_window = QWidget()
    Expenses_window.setContentsMargins(0, 10, 0, 10)

    add_expenses_category = create_button("Create category",(170,40))

    Expenses_window_layout = QHBoxLayout()
    Expenses_window_layout.addWidget(add_expenses_category)
        
    Expenses_window_layout.setSpacing(70)
    Expenses_window.setLayout(Expenses_window_layout)

    Expenses_scroll = QScrollArea()
    Expenses_scroll.setWidget(Expenses_window)
    Expenses_scroll.setWidgetResizable(True)
    Expenses_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    Expenses_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    Expenses_scroll.setObjectName("Expenses-window")
    Expenses_scroll.setStyleSheet("#Expenses-window{ border-color:rgba(205,0,0,100); border-width:2px }")

    Incomes_and_expenses.addTab(Incomes_scroll,"Income")
    Incomes_and_expenses.addTab(Expenses_scroll,"Expenses")
    Incomes_and_expenses.setMinimumHeight(500)
    Incomes_and_expenses.setObjectName("Incomes-and-expenses")
    Incomes_and_expenses.setStyleSheet("QTabWidget::pane{border:none}")

    window_bottom = QHBoxLayout()
    statistics = create_button("Statistics",(160,40))

    mini_calculator_label = QLabel("Mini-calculator")
    mini_calculator_label.setFont(BASIC_FONT)
    mini_calculator_text = QLineEdit()
    mini_calculator_text.setPlaceholderText("2 * 3 = 6;  3 / 2 = 1.5;  3 + 2 = 5;  2 - 3 = -1;  4 ** 2 = 16")
    mini_calculator_text.setMinimumWidth(400)

    calculate = create_button("=",(100,40))

    calculate_font = QFont(BASIC_FONT)
    calculate_font.setPointSize(BASIC_FONT.pointSize()+6)
    calculate.setFont(calculate_font)
    
    window_bottom.addStretch(1)
    window_bottom.addWidget(statistics)
    window_bottom.addStretch(5)
    window_bottom.addWidget(mini_calculator_label)
    window_bottom.addWidget(mini_calculator_text)
    window_bottom.addWidget(calculate)
    window_bottom.addStretch(1)

    main_layout= QVBoxLayout()
    main_layout.addLayout(General_info)
    main_layout.addLayout(Year_layout)
    main_layout.addLayout(Month_layout)
    main_layout.addWidget(Incomes_and_expenses)
    main_layout.addStretch(1)
    main_layout.addLayout(window_bottom)
    main_layout.addStretch(1)

    window.setLayout(main_layout)

    sub_windows:dict[int, SubWindow] = dict()
    def move_event(event:QEvent):
        for sub_window in MainWindow.sub_windows.values():
            main_window_center = MainWindow.window.geometry().center()
            sub_window_geometry = sub_window.geometry()

            main_window_center.setX(main_window_center.x()-sub_window_geometry.width()/2)
            main_window_center.setY(main_window_center.y()-sub_window_geometry.height()/2)

            sub_window.move(main_window_center)
        event.accept()

    window.moveEvent = move_event




