from __future__ import annotations
import os

from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QHeaderView,\
    QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from project_configuration import TRANSACTIONS_DIRECTORY, GENERAL_ICONS_DIRECTORY
from languages import LanguageStructure
from AppObjects.category import Category
from AppObjects.windows_registry import WindowsRegistry
from backend.models import Transaction, Category as CategoryModel

from DesktopQtToolkit.table_widget import CustomTableWidget, CustomTableWidgetItem
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, ICON_SIZE, SHADOW_EFFECT_ARGUMENTS, BASIC_FONT

if TYPE_CHECKING:
    from backend.db_controller import DBController

ADD_TRANSACTION_ICON = QIcon(os.path.join(TRANSACTIONS_DIRECTORY, "add transaction.png"))
REMOVE_TRANSACTION_ICON = QIcon(os.path.join(TRANSACTIONS_DIRECTORY, "remove transaction.png"))
EDIT_TRANSACTION_ICON = QIcon(os.path.join(TRANSACTIONS_DIRECTORY, "edit transaction.png"))


def load_transactions_into_category_table(category_data:CustomTableWidget, transactions:list[Transaction]) -> None:
    """Load transactions into category table widget

        Arguments
        -------
            `category_data` (CustomTableWidget): Table widget to load transactions into<br>
            `transactions` (list[Transaction]): List of transactions to load into the table
    """

    category_data.setRowCount(len(transactions))
    for index,transaction in enumerate(transactions):

        transaction_day = CustomTableWidgetItem(str(transaction.date.day))
        transaction_day.setTextAlignment(ALIGNMENT.AlignCenter)
        transaction_day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes so items can't be edited

        transaction_value = CustomTableWidgetItem(str(transaction.value))
        transaction_value.setTextAlignment(ALIGNMENT.AlignCenter)
        transaction_value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

        transaction_id = CustomTableWidgetItem(str(transaction.id))
        transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

        transaction_name = CustomTableWidgetItem(str(transaction.name))
        transaction_name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

        category_data.setItem(index, 0, transaction_name)
        category_data.setItem(index, 1, transaction_day)
        category_data.setItem(index, 2, transaction_value)
        category_data.setItem(index, 3, transaction_id)


def load_category(category:CategoryModel, db:DBController, year:int, month:int) -> Category:
    """Add category to user window

        Arguments
        -------
            `category` (CategoryModel): Category model object to load into the window<br>
            `db` (DBController): Database controller to get transactions and statistics data<br>
            `year` (int): Year of transactions to load<br>
            `month` (int): Month of transactions to load

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

    category_name = QLabel(category.name)
    category_name.setFont(BASIC_FONT)

    category_settings = QToolButton()
    category_settings.setIcon(QIcon(os.path.join(GENERAL_ICONS_DIRECTORY, "Settings icon.png")))
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
    column.setStretchLastSection(True)

    category_data.setHorizontalHeaderLabels((
        LanguageStructure.Transactions.get_translation(0),
        LanguageStructure.Transactions.get_translation(1),
        LanguageStructure.Transactions.get_translation(2)
    ))

    transactions = db.transaction_query.get_transactions_by_month(category.id, year, month)
    
    if len(transactions) > 0: #Check if transactions are in db
        load_transactions_into_category_table(category_data, transactions)
    category_total = round(db.statistics_query.get_monthly_transactions_sum(category.id, year, month), 2)
    category_total_value.setText(
        f"{LanguageStructure.Categories.get_translation(10)}{category_total}"
    )
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
    
    transactions_management = QHBoxLayout()
    transactions_management.addWidget(add_transaction)
    transactions_management.addWidget(delete_transaction)
    transactions_management.addWidget(edit_transaction)

    category_layout.addStretch(1)
    category_layout.addLayout(Category_general_info)
    category_layout.addWidget(category_data,alignment=ALIGN_V_CENTER)
    category_layout.addLayout(transactions_management)
    category_layout.addStretch(1)

    category_window.setLayout(category_layout)

    if category.category_type == "Incomes":
        WindowsRegistry.MainWindow.Incomes_window_layout.addWidget(category_window)
    else:
        WindowsRegistry.MainWindow.Expenses_window_layout.addWidget(category_window)


    return Category(
        category.id,
        category.category_type,
        category.name,
        category.position,
        category.transaction_min_value,
        category.transaction_max_value,

        category_total_value,
        category_name,
        category_settings,
        category_data,
        add_transaction,
        delete_transaction,
        edit_transaction,
        category_window
    )


def add_category_to_position_list(category:Category) -> None:
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

    WindowsRegistry.ChangeCategoryPositionWindow.categories_list_layout.addWidget(category_container)