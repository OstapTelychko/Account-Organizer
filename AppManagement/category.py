from functools import partial

from AppObjects.session import Session
from GUI import QTableWidgetItem, Qt, QMessageBox, MainWindow, AddCategoryWindow, Errors, CategorySettingsWindow, RenameCategoryWindow, load_category, ALIGMENT
from project_configuration import CATEGORY_TYPE
from languages import LANGUAGES
from Statistics.copy_statistics import show_information_message
from AppManagement.balance import calculate_current_balance
from AppManagement.transaction import show_add_transaction_window, show_edit_transaction_window, remove_transaction




def load_categories_data():
    for category in Session.categories:
        category_data = Session.categories[category].table_data
        if category_data.rowCount() != 0:#Remove current category transactions if it exist
            for row in range(1,category_data.rowCount()+1):
                category_data.removeRow(row)
        category_data.setRowCount(0)

        transactions = Session.account.get_transactions_by_month(category, Session.current_year, Session.current_month)
        total_value = 0
        if len(transactions) != 0:
            category_data.setRowCount(len(transactions))
            for row,transaction in enumerate(transactions):
                name = QTableWidgetItem(transaction.name)
                name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                day = QTableWidgetItem()
                day.setTextAlignment(ALIGMENT.AlignCenter)
                day.setData(Qt.ItemDataRole.EditRole, transaction.day)
                day.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                value = QTableWidgetItem()
                value.setTextAlignment(ALIGMENT.AlignCenter)
                value.setData(Qt.ItemDataRole.EditRole, transaction.value)
                value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                transaction_id = QTableWidgetItem()
                transaction_id.setData(Qt.ItemDataRole.EditRole, transaction.id)

                category_data.setItem(row,0,name)
                category_data.setItem(row,1,day)
                category_data.setItem(row,2,value)
                category_data.setItem(row,3,transaction_id)
                total_value += transaction.value

        Session.categories[category].total_value_label.setText(LANGUAGES[Session.language]["Account"]["Info"][6]+str(float(round(total_value, 2))))


def create_category():
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = AddCategoryWindow.category_name.text().strip()

    if category_name == "":
        return Errors.no_category_name.exec()
    
    if Session.account.category_exists(category_name, category_type):
        return Errors.category_exists.exec()
    
    Session.account.create_category(category_name, category_type)
    category_id = Session.account.get_category_id(category_name, category_type) 
    Session.categories[category_id] = load_category(category_type, category_name, Session.account, category_id, Session.current_year, Session.current_month, Session.language, Session.theme)

    #Activate Category
    Session.categories[category_id].settings.clicked.connect(partial(show_category_settings, Session.categories[category_id].name))
    Session.categories[category_id].add_transaction.clicked.connect(partial(show_add_transaction_window, Session.categories[category_id].name))
    Session.categories[category_id].edit_transaction.clicked.connect(partial(show_edit_transaction_window, Session.categories[category_id].name, Session.categories[category_id].table_data))
    Session.categories[category_id].delete_transaction.clicked.connect(partial(remove_transaction, Session.categories[category_id].table_data, category_id))

    AddCategoryWindow.category_name.setText("")
    AddCategoryWindow.window.hide()
    show_information_message(LANGUAGES[Session.language]["Account"]["Category management"][8])


def load_categories():
    for category in Session.account.get_all_categories():
        Session.categories[category[0]] = load_category(category[1], category[2], Session.account, category[0], Session.current_year, Session.current_month, Session.language, Session.theme)


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

        Session.categories[category_id].window.deleteLater()
        Session.categories[category_id].settings.deleteLater()
        Session.categories[category_id].add_transaction.deleteLater()
        Session.categories[category_id].edit_transaction.deleteLater()
        Session.categories[category_id].delete_transaction.deleteLater()
        del Session.categories[category_id]

        calculate_current_balance()
        show_information_message(LANGUAGES[Session.language]["Account"]["Category management"][7])


def rename_category():
    new_category_name = RenameCategoryWindow.new_category_name.text().strip()
    current_name = RenameCategoryWindow.window.windowTitle()
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]

    if Session.account.category_exists(new_category_name, category_type):
        return Errors.category_exists.exec()

    for category in Session.categories:
        if Session.categories[category].name == current_name and Session.categories[category].type == category_type:
            Session.categories[category].name = new_category_name

            #Update connections
            Session.categories[category].settings.clicked.disconnect()
            Session.categories[category].add_transaction.clicked.disconnect()
            Session.categories[category].edit_transaction.clicked.disconnect()

            Session.categories[category].settings.clicked.connect(partial(show_category_settings, new_category_name))
            Session.categories[category].add_transaction.clicked.connect(partial(show_add_transaction_window, new_category_name))
            Session.categories[category].edit_transaction.clicked.connect(partial(show_edit_transaction_window, new_category_name, Session.categories[category].table_data))
            Session.categories[category].name_label.setText(new_category_name)

            Session.account.rename_category(category, new_category_name)
            RenameCategoryWindow.window.hide()
            CategorySettingsWindow.window.hide()
            RenameCategoryWindow.new_category_name.setText("")
            show_information_message(LANGUAGES[Session.language]["Account"]["Category management"][6])


def update_category_total_value(category_id:int):
    transactions = Session.account.get_transactions_by_month(category_id, Session.current_year, Session.current_month)
    total_value = 0

    if len(transactions) != 0:
        for transaction in transactions:
            total_value += transaction.value
    Session.categories[category_id].total_value_label.setText(LANGUAGES[Session.language]["Account"]["Info"][6]+str(round(total_value, 2)))


def activate_categories():
    for category in Session.categories:
        Session.categories[category].settings.clicked.connect(partial(show_category_settings, Session.categories[category].name))
        Session.categories[category].add_transaction.clicked.connect(partial(show_add_transaction_window, Session.categories[category].name))
        Session.categories[category].edit_transaction.clicked.connect(partial(show_edit_transaction_window, Session.categories[category].name, Session.categories[category].table_data))
        Session.categories[category].delete_transaction.clicked.connect(partial(remove_transaction, Session.categories[category].table_data, category))