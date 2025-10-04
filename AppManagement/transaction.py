from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt

from GUI.gui_constants import ALIGNMENT

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from DesktopQtToolkit.table_widget import CustomTableWidgetItem

from languages import LanguageStructure
from project_configuration import MONTHS_DAYS, CATEGORY_TYPE
from AppManagement.balance import update_account_balance

if TYPE_CHECKING:
    from DesktopQtToolkit.table_widget import CustomTableWidget



logger = get_logger(__name__)

def show_edit_transaction_window(category_name:str, category_data:CustomTableWidget) -> int:
    """Show edit transaction window. It allows to edit transaction data.

        Arguments
        ---------

        `category_name` : (str) - Name of the category. It will be shown in the window title.
        `category_data` : (CustomTableWidget) - Table widget with transaction data. It will be used to get selected row data.
    """

    selected_row = category_data.selectedItems()

    if len(selected_row) == 0 or len(selected_row) < 3:
        return WindowsRegistry.Messages.unselected_row.exec()
        
    if len(selected_row) > 3 or selected_row[0].row() != selected_row[1].row() or selected_row[0].row() != selected_row[2].row():
        return WindowsRegistry.Messages.only_one_row.exec()
    
    WindowsRegistry.TransactionManagementWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(5))
    WindowsRegistry.TransactionManagementWindow.message.setText(LanguageStructure.TransactionsMessages.get_translation(0))
    WindowsRegistry.TransactionManagementWindow.setWindowTitle(category_name)

    WindowsRegistry.TransactionManagementWindow.transaction_name.setText(selected_row[0].text())
    WindowsRegistry.TransactionManagementWindow.transaction_name.setFocus()
    WindowsRegistry.TransactionManagementWindow.transaction_day.setText(selected_row[1].text())
    WindowsRegistry.TransactionManagementWindow.transaction_value.setText(selected_row[2].text())

    WindowsRegistry.TransactionManagementWindow.transaction_id = int(category_data.item(selected_row[0].row(), 3).text()) # type: ignore[reportOptionalMemberAccess, unused-ignore] #This will never be None, because row is selected
    return WindowsRegistry.TransactionManagementWindow.exec()


def update_transaction(transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:float, category_data:CustomTableWidget) -> None:
    """Update transaction data. It updates transaction data in database and GUI.

        Arguments
        ---------

        `transaction_id` : (int) - Transaction id. It will be used to find transaction to update.
        `transaction_name` : (str) - Transaction name.
        `transaction_day` : (int) - Transaction day.
        `transaction_value` : (float) - Transaction value.
        `category_data` : (CustomTableWidget) - Table widget with transaction data. It will be used to update selected row data.
    """

    app_core = AppCore.instance()
    app_core.db.transaction_query.update_transaction(transaction_id, transaction_name, transaction_day, transaction_value)
                
    for row in range(category_data.rowCount()):
        if int(category_data.item(row, 3).text()) == transaction_id: # type: ignore[reportOptionalMemberAccess, unused-ignore] # We only access amount  of rows that is returned by rowCount()
            category_data.item(row, 0).setText(transaction_name) # type: ignore[reportOptionalMemberAccess, unused-ignore]
            category_data.item(row, 1).setText(str(transaction_day)) # type: ignore[reportOptionalMemberAccess, unused-ignore]

            old_value = float(category_data.item(row,2).text()) # type: ignore[reportOptionalMemberAccess, unused-ignore]
            values_difference = transaction_value - old_value

            if CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
                app_core.current_total_income += values_difference
                app_core.current_balance += values_difference
            else:
                app_core.current_total_expenses += values_difference
                app_core.current_balance -=  values_difference
            
            app_core.current_balance = round(app_core.current_balance, 2)
            app_core.current_total_income = round(app_core.current_total_income, 2)
            app_core.current_total_expenses = round(app_core.current_total_expenses, 2)

            category_data.item(row, 2).setText(str(transaction_value)) # type: ignore[reportOptionalMemberAccess, unused-ignore]


def show_add_transaction_window(category_name:str) -> None:
    """Show add transaction window. It allows to add transaction data.
        Arguments
        ---------

        `category_name` : (str) - Name of the category. It will be shown in the window title.
    """

    WindowsRegistry.TransactionManagementWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(1))
    WindowsRegistry.TransactionManagementWindow.message.setText(LanguageStructure.TransactionsMessages.get_translation(1))

    WindowsRegistry.TransactionManagementWindow.transaction_name.setText("")
    WindowsRegistry.TransactionManagementWindow.transaction_name.setFocus()
    WindowsRegistry.TransactionManagementWindow.transaction_day.setText("")
    WindowsRegistry.TransactionManagementWindow.transaction_value.setText("")

    WindowsRegistry.TransactionManagementWindow.setWindowTitle(category_name)
    WindowsRegistry.TransactionManagementWindow.exec()


