from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt
from datetime import date
from calendar import monthrange

from GUI.gui_constants import ALIGNMENT

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from DesktopQtToolkit.Utils import get_table_widget_item

from languages import LanguageStructure
from project_configuration import CategoryType, InvestmentOperation
from AppManagement.balance import update_account_balance, calculate_current_balance
from project_configuration import MAX_TRANSACTION_VALUE
from backend.models import Transaction
from backend.investment_query import calculate_investment_timeline

if TYPE_CHECKING:
    from DesktopQtToolkit.table_widget import CustomTableWidget
    from DesktopQtToolkit.message_window import MessageWindow



logger = get_logger(__name__)

def get_row_selection_error(category_data:CustomTableWidget) -> MessageWindow | None:
    """Check that exactly one whole row is selected in a category table.

        Arguments
        ---------
        `category_data` : (CustomTableWidget) - Table widget with transaction data.

        Returns
        -------
        `MessageWindow | None` - Message to show if the selection is wrong, otherwise None.
    """

    visible_columns = sum(
        not category_data.isColumnHidden(column) for column in range(category_data.columnCount())
    )
    selected_items = category_data.selectedItems()

    if len(selected_items) < visible_columns:
        return WindowsRegistry.Messages.unselected_row
    if len(selected_items) > visible_columns or len({item.row() for item in selected_items}) != 1:
        return WindowsRegistry.Messages.only_one_row
    return None


def update_transaction_value_placeholder() -> None:
    """Show "Current value" placeholder of the value field for Investments revaluations."""

    window = WindowsRegistry.TransactionManagementWindow
    if not window.operation_type.isHidden() and window.operation_type.currentData() == InvestmentOperation.Revaluation:
        window.transaction_value.setPlaceholderText(LanguageStructure.Investments.get_translation(8))
    else:
        window.transaction_value.setPlaceholderText(LanguageStructure.Transactions.get_translation(2))


