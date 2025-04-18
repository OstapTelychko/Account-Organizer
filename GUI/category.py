from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QHeaderView, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from project_configuration import TRANSACTIONS_DIRECTORY, GENERAL_ICONS_DIRECTORY
from languages import LanguageStructure
from AppObjects.category import Category

from DesktopQtToolkit.table_widget import CustomTableWidget, CustomTableWidgetItem
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, ICON_SIZE, SHADOW_EFFECT_ARGUMENTS, BASIC_FONT
from GUI.windows.main_window import MainWindow
from GUI.windows.category import ChangeCategoryPositionWindow

if TYPE_CHECKING:
    from backend.db_controller import DBController

ADD_TRANSACTION_ICON = QIcon(f"{TRANSACTIONS_DIRECTORY}/add transaction.png")
REMOVE_TRANSACTION_ICON = QIcon(f"{TRANSACTIONS_DIRECTORY}/remove transaction.png")
EDIT_TRANSACTION_ICON = QIcon(f"{TRANSACTIONS_DIRECTORY}/edit transaction.png")



def load_category(category_type:str, name:str, db:DBController, category_id:int, position:int, year:int, month:int, Language:str) -> Category:
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
    category_window.setGraphicsEffect(QGraphicsDropShadowEffect(category_window, **SHADOW_EFFECT_ARGUMENTS))

    category_layout = QVBoxLayout()

    category_total_value = QLabel("")
    category_total_value.setFont(BASIC_FONT)

    category_name = QLabel(name)
    category_name.setFont(BASIC_FONT)

    category_settings = QToolButton()
    category_settings.setIcon(QIcon(f"{GENERAL_ICONS_DIRECTORY}/Settings icon.png"))
    category_settings.setIconSize(QSize(30,30))

    Category_general_info = QHBoxLayout()
    Category_general_info.addWidget(category_total_value, alignment=ALIGNMENT.AlignLeft)
    Category_general_info.addWidget(category_name, alignment=ALIGN_H_CENTER)
    Category_general_info.addWidget(category_settings,alignment=ALIGNMENT.AlignRight)

    category_data = CustomTableWidget()
    category_data.setProperty("class", "category_data")

    category_data.setMinimumWidth(600)
    category_data.setMinimumHeight(270)

    category_data.setColumnCount(4)
    category_data.setColumnHidden(3, True)

    row = category_data.horizontalHeader()
    row.setFont(BASIC_FONT)
    row.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    row.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)# Name of transaction
    row.setSectionResizeMode(1, QHeaderView.ResizeMode.Custom)# Day of transaction
    category_data.setColumnWidth(1, 50)

    column = category_data.verticalHeader()
    column.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    category_data.setHorizontalHeaderLabels((LanguageStructure.Transactions.get_translation(0), LanguageStructure.Transactions.get_translation(1), LanguageStructure.Transactions.get_translation(2)))

    transactions = db.transaction_query.get_transactions_by_month(category_id, year, month)
    
    if len(transactions) > 0: #Check if transactions are in db
        category_data.setRowCount(len(transactions))
        for index,transaction in enumerate(transactions):

            transaction_day = CustomTableWidgetItem(str(transaction.day))
            transaction_day.setTextAlignment(ALIGNMENT.AlignCenter)
            transaction_day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes so items can't be edited

            transaction_value = CustomTableWidgetItem(str(transaction.value))
            transaction_value.setTextAlignment(ALIGNMENT.AlignCenter)
            transaction_value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            transaction_id = CustomTableWidgetItem(str(transaction.id))
            transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            transaction_name = CustomTableWidgetItem(transaction.name)
            transaction_name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

            category_data.setItem(index, 0, transaction_name)
            category_data.setItem(index, 1, transaction_day)
            category_data.setItem(index, 2, transaction_value)
            category_data.setItem(index, 3, transaction_id)
            
    category_total_value.setText(LanguageStructure.Categories.get_translation(10)+str(round(db.statistics_query.get_monthly_transactions_sum(category_id, year, month), 2)))
    category_data.setSortingEnabled(True)

    add_transaction = create_button(LanguageStructure.GeneralManagement.get_translation(1),(185,40))
    add_transaction.setIcon(ADD_TRANSACTION_ICON)
    add_transaction.setIconSize(ICON_SIZE)

    delete_transaction = create_button(LanguageStructure.GeneralManagement.get_translation(0),(185,40))
    delete_transaction.setIcon(REMOVE_TRANSACTION_ICON)
    delete_transaction.setIconSize(ICON_SIZE)

    edit_transaction = create_button(LanguageStructure.GeneralManagement.get_translation(7),(210,40))
    edit_transaction.setIcon(EDIT_TRANSACTION_ICON)
    edit_transaction.setIconSize(ICON_SIZE)
    
    transactions_managment = QHBoxLayout()
    transactions_managment.addWidget(add_transaction)
    transactions_managment.addWidget(delete_transaction)
    transactions_managment.addWidget(edit_transaction)

    category_layout.addStretch(1)
    category_layout.addLayout(Category_general_info)
    category_layout.addWidget(category_data,alignment=ALIGN_V_CENTER)
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
    """Add category to categories positions list

        Arguments
        -------
            `category` (Category): Category object to add to the list
    """

    category_position = QLabel()
    category_position.setProperty("class", "category_list_item")
    category_position.setText(str(category.position))

    category_name_label = QLabel()
    category_name_label.setProperty("class", "light-text")
    category_name_label.setText(category.name)

    category_layout = QHBoxLayout()
    category_layout.addWidget(category_position, alignment=ALIGN_H_CENTER)
    category_layout.addStretch(1)
    category_layout.addWidget(category_name_label, alignment=ALIGNMENT.AlignLeft)

    category_container = QWidget()
    category_container.setMaximumWidth(380)
    category_container.setMinimumWidth(380)
    category_container.setContentsMargins(20, 0, 20, 0)
    category_container.setProperty("class", "category_list_item")
    category_container.setLayout(category_layout)

    ChangeCategoryPositionWindow.categories_list_layout.addWidget(category_container)