def add_transaction(transaction_name:str, transaction_day:int, transaction_value:int|float, category_data:CustomTableWidget, category_id:int) -> None:
    """Add transaction data. It adds transaction data to database and GUI.
        Arguments
        ---------

        `transaction_name` : (str) - Transaction name.
        `transaction_day` : (int) - Transaction day.
        `transaction_value` : (int|float) - Transaction value.
        `category_data` : (CustomTableWidget) - Table widget with transaction data. It will be used to update selected row data.
        `category_id` : (int) - Category id. It will be used to find category which transaction should be added to.
    """

    app_core = AppCore.instance()
    transaction = app_core.db.transaction_query.add_transaction(
        category_id,
        app_core.current_year,
        app_core.current_month,
        transaction_day,
        transaction_value,
        transaction_name
    )

    if CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
        app_core.current_total_income = round(app_core.current_total_income + transaction_value, 2)
        app_core.current_balance = round(app_core.current_balance + transaction_value, 2)
    else:
        app_core.current_total_expenses = round(app_core.current_total_expenses + transaction_value, 2)
        app_core.current_balance = round(app_core.current_balance - transaction_value, 2)

    row = category_data.rowCount()
    category_data.setRowCount(row+1)

    day = CustomTableWidgetItem(str(transaction.day))
    day.setTextAlignment(ALIGNMENT.AlignCenter)
    day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes in this case cells in table can't be edited

    value = CustomTableWidgetItem(str(transaction.value))
    value.setTextAlignment(ALIGNMENT.AlignCenter)
    value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    transaction_id = CustomTableWidgetItem(str(transaction.id))
    transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    name = CustomTableWidgetItem(transaction_name)
    name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    category_data.setItem(row, 0, name)
    category_data.setItem(row, 1, day)
    category_data.setItem(row, 2, value)
    category_data.setItem(row, 3, transaction_id)
    WindowsRegistry.TransactionManagementWindow.hide()


def transaction_data_handler() -> int:
    """Handle transaction data. It checks if transaction data is valid and adds or updates transaction data."""

    from AppManagement.category import update_category_total_value

    transaction_name = WindowsRegistry.TransactionManagementWindow.transaction_name.text().strip()
    raw_transaction_day = WindowsRegistry.TransactionManagementWindow.transaction_day.text()
    raw_transaction_value = WindowsRegistry.TransactionManagementWindow.transaction_value.text()

    app_core = AppCore.instance()
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
    category = app_core.db.category_query.get_category(
        WindowsRegistry.TransactionManagementWindow.windowTitle(), category_type
    )
    if category is None:
        logger.error(f"Category {WindowsRegistry.TransactionManagementWindow.windowTitle()} not found. Transaction haven't been handled.")
        raise RuntimeError(f"Category {WindowsRegistry.TransactionManagementWindow.windowTitle()} not found. Transaction haven't been handled.")
    
    category_id = category.id
    category_data = app_core.categories[category_id].table_data

    max_month_day = MONTHS_DAYS[app_core.current_month-1] + (app_core.current_month == 2 and app_core.current_year % 4 == 0)#Add one day to February (29) if year is leap

    if raw_transaction_day == "" or raw_transaction_value == "":
        return WindowsRegistry.Messages.empty_fields.exec()
    
    if raw_transaction_value.replace(".","").replace(",","").isdigit() and raw_transaction_day.isdigit():
        transaction_day = int(raw_transaction_day)
    else:
        return WindowsRegistry.Messages.incorrect_data_type.exec()

    if not 0 < transaction_day <= max_month_day:
        WindowsRegistry.Messages.day_out_range.setText(LanguageStructure.Messages.get_translation(8)+f"1-{max_month_day}")
        return WindowsRegistry.Messages.day_out_range.exec()

    transaction_value = float(raw_transaction_value)

    if WindowsRegistry.TransactionManagementWindow.button.text() == LanguageStructure.GeneralManagement.get_translation(5): #Update 
        transaction_id = WindowsRegistry.TransactionManagementWindow.transaction_id
        update_transaction(transaction_id, transaction_name, transaction_day, transaction_value, category_data)
        logger.debug(f"Transaction updated: {transaction_name}\
                     | {transaction_day}\
                     | {transaction_value}\
                     | Transaction id: {transaction_id}\
                     | Category id: {category_id}")
    else: #Add
        add_transaction(transaction_name, transaction_day, transaction_value, category_data, category_id)
        logger.debug(f"Transaction added: {transaction_name}\
                     | {transaction_day}\
                     | {transaction_value}\
                     | Category id: {category_id}")


    update_category_total_value(category_id)
    
    update_account_balance()
    WindowsRegistry.TransactionManagementWindow.hide()
    return 1
        


def remove_transaction(category_data:CustomTableWidget, category_id:int) -> int:
    """Remove transaction. It removes transaction from database and GUI.

        Arguments
        ---------

        `category_data` : (CustomTableWidget) - Table widget with transaction data. It will be used to delete selected row data.
        `category_id` : (int) - Category id. It will be used to find category which transaction should be removed from.
    """
    from AppManagement.category import update_category_total_value

    app_core = AppCore.instance()
    selected_row = category_data.selectedItems()

    if len(selected_row) == 0 or len(selected_row) < 3:
        return WindowsRegistry.Messages.unselected_row.exec()
    
    if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
        transaction_id = int(category_data.item(selected_row[0].row(), 3).text()) # type: ignore[reportOptionalMemberAccess, unused-ignore] #This will never be None, because row is selected
    else:
        return WindowsRegistry.Messages.only_one_row.exec()

    WindowsRegistry.Messages.delete_transaction_confirmation.exec()
    ok_button = WindowsRegistry.Messages.delete_transaction_confirmation.ok_button
    if WindowsRegistry.Messages.delete_transaction_confirmation.clickedButton() == ok_button:
        transaction_value = float(selected_row[2].text())
        app_core.db.transaction_query.delete_transaction(transaction_id)

        category_data.removeRow(selected_row[0].row())

        update_category_total_value(category_id)

        if CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
            app_core.current_total_income -= transaction_value
            app_core.current_balance -= transaction_value
        else:
            app_core.current_total_expenses -= transaction_value
            app_core.current_balance += transaction_value
        
        app_core.current_balance = round(app_core.current_balance, 2)
        app_core.current_total_income = round(app_core.current_total_income, 2)
        app_core.current_total_expenses = round(app_core.current_total_expenses, 2)

        update_account_balance()
    
    return 1