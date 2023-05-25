from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QLabel,QPushButton,QScrollArea,QApplication,QGridLayout,QMessageBox,QTabWidget,QToolButton,QComboBox,QDialog,QTableWidget,QTableWidgetItem,QHeaderView,QListWidget
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap,QIcon,QFont,QFontDatabase
from qdarktheme._style_loader import load_stylesheet
from Accont_mangment import Account


app = QApplication([])

ALIGMENT = Qt.AlignmentFlag
APP_ICON = QIcon("./Images/App icon.png")
Languages_loaded = False

dark_theme = load_stylesheet("dark")
dark_theme_icon = QIcon("./Images/Dark theme.png")

light_theme = load_stylesheet("light",custom_colors={"background":"#ebeef0","foreground":"#191a1b"})
light_theme_icon = QIcon("./Images/Light theme.png")

errors_list = []

# print(QFontDatabase.families())
def create_error(type_confirm:bool,icon:QMessageBox.Icon) -> QMessageBox:
    error = QMessageBox()
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
    button.setFont(QFont("C059 [urw]",pointSize=12))
    button.setMinimumSize(*size)
    button.setMaximumSize(*size)
    return button


def load_category(category_type:str,name:str,account:Account,category_id:int,year:int,month:int,Language:str,theme:str)-> dict:

    if not Languages_loaded:
        from Languages import LANGUAGES
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
            `category` (dict): Dictionary with category name, type and link on add, delete, rename transaction buttons
    """

    category = {}
    category["Type"] = category_type

    category_window = QWidget()
    category_window.setMaximumWidth(1000)
    category_layout = QVBoxLayout()

    category_total_value = QLabel("")
    category["Total value"] = category_total_value

    category_name = QLabel(name)
    category["Name"] = name
    category["Name label"] = category_name

    category_settings = QToolButton()
    category_settings.setIcon(QIcon("./Images/Settings icon.png"))
    category_settings.setIconSize(QSize(30,30))
    category["Settings"] = category_settings

    Category_general_info = QHBoxLayout()
    Category_general_info.addWidget(category_total_value, alignment=ALIGMENT.AlignLeft)
    Category_general_info.addWidget(category_name, alignment=ALIGMENT.AlignHCenter)
    Category_general_info.addWidget(category_settings,alignment=ALIGMENT.AlignRight)

    category_data = QTableWidget()
    category["Category data"] = category_data

    category_data.setMinimumWidth(600)
    category_data.setMinimumHeight(270)

    
    if theme == "Dark":
        category_data.setStyleSheet("QTableWidget{background-color:rgb(45,45,45)}")
    else:
        category_data.setStyleSheet("QTableWidget{background-color:rgb(205,205,205)}")

    category_data.setColumnCount(4)
    category_data.setColumnHidden(3,True)

    header = category_data.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)

    row = category_data.verticalHeader()
    row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    category_data.setHorizontalHeaderLabels((LANGUAGES[Language]["Account"]["Info"][0],LANGUAGES[Language]["Account"]["Info"][1],LANGUAGES[Language]["Account"]["Info"][2]))

    transactions = account.get_transactions_by_month(category_id,year,month)
    total_value = 0

    if len(transactions) > 0: #Check if transactions are in db
        category_data.setRowCount(len(transactions))
        for index,transaction in enumerate(transactions):
            transaction_day = QTableWidgetItem()
            transaction_day.setData(Qt.ItemDataRole.EditRole,transaction[4])
            transaction_day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes so items can't be edited

            transaction_value = QTableWidgetItem()
            transaction_value.setData(Qt.ItemDataRole.EditRole,transaction[5])
            transaction_value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            transaction_id = QTableWidgetItem()
            transaction_id.setData(Qt.ItemDataRole.EditRole,transaction[0])
            transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            transaction_name = QTableWidgetItem(transaction[6])
            transaction_name.setFlags(~ Qt.ItemFlag.ItemIsEditable)
            
            category_data.setItem(index,0,transaction_name)
            category_data.setItem(index,1,transaction_day)
            category_data.setItem(index,2,transaction_value)
            category_data.setItem(index,3,transaction_id)
            total_value += transaction[5]
            
    category_total_value.setText(LANGUAGES[Language]["Account"]["Info"][6]+str(total_value))
    category_data.setSortingEnabled(True)


    add_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][0],(185,40))
    delete_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][1],(185,40))
    edit_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][2],(210,40))
    
    category["Add transaction"] = add_transaction
    category["Delete transaction"] = delete_transaction
    category["Edit transaction"] = edit_transaction

    transactions_managment = QHBoxLayout()
    transactions_managment.addWidget(add_transaction)
    transactions_managment.addWidget(delete_transaction)
    transactions_managment.addWidget(edit_transaction)

    category_layout.addStretch(1)
    category_layout.addLayout(Category_general_info)
    category_layout.addWidget(category_data,alignment=ALIGMENT.AlignVCenter)
    category_layout.addLayout(transactions_managment)
    category_layout.addStretch(1)

    category_window.setLayout(category_layout)
    category["Category window"] = category_window

    if category_type == "Incomes":
        Main_window.Incomes_window_layout.addWidget(category_window)
    else:
        Main_window.Expenses_window_layout.addWidget(category_window)
    return category


class Errors():
    incorrect_data_type_error = create_error(False,QMessageBox.Icon.Warning)
    account_alredy_exists_error  = create_error(False,QMessageBox.Icon.Warning)
    zero_current_balance_error = create_error(True,QMessageBox.Icon.Question)
    category_exists_error = create_error(False,QMessageBox.Icon.Warning)
    delete_category_question = create_error(True,QMessageBox.Icon.Question)
    unselected_row_error = create_error(False,QMessageBox.Icon.Warning)
    only_one_row_error = create_error(False,QMessageBox.Icon.Warning)
    empty_fields_error = create_error(False,QMessageBox.Icon.Warning)
    day_out_range_error = create_error(False,QMessageBox.Icon.Critical)
    delete_transaction_question = create_error(True,QMessageBox.Icon.Question)
    load_account_question =  create_error(True,QMessageBox.Icon.Question)
    delete_account_warning = create_error(True,QMessageBox.Icon.Critical)
    empty_expression_error = create_error(False,QMessageBox.Icon.Information)
    forbidden_calculator_word_error = create_error(False,QMessageBox.Icon.Critical)



class Main_window():
    window = QWidget()
    window.resize(1400,750)
    window.setMinimumHeight(650)
    window.setMinimumWidth(1150)
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
    Incomes_window.setMinimumHeight(400)
    Incomes_window_layout = QHBoxLayout()
    
    add_incomes_category = create_button("Create category",(170,40))
    Incomes_window_layout.addWidget(add_incomes_category)

    Incomes_window_layout.setSpacing(70)
    Incomes_window.setLayout(Incomes_window_layout)
    Incomes_window.setUpdatesEnabled(True)

    Incomes_scroll = QScrollArea()
    Incomes_scroll.setWidget(Incomes_window)
    Incomes_scroll.setWidgetResizable(True)
    Incomes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    Incomes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    Incomes_scroll.setObjectName("Income-window")
    Incomes_scroll.setStyleSheet("#Income-window{ border-color:rgba(0,205,0,100); border-width:2px }")
    Incomes_scroll.setUpdatesEnabled(True)
        
    Expenses_window = QWidget()
    Expenses_window_layout = QHBoxLayout()

    add_expenses_category = create_button("Create category",(170,40))
    Expenses_window_layout.addWidget(add_expenses_category)
        
    Expenses_window_layout.setSpacing(70)
    Expenses_window.setLayout(Expenses_window_layout)
    Expenses_window.setUpdatesEnabled(True)

    Expenses_scroll = QScrollArea()
    Expenses_scroll.setWidget(Expenses_window)
    Expenses_scroll.setWidgetResizable(True)
    Expenses_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    Expenses_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    Expenses_scroll.setObjectName("Expenses-window")
    Expenses_scroll.setStyleSheet("#Expenses-window{ border-color:rgba(205,0,0,100); border-width:2px }")
    Expenses_scroll.setUpdatesEnabled(True)

    Incomes_and_expenses.addTab(Incomes_scroll,"Income")
    Incomes_and_expenses.addTab(Expenses_scroll,"Expenses")

    window_bottom = QHBoxLayout()
    statistics = create_button("Statistics",(160,40))
    mini_calculator_label = QLabel("Mini-calculator")
    mini_calculator_text = QLineEdit()
    mini_calculator_text.setPlaceholderText("2 * 3 = 6;  3 / 2 = 1.5;  3 + 2 = 5;  2 - 3 = -1;  4 ** 2 = 16")
    mini_calculator_text.setMinimumWidth(600)
    calculate = create_button("=",(100,40))
    calculate.setFont(QFont("C059 [urw]",pointSize=18))

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

    add_account = create_button("Add account",(150,50))
    delete_account = create_button("Delete account",(150,50))
    rename_account = create_button("Rename account",(180,50))

    total_income = QLabel()
    total_expense = QLabel()
    account_created_date = QLabel()

    main_layout = QVBoxLayout()
    main_layout.addStretch(2)
    main_layout.addWidget(switch_themes_button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addWidget(languages,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addWidget(accounts,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(5)
    main_layout.addWidget(add_account,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addWidget(rename_account,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addWidget(delete_account,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(5)
    main_layout.addWidget(total_income,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignBottom)
    main_layout.addStretch(1)
    main_layout.addWidget(total_expense,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignBottom)
    main_layout.addStretch(1)
    main_layout.addWidget(account_created_date,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignBottom)

    window.setLayout(main_layout)



class Category_settings_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle(" ")

    rename_category = create_button("Rename category",(195,40))
    delete_category = create_button("Delete category",(180,40))

    main_layout = QVBoxLayout()
    main_layout.addWidget(rename_category,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(delete_category,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class Add_account_window():
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

    button = create_button("",(140,50))
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



class Rename_account_window():
    window = QDialog()
    window.resize(800,800)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Rename account")
    
    message = QLabel()

    new_name = QLineEdit("New name")
    new_surname = QLineEdit("New Surname")
    full_name_layout = QHBoxLayout()
    full_name_layout.addWidget(new_name,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    full_name_layout.addWidget(new_surname,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)

    button = create_button("Update",(160,40))

    main_layout = QVBoxLayout()
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addLayout(full_name_layout)
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

    button = create_button("Add category",(160,40))

    main_layout = QVBoxLayout()

    main_layout.addWidget(category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class Rename_category_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Rename")

    new_category_name = QLineEdit()
    new_category_name.setMinimumWidth(150)
    new_category_name.setPlaceholderText("New name")
    button = create_button("Rename",(170,40))

    main_layout = QVBoxLayout()
    # main_layout.addSt
    main_layout.addWidget(new_category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class Transaction_management_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Edit")

    message = QLabel()

    transaction_layout = QHBoxLayout()
    transaction_name = QLineEdit()
    transaction_day = QLineEdit()
    transaction_value = QLineEdit()
    transaction_id = None

    transaction_layout.addWidget(transaction_name,alignment=ALIGMENT.AlignVCenter)
    transaction_layout.addWidget(transaction_day,alignment=ALIGMENT.AlignVCenter)
    transaction_layout.addWidget(transaction_value,alignment=ALIGMENT.AlignVCenter)

    button = create_button("",(150,40))

    main_layout = QVBoxLayout()
    main_layout.addStretch(1)
    main_layout.addWidget(message,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.addLayout(transaction_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)



class Statistcs_window():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Statistics")

    monthly_statistics = create_button("Monthly",(150,40))
    quarterly_statistics = create_button("Quarterly",(150,40))
    yearly_statistics = create_button("Yearly",(150,40))

    main_layout = QVBoxLayout()
    main_layout.addSpacing(50)
    main_layout.addWidget(monthly_statistics,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    main_layout.addWidget(quarterly_statistics,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    main_layout.addWidget(yearly_statistics,alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)

    window.setLayout(main_layout)



class Monthly_statistics():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("April")
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on mouseover
    
    statistics = QListWidget()
    main_layout = QVBoxLayout()
    main_layout.addWidget(statistics)

    window.setLayout(main_layout)
