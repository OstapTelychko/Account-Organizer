from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QLabel,QPushButton,QListWidget,QScrollArea,QApplication,QGridLayout,QMessageBox,QTabWidget,QToolButton,QComboBox,QDialog
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap,QIcon,QFont,QFontDatabase
from qdarktheme._style_loader import load_stylesheet
from Accont_mangment import Account
from Languages import LANGUAGES



app = QApplication([])

ALIGMENT = Qt.AlignmentFlag
APP_ICON = QIcon("./Images/App icon.png")

dark_theme = load_stylesheet("dark")
dark_theme_icon = QIcon("./Images/Dark theme.png")

light_theme = load_stylesheet("light",custom_colors={"background":"#ffffff","foreground":"#191a1b"})
light_theme_icon = QIcon("./Images/Light theme.png")

# app.setStyleSheet(dark_theme)

errors_list = []
# buttons_list = []

# print(QFontDatabase.families())
def create_error(text:str,type_confirm:bool,icon:QMessageBox.Icon) -> QMessageBox:
    error = QMessageBox(text=text)
    # error.setText(text)
    error.addButton(QMessageBox.StandardButton.Ok)
    error.setWindowTitle("Account Organizer")
    if type_confirm:
        error.addButton(QMessageBox.StandardButton.Cancel)  
    error.setWindowIcon(APP_ICON)
    error.setIcon(icon)
    errors_list.append(error)
    return error


def create_button(button_text:str,size:tuple[int])->QPushButton:
    button = QPushButton(text=button_text)
    # button.setFont(QFont("Calibri",pointSize=10))
    button.setFont(QFont("C059 [urw]",pointSize=10))
    button.setMinimumSize(*size)
    button.setMaximumSize(*size)
    return button


def load_category(type:str,name:str,account:Account,category_id:int,year:int,month:int,Language:str)-> dict:
    """Add category to user window

        Args:
            `type` (str): category type incomes or expenses

            `name` (str): category name

            `account` (str): account loads transactions by month from db

            `category_id` (int): category id to identify the category

            `year` (int): year of transactions

            `month` (int): month of transactions

            `Language` (str): Language for buttons and columns

        Returns:
            `category` (dict): Dictionary with category name and link on add, delete, rename transaction buttons
    """
    category = {}

    category_window = QWidget()
    category_layout = QVBoxLayout()
    category_name = QLabel(name)
    category["Name"] = name

    category_settings = QToolButton()
    category_settings.setIcon(QIcon("./Images/Settings icon.png"))
    category_settings.setIconSize(QSize(30,30))
    category["Settings"] = category_settings

    Category_general_info = QHBoxLayout()
    Category_general_info.addWidget(category_name, alignment=ALIGMENT.AlignHCenter)
    Category_general_info.addWidget(category_settings)

    category_data = QWidget()
    category_data_layout = QGridLayout()

    transaction_name_title = QLabel(LANGUAGES[Language]["Account"]["Info"][0])
    transaction_day_title = QLabel(LANGUAGES[Language]["Account"]["Info"][1])
    transaction_value_title = QLabel(LANGUAGES[Language]["Account"]["Info"][2])

    category["Columns"] = {}
    category["Columns"]["Name"] = transaction_name_title
    category["Columns"]["Date"] = transaction_day_title
    category["Columns"]["Value"] = transaction_value_title

    category_data_layout.addWidget(transaction_name_title,0,0)
    category_data_layout.addWidget(transaction_day_title,0,1,alignment=ALIGMENT.AlignLeft)
    category_data_layout.addWidget(transaction_value_title,0,2,alignment=ALIGMENT.AlignLeft)

    transactions = account.get_transactions_by_month(category_id,year,month)
    if len(transactions) > 0: #Check if transactions are in db
        for index,transaction in enumerate(transactions):
            transaction_name = QLabel(transaction[6])
            transaction_day = QLabel(str(transaction[4]))
            transaction_value = QLabel(str(transaction[5]))
            category_data_layout.addWidget(transaction_name,index+1,0)
            category_data_layout.addWidget(transaction_day,index+1,1,alignment=ALIGMENT.AlignLeft)
            category_data_layout.addWidget(transaction_value,index+1,2,alignment=ALIGMENT.AlignLeft)

    category_data.setLayout(category_data_layout)
    category_data_scroll = QScrollArea()
    category_data_scroll.setWidget(category_data)
    category_data_scroll.setWidgetResizable(True)
    category_data_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    category_data_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    category_data_scroll.setMinimumWidth(400)

    add_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][0],(155,40))
    delete_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][1],(155,40))
    rename_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][2],(170,40))
    
    category["Add transaction"] = add_transaction
    category["Delete transaction"] = delete_transaction
    category["Rename transaction"] = rename_transaction

    transactions_managment = QHBoxLayout()
    transactions_managment.addWidget(add_transaction)
    transactions_managment.addWidget(delete_transaction)
    transactions_managment.addWidget(rename_transaction)

    category_layout.addStretch(1)
    category_layout.addLayout(Category_general_info)
    category_layout.addWidget(category_data_scroll,alignment=ALIGMENT.AlignVCenter)
    category_layout.addLayout(transactions_managment)
    category_layout.addStretch(1)

    category_window.setLayout(category_layout)

    if type == "Incomes":
        Main_window.Incomes_window_layout.addWidget(category_window)
    else:
        Main_window.Expenses_window_layout.addWidget(category_window)
    return category


