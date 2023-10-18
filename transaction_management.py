from Session import Session
from GUI import QTableWidget, QTableWidgetItem, Qt, QMessageBox, QHeaderView, TransactionManagementWindow, Errors, MainWindow
from languages import LANGUAGES
from project_configuration import MONTHS_DAYS, CATEGORY_TYPE
from balance_management import update_account_balance




def show_edit_transaction_window(category_name:str, category_data:QTableWidget):
    selected_row = category_data.selectedItems()

    if len(selected_row) != 0 and not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
            TransactionManagementWindow.button.setText(LANGUAGES[Session.Language]["General management"][5])
            TransactionManagementWindow.message.setText(LANGUAGES[Session.Language]["Account"]["Transactions management"]["Messages"][0])
            TransactionManagementWindow.window.setWindowTitle(category_name)
            TransactionManagementWindow.transaction_name.setText(selected_row[0].text())
            TransactionManagementWindow.transaction_day.setText(selected_row[1].text())
            TransactionManagementWindow.transaction_value.setText(selected_row[2].text())
            TransactionManagementWindow.transaction_id = int(category_data.item(selected_row[0].row(), 3).text())
            TransactionManagementWindow.window.exec()
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def update_transaction(transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int|float, category_data:QTableWidget):
    Session.account.update_transaction(transaction_id, transaction_name, transaction_day, transaction_value)
                
    for row in range(category_data.rowCount()):
        if int(category_data.item(row,3).text()) == transaction_id:
            category_data.item(row,0).setText(transaction_name)
            category_data.item(row,1).setData(Qt.ItemDataRole.EditRole, transaction_day)

            old_value = category_data.item(row,2).data(Qt.ItemDataRole.EditRole)
            values_difference = transaction_value - old_value

            if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
                Session.Current_total_income += values_difference
                Session.Current_balance += values_difference
            else:
                Session.Current_total_expenses += values_difference
                Session.Current_balance -=  values_difference
            category_data.item(row,2).setData(Qt.ItemDataRole.EditRole, transaction_value)


def show_add_transaction_window(category_name:str):
    TransactionManagementWindow.button.setText(LANGUAGES[Session.Language]["General management"][1])
    TransactionManagementWindow.message.setText(LANGUAGES[Session.Language]["Account"]["Transactions management"]["Messages"][1])
    TransactionManagementWindow.transaction_name.setText("")
    TransactionManagementWindow.transaction_day.setText("")
    TransactionManagementWindow.transaction_value.setText("")

    TransactionManagementWindow.window.setWindowTitle(category_name)
    TransactionManagementWindow.window.exec()


def add_transaction(transaction_name:str, transaction_day:int, transaction_value:int|float, category_data:QTableWidget, category_id:int):
    Session.account.add_transaction(category_id, Session.Current_year, Session.Current_month, transaction_day, transaction_value, transaction_name)

    if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
        Session.Current_total_income += transaction_value
        Session.Current_balance += transaction_value
    else:
        Session.Current_total_expenses += transaction_value
        Session.Current_balance -= transaction_value

    row = category_data.rowCount()
    category_data.setRowCount(row+1)

    day = QTableWidgetItem()
    day.setData(Qt.ItemDataRole.EditRole, transaction_day)
    day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes in this case cells in table can't be edited

    value = QTableWidgetItem()
    value.setData(Qt.ItemDataRole.EditRole, transaction_value)
    value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    transaction_id = QTableWidgetItem()
    transaction_id.setData(Qt.ItemDataRole.EditRole, Session.account.get_last_transaction_id())
    transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    name = QTableWidgetItem(transaction_name)
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
    category_id = Session.account.get_category_id(TransactionManagementWindow.window.windowTitle(), CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
    category_data = Session.Categories[category_id]["Category data"]

    if  transaction_day != "" or transaction_value != "":
        if transaction_value.replace(".","").isdigit() or transaction_value.replace(",","").isdigit() and transaction_day.isdigit():
            transaction_day = int(transaction_day)
            max_month_day = MONTHS_DAYS[Session.Current_month-1] + (Session.Current_month == 2 and Session.Current_year % 4 == 0)#Add one day to February (29) if year is leap

            if 0 < transaction_day <= max_month_day:

                if transaction_value.find(","):#if transaction_value contains "," for example: 4,5 will be 4.5 
                    transaction_value = float(".".join(transaction_value.split(",")))
                elif transaction_value.find("."):
                    transaction_value = float(transaction_value)
                else:
                    transaction_value = int(transaction_value)

                if TransactionManagementWindow.button.text() == LANGUAGES[Session.Language]["General management"][5]: #Update 
                    update_transaction(transaction_id, transaction_name, transaction_day, transaction_value, category_data)
                else: #Add
                    add_transaction(transaction_name, transaction_day, transaction_value, category_data, category_id)

                try:
                    update_category_total_value
                except UnboundLocalError:
                    from category_management import update_category_total_value
                update_category_total_value(category_id)
                
                update_account_balance()
                TransactionManagementWindow.window.hide()
            else:
                Errors.day_out_range_error.setText(LANGUAGES[Session.Language]["Errors"][8]+f"1-{max_month_day}")
                Errors.day_out_range_error.exec()
        else:
            Errors.incorrect_data_type_error.exec()
    else:
        Errors.empty_fields_error.exec()


def remove_transaction(category_data:QTableWidget, category_id:int):
    selected_row = category_data.selectedItems()

    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row()  and selected_row[0].row() == selected_row[2].row():
            transaction_id = category_data.item(selected_row[0].row(), 3).data(Qt.ItemDataRole.EditRole)

            if Errors.delete_transaction_question.exec() == QMessageBox.StandardButton.Ok:

                transaction_value = selected_row[2].data(Qt.ItemDataRole.EditRole)
                Session.account.delete_transaction(transaction_id)

                for row in range(category_data.rowCount()):
                    if category_data.item(row, 3).data(Qt.ItemDataRole.EditRole) == transaction_id:
                        category_data.removeRow(row)
                        break

                try:
                    update_category_total_value
                except UnboundLocalError:
                    from category_management import update_category_total_value
                update_category_total_value(category_id)

                if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
                    Session.Current_total_income -= transaction_value
                    Session.Current_balance -= transaction_value
                else:
                    Session.Current_total_expenses -= transaction_value
                    Session.Current_balance += transaction_value
                update_account_balance()

                row = category_data.verticalHeader()
                row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()