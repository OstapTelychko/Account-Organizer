from Session import Session
from GUI import QTableWidgetItem, Qt, QMessageBox, MainWindow, AddCategoryWindow, Errors, CategorySettingsWindow, RenameCategoryWindow, load_category
from project_configuration import CATEGORY_TYPE
from languages import LANGUAGES
from copy_statistics import show_information_message
from balance_management import calculate_current_balance
from transaction_management import show_add_transaction_window, show_edit_transaction_window, remove_transaction

from functools import partial



def load_categories_data():
    for category in Session.Categories:
        category_data = Session.Categories[category]["Category data"]
        if category_data.rowCount() != 0:#Remove current category transactions if it exist
            for row in range(1,category_data.rowCount()+1):
                category_data.removeRow(row)
        category_data.setRowCount(0)

        transactions = Session.account.get_transactions_by_month(category, Session.Current_year, Session.Current_month)
        total_value = 0
        if len(transactions) != 0:
            category_data.setRowCount(len(transactions))
            for row,transaction in enumerate(transactions):
                name = QTableWidgetItem(transaction[6])
                name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                day = QTableWidgetItem()
                day.setData(Qt.ItemDataRole.EditRole,transaction[4])
                day.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                value = QTableWidgetItem()
                value.setData(Qt.ItemDataRole.EditRole,transaction[5])
                value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                transaction_id = QTableWidgetItem()
                transaction_id.setData(Qt.ItemDataRole.EditRole,transaction[0])

                category_data.setItem(row,0,name)
                category_data.setItem(row,1,day)
                category_data.setItem(row,2,value)
                category_data.setItem(row,3,transaction_id)
                total_value += transaction[5]
        Session.Categories[category]["Total value"].setText(LANGUAGES[Session.Language]["Account"]["Info"][6]+str(round(total_value, 2)))


def create_category():
    category_type = "Incomes" if MainWindow.Incomes_and_expenses.currentIndex() == 0 else "Expenses"
    category_name = AddCategoryWindow.category_name.text().strip()

    if category_name != "":
        if not Session.account.category_exists(category_name, category_type):
            Session.account.create_category(category_name, category_type)
            category_id = Session.account.get_category_id(category_name, category_type) 
            Session.Categories[category_id] = load_category(category_type, category_name, Session.account, category_id, Session.Current_year, Session.Current_month, Session.Language, Session.Theme)

            #Activate Category
            Session.Categories[category_id]["Settings"].clicked.connect(partial(show_category_settings, Session.Categories[category_id]["Name"]))
            Session.Categories[category_id]["Add transaction"].clicked.connect(partial(show_add_transaction_window, Session.Categories[category_id]["Name"]))
            Session.Categories[category_id]["Edit transaction"].clicked.connect(partial(show_edit_transaction_window,Session.Categories[category_id]["Name"], Session.Categories[category_id]["Category data"]))
            Session.Categories[category_id]["Delete transaction"].clicked.connect(partial(remove_transaction, Session.Categories[category_id]["Category data"], category_id))

            AddCategoryWindow.category_name.setText("")
            AddCategoryWindow.window.hide()
            show_information_message(LANGUAGES[Session.Language]["Account"]["Category management"][8])
        else:
            Errors.category_exists_error.exec()
    else:
        Errors.no_category_name_error.exec()


def load_categories():
    for category in Session.account.get_all_categories():
        Session.Categories[category[0]] = load_category(category[1], category[2], Session.account, category[0], Session.Current_year, Session.Current_month, Session.Language, Session.Theme)


def show_category_settings(category_name:str):
    if Session.account.category_exists(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]):
        CategorySettingsWindow.window.setWindowTitle(category_name)
        CategorySettingsWindow.window.exec()


def remove_category():
    category_name = CategorySettingsWindow.window.windowTitle()

    if Errors.delete_category_question.exec() == QMessageBox.StandardButton.Ok:
        category_id = Session.account.get_category_id(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
        Session.account.delete_category(category_id)
        CategorySettingsWindow.window.setWindowTitle(" ")
        CategorySettingsWindow.window.hide()

        Session.Categories[category_id]["Category window"].deleteLater()
        Session.Categories[category_id]["Settings"].deleteLater()
        Session.Categories[category_id]["Add transaction"].deleteLater()
        Session.Categories[category_id]["Edit transaction"].deleteLater()
        Session.Categories[category_id]["Delete transaction"].deleteLater()
        del Session.Categories[category_id]

        calculate_current_balance()
        show_information_message(LANGUAGES[Session.Language]["Account"]["Category management"][7])


def rename_category():
    new_category_name = RenameCategoryWindow.new_category_name.text().strip()
    current_name = RenameCategoryWindow.window.windowTitle()
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]

    if not Session.account.category_exists(new_category_name, category_type):
        for category in Session.Categories:
            if Session.Categories[category]["Name"] == current_name and Session.Categories[category]["Type"] == category_type:
                Session.Categories[category].update({"Name":new_category_name})

                #Update connections
                Session.Categories[category]["Settings"].clicked.disconnect()
                Session.Categories[category]["Add transaction"].clicked.disconnect()
                Session.Categories[category]["Edit transaction"].clicked.disconnect()
                Session.Categories[category]["Settings"].clicked.connect(partial(show_category_settings, new_category_name))
                Session.Categories[category]["Add transaction"].clicked.connect(partial(show_add_transaction_window, new_category_name))
                Session.Categories[category]["Edit transaction"].clicked.connect(partial(show_edit_transaction_window, new_category_name, Session.Categories[category]["Category data"]))
                Session.Categories[category]["Name label"].setText(new_category_name)

                Session.account.rename_category(category, new_category_name)
                RenameCategoryWindow.window.hide()
                CategorySettingsWindow.window.hide()
                RenameCategoryWindow.new_category_name.setText("")
                show_information_message(LANGUAGES[Session.Language]["Account"]["Category management"][6])
    else:
        Errors.category_exists_error.exec()


def update_category_total_value(category_id:int):
    transactions = Session.account.get_transactions_by_month(category_id, Session.Current_year, Session.Current_month)
    total_value = 0

    if len(transactions) != 0:
        for transaction in transactions:
            total_value += transaction[5]
    Session.Categories[category_id]["Total value"].setText(LANGUAGES[Session.Language]["Account"]["Info"][6]+str(round(total_value, 2)))


def activate_categories():
    for category in Session.Categories:
        Session.Categories[category]["Settings"].clicked.connect(partial(show_category_settings, Session.Categories[category]["Name"]))
        Session.Categories[category]["Add transaction"].clicked.connect(partial(show_add_transaction_window, Session.Categories[category]["Name"]))
        Session.Categories[category]["Edit transaction"].clicked.connect(partial(show_edit_transaction_window, Session.Categories[category]["Name"], Session.Categories[category]["Category data"]))
        Session.Categories[category]["Delete transaction"].clicked.connect(partial(remove_transaction, Session.Categories[category]["Category data"], category))