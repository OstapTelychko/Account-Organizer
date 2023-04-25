from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QLabel,QPushButton,QListWidget,QScrollArea,QApplication,QGridLayout,QMessageBox,QTabWidget,QToolButton,QComboBox,QDialog
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap,QIcon,QFont,QFontDatabase
from qdarktheme._style_loader import load_stylesheet



app = QApplication([])

ALIGMENT = Qt.AlignmentFlag
APP_ICON = QIcon("./Images/App icon.png")

dark_theme = load_stylesheet("dark")
dark_theme_icon = QIcon("./Images/Dark theme.png")

light_theme = load_stylesheet("light",custom_colors={"background":"#ffffff","foreground":"#191a1b"})
light_theme_icon = QIcon("./Images/Light theme.png")

# app.setStyleSheet(dark_theme)

messages_list = []
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
    messages_list.append(error)
    return error


def create_button(button_text:str,size:tuple[int])->QPushButton:
    button = QPushButton(text=button_text)
    # button.setFont(QFont("Calibri",pointSize=10))
    button.setFont(QFont("C059 [urw]",pointSize=10))
    button.setMinimumSize(*size)
    button.setMaximumSize(*size)
    return button


class Errors():
    incorrect_data_type_error = create_error("",False,QMessageBox.Icon.Warning)
    account_alredy_exists_error  = create_error("",False,QMessageBox.Icon.Warning)
    zero_current_balance_error = create_error("",True,QMessageBox.Icon.Question)



class Main_window():
    window = QWidget()
    window.resize(1400,750)
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
    Income_and_expenses = QTabWidget()
    for _ in range(3):
        Income_window = QWidget()
        Income_window_layout = QHBoxLayout()

        for _ in range(15):
            test_category_window = QWidget()
            test_category_layout = QVBoxLayout()
            test_category_name = QLabel("Test")
            delete_test_category = create_button("Delete category",(130,40))

            Category_general_info = QHBoxLayout()
            Category_general_info.addWidget(test_category_name, alignment=ALIGMENT.AlignHCenter)
            Category_general_info.addWidget(delete_test_category)

            category_data = QWidget()
            category_data_layout = QGridLayout()

            transaction_name_title = QLabel("Name")
            transaction_day_title = QLabel("Day")
            transaction_value_title = QLabel("Value")
            category_data_layout.addWidget(transaction_name_title,0,0)
            category_data_layout.addWidget(transaction_day_title,0,1,alignment=ALIGMENT.AlignLeft)
            category_data_layout.addWidget(transaction_value_title,0,2,alignment=ALIGMENT.AlignLeft)

            for iteration in range(1,15):
                transaction_name = QLabel("Ковбаса")
                transaction_day = QLabel("23")
                transaction_value = QLabel("1000")
                category_data_layout.addWidget(transaction_name,iteration,0)
                category_data_layout.addWidget(transaction_day,iteration,1,alignment=ALIGMENT.AlignLeft)
                category_data_layout.addWidget(transaction_value,iteration,2,alignment=ALIGMENT.AlignLeft)

            category_data.setLayout(category_data_layout)
            category_data_scroll = QScrollArea()
            category_data_scroll.setWidget(category_data)
            category_data_scroll.setWidgetResizable(True)
            category_data_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            category_data_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            category_data_scroll.setMinimumWidth(400)

            add_transaction = create_button("Make transaction",(130,40))
            delete_transaction = create_button("Delete transaction",(130,40))
            transactions_managment = QHBoxLayout()
            transactions_managment.addWidget(add_transaction)
            transactions_managment.addWidget(delete_transaction)

            test_category_layout.addStretch(1)
            test_category_layout.addLayout(Category_general_info)
            test_category_layout.addWidget(category_data_scroll)
            test_category_layout.addLayout(transactions_managment)
            test_category_layout.addStretch(20)

            Income_window_layout.addLayout(test_category_layout,20)
        Income_window_layout.setSpacing(70)
        Income_window.setLayout(Income_window_layout)
    
        Income_scroll = QScrollArea()
        Income_scroll.setWidget(Income_window)
        Income_scroll.setWidgetResizable(True)
        Income_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        Income_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        Income_scroll.setObjectName("Income-window")
        Income_scroll.setStyleSheet("#Income-window{ border-color:rgb(0,205,0); border-width:2px }")
            
        Income_and_expenses.addTab(Income_scroll,"Income")

    main_layout= QVBoxLayout()
    main_layout.addLayout(General_info)
    # main_layout.addStretch(1)
    main_layout.addLayout(Year_layout)
    main_layout.addLayout(Month_layout)
    # main_layout.addStretch(1)
    main_layout.addWidget(Income_and_expenses)


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
    accounts.setMinimumWidth(200)
    accounts.addItem("Ostap Telychko")

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
