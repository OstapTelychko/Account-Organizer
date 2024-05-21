from sys import platform

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QLabel, QPushButton, QScrollArea, QApplication,
                               QTabWidget, QToolButton, QComboBox, QDialog,
                               QSizePolicy, QGraphicsDropShadowEffect)

from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtGui import QIcon, QFont, QColor

from project_configuration import ROOT_DIRECTORY, AVAILABLE_LANGUAGES



app = QApplication([])
app.setApplicationName("Account Organizer")


ALIGMENT = Qt.AlignmentFlag
ICON_SIZE = QSize(30, 30)
APP_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/App icon.png")

SHADOW_EFFECT_ARGUMENTS = {"blurRadius":15, "xOffset":0, "yOffset":0, "color":QColor(0, 0, 0)}

if platform == "linux":
    BASIC_FONT = QFont("C059 [urw]", pointSize=12)
else:#Windows
    BASIC_FONT = QFont("Georgia", pointSize=12)


def create_button(button_text:str, size:tuple[int]) -> QPushButton:
    button = QPushButton(text=button_text)
    button.setFont(BASIC_FONT)
    button.setMinimumSize(*size)
    button.setMaximumSize(*size)
    return button


def close_dialog(event:QEvent):
    event.accept()
    MainWindow.window.raise_()



class MainWindow():
    window = QWidget()
    window.resize(1500,750)
    window.setMinimumHeight(685)
    window.setMinimumWidth(900)
    window.setWindowTitle("Account Organizer")
    window.setWindowIcon(APP_ICON)
    window.setObjectName("main_window")

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
    previous_year_button.setProperty("class", "button")

    next_year_button = create_button(">",(32,30))
    next_year_button.setProperty("class", "button")

    current_year = QLabel("2023")
    current_year.setFont(BASIC_FONT)

    Year_layout = QHBoxLayout()
    Year_layout.addStretch(4)
    Year_layout.addWidget(previous_year_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Year_layout.addWidget(current_year, 1, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    Year_layout.addWidget(next_year_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Year_layout.addStretch(5)

    previous_month_button = create_button("<",(30,30))
    previous_month_button.setProperty("class", "button")

    next_month_button = create_button(">",(30,30))
    next_month_button.setProperty("class", "button")

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
    add_incomes_category.setProperty("class", "button")

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
    add_expenses_category.setProperty("class", "button")

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
    statistics.setProperty("class", "button")

    mini_calculator_label = QLabel("Mini-calculator")
    mini_calculator_label.setFont(BASIC_FONT)
    mini_calculator_text = QLineEdit()
    mini_calculator_text.setPlaceholderText("2 * 3 = 6;  3 / 2 = 1.5;  3 + 2 = 5;  2 - 3 = -1;  4 ** 2 = 16")
    mini_calculator_text.setMinimumWidth(400)

    calculate = create_button("=",(100,40))
    calculate.setProperty("class", "button")

    if platform == "linux":
        calculate.setFont(QFont("C059 [urw]", pointSize=18))
    else:#Windows
        calculate.setFont(QFont("Georgia", pointSize=18))

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



class SettingsWindow():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Settings")
    window.setStyleSheet("QComboBox:active,QComboBox:focus,QComboBox:disabled{border-color:transparent}")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog

    switch_themes_button = QToolButton()
    switch_themes_button.setIconSize(ICON_SIZE)

    languages = QComboBox()
    languages.setFont(BASIC_FONT)
    languages.addItems(AVAILABLE_LANGUAGES)

    for language in range(len(AVAILABLE_LANGUAGES)):
        languages.setItemIcon(language, QIcon(f"{ROOT_DIRECTORY}/Images/{language}-flag.png"))

    gui_settings_wrapper_layout = QVBoxLayout()
    gui_settings_wrapper_layout.addWidget(switch_themes_button, alignment=ALIGMENT.AlignHCenter)
    gui_settings_wrapper_layout.addWidget(languages, alignment=ALIGMENT.AlignHCenter)

    gui_settings_wrapper = QWidget()
    gui_settings_wrapper.setProperty("class", "wrapper")
    gui_settings_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(gui_settings_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    gui_settings_wrapper.setLayout(gui_settings_wrapper_layout)
    gui_settings_wrapper.setMinimumHeight(220)
    gui_settings_wrapper.setMinimumWidth(250)



    accounts = QComboBox()
    accounts.setFont(BASIC_FONT)
    accounts.setMinimumWidth(250)
    accounts.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)

    add_account = create_button("Add account",(180,50))
    add_account.setProperty("class", "button")

    rename_account = create_button("Rename account",(180,50))
    rename_account.setProperty("class", "button")

    delete_account = create_button("Delete account",(180,50))
    delete_account.setStyleSheet("QPushButton{color:rgba(255,0,0,150); border-color:red;}")

    account_management_wrapper_layout = QVBoxLayout()
    account_management_wrapper_layout.addWidget(accounts, alignment=ALIGMENT.AlignHCenter)
    account_management_wrapper_layout.addWidget(add_account, alignment=ALIGMENT.AlignHCenter)
    account_management_wrapper_layout.addWidget(rename_account, alignment=ALIGMENT.AlignHCenter)
    account_management_wrapper_layout.addWidget(delete_account, alignment=ALIGMENT.AlignHCenter)

    account_management_wrapper = QWidget()
    account_management_wrapper.setLayout(account_management_wrapper_layout)
    account_management_wrapper.setProperty("class", "wrapper")
    account_management_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(account_management_wrapper, **SHADOW_EFFECT_ARGUMENTS))


    total_income = QLabel()
    total_income.setProperty("class", "account-info")
    total_income.setFont(BASIC_FONT)

    total_expense = QLabel()
    total_expense.setFont(BASIC_FONT)
    total_expense.setProperty("class", "account-info")

    account_created_date = QLabel()
    account_created_date.setFont(BASIC_FONT)
    account_created_date.setProperty("class", "account-info")

    account_info_wrapper_layout = QVBoxLayout()
    account_info_wrapper_layout.addWidget(total_income, alignment=ALIGMENT.AlignHCenter)
    account_info_wrapper_layout.addWidget(total_expense, alignment=ALIGMENT.AlignHCenter)
    account_info_wrapper_layout.addWidget(account_created_date, alignment=ALIGMENT.AlignHCenter)

    account_info_wrapper = QWidget()
    account_info_wrapper.setProperty("class", "wrapper")
    account_info_wrapper.setLayout(account_info_wrapper_layout)
    account_info_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(account_info_wrapper, **SHADOW_EFFECT_ARGUMENTS))


    gui_settings_and_account_management = QHBoxLayout()
    gui_settings_and_account_management.addStretch(1)
    gui_settings_and_account_management.addWidget(gui_settings_wrapper, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    gui_settings_and_account_management.addStretch(1)
    gui_settings_and_account_management.addWidget(account_management_wrapper, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    gui_settings_and_account_management.addStretch(1)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addStretch(1)
    main_layout.addLayout(gui_settings_and_account_management)
    main_layout.addWidget(account_info_wrapper, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)