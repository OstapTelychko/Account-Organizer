from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt

from GUI.gui_constants import ALIGNMENT
from GUI.windows.main_window import MainWindow
from GUI.windows.messages import Messages
from GUI.windows.transaction import TransactionManagementWindow

from AppObjects.session import Session
from AppObjects.logger import get_logger
from DesktopQtToolkit.table_widget import CustomTableWidgetItem, CustomTableWidget
from languages import LANGUAGES
from project_configuration import MONTHS_DAYS, CATEGORY_TYPE
from AppManagement.balance import update_account_balance



logger = get_logger(__name__)

def show_edit_transaction_window(category_name:str, category_data:CustomTableWidget):
    selected_row = category_data.selectedItems()

    if len(selected_row) == 0 or len(selected_row) < 3:
        return Messages.unselected_row.exec()
        
    if len(selected_row) > 3 or selected_row[0].row() != selected_row[1].row() or selected_row[0].row() != selected_row[2].row():
        return Messages.only_one_row.exec()
    
    TransactionManagementWindow.button.setText(LANGUAGES[Session.language]["General management"][5])
    TransactionManagementWindow.message.setText(LANGUAGES[Session.language]["Windows"]["Main"]["Transactions"]["Messages"][0])
    TransactionManagementWindow.window.setWindowTitle(category_name)

    TransactionManagementWindow.transaction_name.setText(selected_row[0].text())
    TransactionManagementWindow.transaction_name.setFocus()
    TransactionManagementWindow.transaction_day.setText(selected_row[1].text())
    TransactionManagementWindow.transaction_value.setText(selected_row[2].text())

    TransactionManagementWindow.transaction_id = int(category_data.item(selected_row[0].row(), 3).text())
    TransactionManagementWindow.window.exec()


def update_transaction(transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int|float, category_data:CustomTableWidget):
    Session.db.transaction_query.update_transaction(transaction_id, transaction_name, transaction_day, transaction_value)
                
    for row in range(category_data.rowCount()):
        if int(category_data.item(row, 3).text()) == transaction_id:
            category_data.item(row, 0).setText(transaction_name)
            category_data.item(row, 1).setText(str(transaction_day))

            old_value = float(category_data.item(row,2).text())
            values_difference = transaction_value - old_value

            if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
                Session.current_total_income += values_difference
                Session.current_balance += values_difference
            else:
                Session.current_total_expenses += values_difference
                Session.current_balance -=  values_difference
            
            Session.current_balance = round(Session.current_balance, 2)
            Session.current_total_income = round(Session.current_total_income, 2)
            Session.current_total_expenses = round(Session.current_total_expenses, 2)

            category_data.item(row,2).setText(str(transaction_value))


def show_add_transaction_window(category_name:str):
    TransactionManagementWindow.button.setText(LANGUAGES[Session.language]["General management"][1])
    TransactionManagementWindow.message.setText(LANGUAGES[Session.language]["Windows"]["Main"]["Transactions"]["Messages"][1])

    TransactionManagementWindow.transaction_name.setText("")
    TransactionManagementWindow.transaction_name.setFocus()
    TransactionManagementWindow.transaction_day.setText("")
    TransactionManagementWindow.transaction_value.setText("")

    TransactionManagementWindow.window.setWindowTitle(category_name)
    TransactionManagementWindow.window.exec()


def add_transaction(transaction_name:str, transaction_day:int, transaction_value:int|float, category_data:CustomTableWidget, category_id:int):
    transaction = Session.db.transaction_query.add_transaction(category_id, Session.current_year, Session.current_month, transaction_day, transaction_value, transaction_name)

    if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
        Session.current_total_income = round(Session.current_total_income + transaction_value, 2)
        Session.current_balance = round(Session.current_balance + transaction_value, 2)
    else:
        Session.current_total_expenses = round(Session.current_total_expenses + transaction_value, 2)
        Session.current_balance = round(Session.current_balance - transaction_value, 2)

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
    TransactionManagementWindow.window.hide()


def transaction_data_handler():
    transaction_name = TransactionManagementWindow.transaction_name.text().strip()
    transaction_day = TransactionManagementWindow.transaction_day.text()
    transaction_value = TransactionManagementWindow.transaction_value.text()
    transaction_id = TransactionManagementWindow.transaction_id
    category_id = Session.db.category_query.get_category(TransactionManagementWindow.window.windowTitle(), CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]).id
    category_data = Session.categories[category_id].table_data

    max_month_day = MONTHS_DAYS[Session.current_month-1] + (Session.current_month == 2 and Session.current_year % 4 == 0)#Add one day to February (29) if year is leap

    if transaction_day == "" or transaction_value == "":
        return Messages.empty_fields.exec()
    
    if transaction_value.replace(".","").replace(",","").isdigit() and transaction_day.isdigit():
        transaction_day = int(transaction_day)
    else:
        return Messages.incorrect_data_type.exec()

    if not 0 < transaction_day <= max_month_day:
        Messages.day_out_range.setText(LANGUAGES[Session.language]["Messages"][8]+f"1-{max_month_day}")
        return Messages.day_out_range.exec()

    if transaction_value.find(","):#if transaction_value contains "," for example: 4,5 will be 4.5 
        transaction_value = float(".".join(transaction_value.split(",")))
    elif transaction_value.find("."):
        transaction_value = float(transaction_value)
    else:
        transaction_value = int(transaction_value)

    if TransactionManagementWindow.button.text() == LANGUAGES[Session.language]["General management"][5]: #Update 
        update_transaction(transaction_id, transaction_name, transaction_day, transaction_value, category_data)
        logger.debug(f"Transaction updated: {transaction_name} | {transaction_day} | {transaction_value} | Transaction id: {transaction_id} | Category id: {category_id}")
    else: #Add
        add_transaction(transaction_name, transaction_day, transaction_value, category_data, category_id)
        logger.debug(f"Transaction added: {transaction_name} | {transaction_day} | {transaction_value} | Category id: {category_id}")

    try:
        update_category_total_value
    except UnboundLocalError:
        from AppManagement.category import update_category_total_value
    update_category_total_value(category_id)
    
    update_account_balance()
    TransactionManagementWindow.window.hide()
        


def remove_transaction(category_data:CustomTableWidget, category_id:int):
    selected_row = category_data.selectedItems()

    if len(selected_row) == 0 or len(selected_row) < 3:
        return Messages.unselected_row.exec()
    
    if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
        transaction_id = int(category_data.item(selected_row[0].row(), 3).text())
    else:
        return Messages.only_one_row.exec()

    Messages.delete_transaction_confirmation.exec()
    if Messages.delete_transaction_confirmation.clickedButton() == Messages.delete_transaction_confirmation.ok_button:
        transaction_value = float(selected_row[2].text())
        Session.db.transaction_query.delete_transaction(transaction_id)

        category_data.removeRow(selected_row[0].row())

        try:
            update_category_total_value
        except UnboundLocalError:
            from AppManagement.category import update_category_total_value
        update_category_total_value(category_id)

        if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
            Session.current_total_income -= transaction_value
            Session.current_balance -= transaction_value
        else:
            Session.current_total_expenses -= transaction_value
            Session.current_balance += transaction_value
        
        Session.current_balance = round(Session.current_balance, 2)
        Session.current_total_income = round(Session.current_total_income, 2)
        Session.current_total_expenses = round(Session.current_total_expenses, 2)

        update_account_balance()

        columns = category_data.verticalHeader()
        columns.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)