def show_edit_transaction_window(category_name:str, category_data:CustomTableWidget) -> int:
    """Show edit transaction window. It allows to edit transaction data.

        Arguments
        ---------

        `category_name` : (str) - Name of the category. It will be shown in the window title.
        `category_data` : (CustomTableWidget) - Table widget with transaction data. It will be used to get selected row data.
    """

    selection_error = get_row_selection_error(category_data)
    if selection_error is not None:
        return selection_error.exec()
    row = category_data.selectedItems()[0].row()
    
    WindowsRegistry.TransactionManagementWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(5))
    WindowsRegistry.TransactionManagementWindow.message.setText(LanguageStructure.TransactionsMessages.get_translation(0))
    WindowsRegistry.TransactionManagementWindow.setWindowTitle(category_name)

    WindowsRegistry.TransactionManagementWindow.transaction_name.setText(get_table_widget_item(category_data, row, 0).text())
    WindowsRegistry.TransactionManagementWindow.transaction_name.setFocus()
    WindowsRegistry.TransactionManagementWindow.transaction_day.setText(get_table_widget_item(category_data, row, 1).text())
    WindowsRegistry.TransactionManagementWindow.transaction_value.setText(get_table_widget_item(category_data, row, 2).text())

    operation_type = WindowsRegistry.TransactionManagementWindow.operation_type
    is_investment = WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == CategoryType.get_index(
        CategoryType.Investment
    )
    operation_type.setVisible(is_investment)
    if is_investment:
        operation_type.setCurrentIndex(operation_type.findText(get_table_widget_item(category_data, row, 4).text()))
    update_transaction_value_placeholder()

    WindowsRegistry.TransactionManagementWindow.transaction_id = int(get_table_widget_item(category_data, row, 3).text())
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
        if int(get_table_widget_item(category_data, row, 3).text()) == transaction_id:
            get_table_widget_item(category_data, row, 0).setText(transaction_name)
            get_table_widget_item(category_data, row, 1).setText(str(transaction_day))

            old_value = float(get_table_widget_item(category_data, row, 2).text())
            values_difference = transaction_value - old_value

            if CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()) == CategoryType.Income:
                app_core.current_total_income += values_difference
                app_core.current_balance += values_difference
            else:
                app_core.current_total_expenses += values_difference
                app_core.current_balance -=  values_difference
            
            app_core.current_balance = round(app_core.current_balance, 2)
            app_core.current_total_income = round(app_core.current_total_income, 2)
            app_core.current_total_expenses = round(app_core.current_total_expenses, 2)

            get_table_widget_item(category_data, row, 2).setText(str(transaction_value))


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

    WindowsRegistry.TransactionManagementWindow.operation_type.setCurrentIndex(0)
    WindowsRegistry.TransactionManagementWindow.operation_type.setVisible(
        WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == CategoryType.get_index(CategoryType.Investment)
    )
    update_transaction_value_placeholder()

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
        date(app_core.current_year, app_core.current_month, transaction_day),
        transaction_value,
        transaction_name
    )

    if CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()) == CategoryType.Income:
        app_core.current_total_income = round(app_core.current_total_income + transaction_value, 2)
        app_core.current_balance = round(app_core.current_balance + transaction_value, 2)
    else:
        app_core.current_total_expenses = round(app_core.current_total_expenses + transaction_value, 2)
        app_core.current_balance = round(app_core.current_balance - transaction_value, 2)

    row = category_data.rowCount()
    category_data.setRowCount(row+1)

    day = CustomTableWidgetItem(str(transaction.date.day))
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
    category_type = CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    category = app_core.db.category_query.get_category(
        WindowsRegistry.TransactionManagementWindow.windowTitle(), category_type
    )
    if category is None:
        logger.error(f"Category {WindowsRegistry.TransactionManagementWindow.windowTitle()} not found. Transaction haven't been handled.")
        raise RuntimeError(f"Category {WindowsRegistry.TransactionManagementWindow.windowTitle()} not found. Transaction haven't been handled.")
    
    category_id = category.id
    category_data = app_core.categories[category_id].table_data

    _, max_month_day = monthrange(app_core.current_year, app_core.current_month)

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

    min_value = category.transaction_min_value if category.transaction_min_value is not None else 0
    max_value = category.transaction_max_value if category.transaction_max_value is not None else 0
    if min_value != 0 and transaction_value < min_value or max_value != 0 and transaction_value > max_value:
        WindowsRegistry.Messages.transaction_value_anomalous.setText(
            LanguageStructure.Messages.get_translation(37)
            .replace("%transaction_value%", str(transaction_value))
            .replace("%min_value%", str(min_value))
            .replace("%max_value%", str(max_value or MAX_TRANSACTION_VALUE))
        )
        return WindowsRegistry.Messages.transaction_value_anomalous.exec()

    is_update = WindowsRegistry.TransactionManagementWindow.button.text() == LanguageStructure.GeneralManagement.get_translation(5)

    if category_type == CategoryType.Investment:
        operation_type = InvestmentOperation(WindowsRegistry.TransactionManagementWindow.operation_type.currentData())
        transaction_date = date(app_core.current_year, app_core.current_month, transaction_day)

        if transaction_date > date.today():
            return WindowsRegistry.Messages.future_investment_operation.exec()

        if operation_type != InvestmentOperation.Revaluation and transaction_value == 0:
            return WindowsRegistry.Messages.zero_investment_value.exec()

        transaction_id = WindowsRegistry.TransactionManagementWindow.transaction_id if is_update else None
        category_transactions = [
            transaction for transaction in app_core.db.transaction_query.get_all_transactions(category_id)
            if transaction.id != transaction_id
        ]
        category_transactions.append(Transaction(
            id=transaction_id, date=transaction_date, value=transaction_value,
            operation_type=operation_type, category_id=category_id
        ))
        if any(point.value_after < 0 for point in calculate_investment_timeline(category_transactions)):
            return WindowsRegistry.Messages.negative_investment_value.exec()

        if transaction_id is not None:
            app_core.db.transaction_query.update_transaction(
                transaction_id, transaction_name, transaction_day, transaction_value, operation_type
            )
            logger.info(
                f'[ENTITY: INVESTMENT] [ACTION: UPDATED] id={transaction_id} operation={operation_type.name} '
                f'name="{transaction_name}" date={transaction_date} value={transaction_value} category_id={category_id}'
            )
        else:
            app_core.db.transaction_query.add_transaction(
                category_id, transaction_date, transaction_value, transaction_name, operation_type
            )
            logger.info(
                f'[ENTITY: INVESTMENT] [ACTION: {operation_type.name.upper()}] name="{transaction_name}" '
                f'date={transaction_date} value={transaction_value} category_id={category_id}'
            )

        update_category_total_value(category_id)
        calculate_current_balance()
        WindowsRegistry.TransactionManagementWindow.hide()
        return 1

    if is_update:
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
    selection_error = get_row_selection_error(category_data)
    if selection_error is not None:
        return selection_error.exec()
    row = category_data.selectedItems()[0].row()
    transaction_id = int(get_table_widget_item(category_data, row, 3).text())
    category_type = CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())

    if category_type == CategoryType.Investment and any(
        point.value_after < 0 for point in calculate_investment_timeline(
            transaction for transaction in app_core.db.transaction_query.get_all_transactions(category_id)
            if transaction.id != transaction_id
        )
    ):
        return WindowsRegistry.Messages.negative_investment_value.exec()

    WindowsRegistry.Messages.delete_transaction_confirmation.exec()
    ok_button = WindowsRegistry.Messages.delete_transaction_confirmation.ok_button
    if WindowsRegistry.Messages.delete_transaction_confirmation.clickedButton() == ok_button:
        transaction_value = float(get_table_widget_item(category_data, row, 2).text())
        app_core.db.transaction_query.delete_transaction(transaction_id)

        if category_type == CategoryType.Investment:
            logger.info(
                f"[ENTITY: INVESTMENT] [ACTION: DELETED] id={transaction_id} value={transaction_value} "
                f"category_id={category_id}"
            )
            update_category_total_value(category_id)
            calculate_current_balance()
            return 1

        category_data.removeRow(row)

        update_category_total_value(category_id)

        if category_type == CategoryType.Income:
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