class Errors():
    incorrect_data_type_error = create_error("",False,QMessageBox.Icon.Warning)
    account_alredy_exists_error  = create_error("",False,QMessageBox.Icon.Warning)
    zero_current_balance_error = create_error("",True,QMessageBox.Icon.Question)
    category_exists_error = create_error("",False,QMessageBox.Icon.Warning)



class Main_window():
    window = QWidget()
    window.resize(1400,750)
    window.setMinimumHeight(500)
    window.setMinimumWidth(750)
    window.setWindowTitle("Account Organizer")
    window.setWindowIcon(APP_ICON)


    #Account balance and settings
    General_info = QHBoxLayout()
    account_current_balance = QLabel("Balance: 0")
    account_current_balance.setFont(QFont("C059 [urw]",pointSize=15))
    settings = QToolButton()
    settings.setIcon(QIcon("./Images/Settings icon.png"))
    settings.setIconSize(QSize(30,30))

    General_info.addStretch(7)
    General_info.addWidget(account_current_balance,alignment=ALIGMENT.AlignTop| ALIGMENT.AlignHCenter)
    General_info.addStretch(8)
    General_info.addWidget(settings,alignment=ALIGMENT.AlignTop | ALIGMENT.AlignRight)


    #Year and month
    Year_layout = QHBoxLayout()
    previous_year_button = create_button("<",(32,30))
    current_year = QLabel("2023")
    next_year_button = create_button(">",(32,30))

    Year_layout.addStretch(5)
    Year_layout.addSpacing(1)
    Year_layout.addWidget(previous_year_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Year_layout.addWidget(current_year,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    Year_layout.addWidget(next_year_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Year_layout.addStretch(6)

    Month_layout = QHBoxLayout()
    previous_month_button = create_button("<",(30,30))
    current_month = QLabel("April")
    next_month_button = create_button(">",(30,30))

    Month_layout.addStretch(5)
    Month_layout.addWidget(previous_month_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Month_layout.addWidget(current_month,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    Month_layout.addWidget(next_month_button,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignTop)
    Month_layout.addStretch(6)

    #Income and expenses windows 
    Incomes_and_expenses = QTabWidget()

    Incomes_window = QWidget()
    Incomes_window_layout = QHBoxLayout()
    
    add_incomes_category = create_button("Create category",(150,40))
    Incomes_window_layout.addWidget(add_incomes_category)

    Incomes_window_layout.setSpacing(70)
    Incomes_window.setLayout(Incomes_window_layout)
    # Incomes_window.setUpdatesEnabled(True)

    Incomes_scroll = QScrollArea()
    Incomes_scroll.setWidget(Incomes_window)
    Incomes_scroll.setWidgetResizable(True)
    Incomes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    Incomes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    Incomes_scroll.setObjectName("Income-window")
    Incomes_scroll.setStyleSheet("#Income-window{ border-color:rgba(0,205,0,100); border-width:2px }")
    # Incomes_scroll.setUpdatesEnabled(True)
        
    Expenses_window = QWidget()
    Expenses_window_layout = QHBoxLayout()

    add_expenses_category = create_button("Create category",(150,40))
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


    main_layout= QVBoxLayout()
    main_layout.addLayout(General_info)
    main_layout.addLayout(Year_layout)
    main_layout.addLayout(Month_layout)
    main_layout.addWidget(Incomes_and_expenses)

    window.setLayout(main_layout)



class Settings_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Settings")

    switch_themes_button = QToolButton()
    switch_themes_button.setIconSize(QSize(35,35))

    languages = QComboBox()
    languages.addItems(("English","Українська"))
    languages.setItemIcon(0,QIcon("./Images/English.png"))
    languages.setItemIcon(1,QIcon("./Images/Ukrainian.png"))

    accounts = QComboBox()
    accounts.setMinimumWidth(250)

    add_account = create_button("Add account",(130,50))
    delete_account = create_button("Delete account",(130,50))
    rename_account = create_button("Rename account",(150,50))

    main_layout = QVBoxLayout()
    main_layout.addWidget(switch_themes_button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(languages,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(accounts,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(add_account,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(rename_account,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(delete_account,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class Category_settings_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle(" ")

    rename_category = create_button("Rename category",(160,40))
    delete_category = create_button("Delete category",(160,40))
    show_statistics = create_button("Statistics",(150,40))

    main_layout = QVBoxLayout()
    main_layout.addWidget(rename_category,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(delete_category,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(show_statistics,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class Add_accoount_window():
    window = QDialog()
    window.resize(800,800)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Add account")

    message = QLabel()
    message.setWordWrap(True)
    message.setMinimumHeight(60)

    Full_name_layout = QHBoxLayout()
    name = QLineEdit()
    name.setPlaceholderText("Name")
    surname = QLineEdit()
    surname.setPlaceholderText("Surname")

    Full_name_layout.addWidget(name,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    Full_name_layout.addWidget(surname,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)

    button = create_button("",(120,50))
    current_balance = QLineEdit()
    current_balance.setPlaceholderText("Current balance")

    main_layout = QVBoxLayout()
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)    
    main_layout.addStretch(1)
    main_layout.addLayout(Full_name_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(current_balance,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)



class Add_category_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Add category")

    category_name = QLineEdit()
    category_name.setPlaceholderText("Category name")

    button = create_button("Add category",(140,40))

    main_layout = QVBoxLayout()

    main_layout.addWidget(category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)


