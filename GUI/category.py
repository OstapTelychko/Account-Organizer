from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QIcon

from project_configuration import ROOT_DIRECTORY
from languages import LANGUAGES
from AppObjects.category import Category
from AppObjects.account import Account
from GUI.windows.main import BASIC_FONT, ALIGMENT, ICON_SIZE, create_button, MainWindow
from GUI.windows.category import ChangeCategoryPositionWindow


ADD_TRANSACTION_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/add transaction.png")
REMOVE_TRANSACTION_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/remove transaction.png")
EDIT_TRANSACTION_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/edit transaction.png")



def load_category(category_type:str, name:str, account:Account, category_id:int, position:int, year:int, month:int, Language:str, theme:str) -> Category:
    """Add category to user window

        Arguments
        -------
            `type` (str): category type incomes or expenses

            `name` (str): category name

            `account` (str): account loads transactions by month from db

            `category_id` (int): category id to identify the 
            
            `position` (int): category position to order categories

            `year` (int): year of transactions

            `month` (int): month of transactions

            `Language` (str): Language for buttons and columns

        Returns
        ------
            `category` (Category): Category object  (name, type and links on add, delete, rename transaction buttons)
    """
    category_window = QWidget()
    category_window.setMaximumWidth(1000)
    category_window.setProperty("class", "category")
    category_window.setContentsMargins(10, 0, 10, 0)

    category_layout = QVBoxLayout()

    category_total_value = QLabel("")
    category_total_value.setFont(BASIC_FONT)

    category_name = QLabel(name)
    category_name.setFont(BASIC_FONT)

    category_settings = QToolButton()
    category_settings.setIcon(QIcon(f"{ROOT_DIRECTORY}/Images/Settings icon.png"))
    category_settings.setIconSize(QSize(30,30))

    Category_general_info = QHBoxLayout()
    Category_general_info.addWidget(category_total_value, alignment=ALIGMENT.AlignLeft)
    Category_general_info.addWidget(category_name, alignment=ALIGMENT.AlignHCenter)
    Category_general_info.addWidget(category_settings,alignment=ALIGMENT.AlignRight)

    category_data = QTableWidget()
    category_data.setProperty("class", "category_data")

    category_data.setMinimumWidth(600)
    category_data.setMinimumHeight(270)


    category_data.setColumnCount(4)
    category_data.setColumnHidden(3, True)

    header = category_data.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)# Name of transaction
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Custom)# Day of transaction
    category_data.setColumnWidth(1, 50)

    column = category_data.verticalHeader()
    column.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    category_data.setHorizontalHeaderLabels((LANGUAGES[Language]["Account"]["Info"][0], LANGUAGES[Language]["Account"]["Info"][1], LANGUAGES[Language]["Account"]["Info"][2]))
    row = category_data.horizontalHeader()
    row.setFont(BASIC_FONT)

    transactions = account.get_transactions_by_month(category_id, year, month)
    total_value = 0
    
    if len(transactions) > 0: #Check if transactions are in db
        category_data.setRowCount(len(transactions))
        for index,transaction in enumerate(transactions):

            transaction_day = QTableWidgetItem()
            transaction_day.setTextAlignment(ALIGMENT.AlignCenter)
            transaction_day.setData(Qt.ItemDataRole.EditRole, transaction.day)
            transaction_day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes so items can't be edited

            transaction_value = QTableWidgetItem()
            transaction_value.setTextAlignment(ALIGMENT.AlignCenter)
            transaction_value.setData(Qt.ItemDataRole.EditRole, transaction.value)
            transaction_value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            transaction_id = QTableWidgetItem()
            transaction_id.setData(Qt.ItemDataRole.EditRole, transaction.id)
            transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            transaction_name = QTableWidgetItem(transaction.name)
            transaction_name.setFlags(~ Qt.ItemFlag.ItemIsEditable)


            category_data.setItem(index, 0, transaction_name)
            category_data.setItem(index, 1, transaction_day)
            category_data.setItem(index, 2, transaction_value)
            category_data.setItem(index, 3, transaction_id)
            total_value += transaction.value
            
    category_total_value.setText(LANGUAGES[Language]["Account"]["Info"][6]+str(round(total_value, 2)))
    category_data.setSortingEnabled(True)

    add_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][0],(185,40))
    add_transaction.setIcon(ADD_TRANSACTION_ICON)
    add_transaction.setIconSize(ICON_SIZE)

    delete_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][1],(185,40))
    delete_transaction.setIcon(REMOVE_TRANSACTION_ICON)
    delete_transaction.setIconSize(ICON_SIZE)

    edit_transaction = create_button(LANGUAGES[Language]["Account"]["Transactions management"][2],(210,40))
    edit_transaction.setIcon(EDIT_TRANSACTION_ICON)
    edit_transaction.setIconSize(ICON_SIZE)
    
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

    if category_type == "Incomes":
        MainWindow.Incomes_window_layout.addWidget(category_window)
    else:
        MainWindow.Expenses_window_layout.addWidget(category_window)


    return Category(
        category_id,
        category_type,
        name,
        position,

        category_total_value,
        category_name,
        category_settings,
        category_data,
        add_transaction,
        delete_transaction,
        edit_transaction,
        category_window
    )


def add_category_to_position_list(category:Category):
    category_position = QLabel()
    category_position.setText(str(category.position))

    category_name_label = QLabel()
    category_name_label.setText(category.name)

    category_layout = QHBoxLayout()
    category_layout.addWidget(category_position, alignment=ALIGMENT.AlignHCenter)
    category_layout.addStretch(1)
    category_layout.addWidget(category_name_label, alignment=ALIGMENT.AlignLeft)

    category_container = QWidget()
    category_container.setMaximumWidth(350)
    category_container.setMinimumWidth(350)
    category_container.setContentsMargins(50, 0, 50, 0)
    category_container.setProperty("class", "category_list_item")
    category_container.setLayout((category_layout))

    ChangeCategoryPositionWindow.categories_list_layout.addWidget(category_container)