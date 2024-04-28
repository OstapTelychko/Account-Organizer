from functools import partial
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt

from AppObjects.session import Session
from project_configuration import CATEGORY_TYPE
from languages import LANGUAGES

from GUI.windows.main import ALIGMENT, MainWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, RenameCategoryWindow, ChangeCategoryPositionWindow
from GUI.windows.errors import Errors
from GUI.category import load_category, add_category_to_position_list

from Statistics.copy_statistics import show_information_message
from AppManagement.balance import calculate_current_balance
from AppManagement.transaction import show_add_transaction_window, show_edit_transaction_window, remove_transaction


def remove_categories_from_list():
    for category in Session.categories.copy():
        Session.categories[category].window.deleteLater()
        Session.categories[category].settings.deleteLater()
        Session.categories[category].add_transaction.deleteLater()
        Session.categories[category].edit_transaction.deleteLater()
        Session.categories[category].delete_transaction.deleteLater()
        del Session.categories[category]



def load_categories_data():
    for category in Session.categories:
        category_data = Session.categories[category].table_data
        if category_data.rowCount() != 0:#Remove current category transactions if it exist
            for row in range(1,category_data.rowCount()+1):
                category_data.removeRow(row)
        category_data.setRowCount(0)

        transactions = Session.db.get_transactions_by_month(category, Session.current_year, Session.current_month)
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
    
    if Session.db.category_exists(category_name, category_type):
        return Errors.category_exists.exec()
    
    position = Session.db.get_last_category_position(category_type) + 1

    Session.db.create_category(category_name, category_type, position)
    category_id = Session.db.get_category_id(category_name, category_type) 
    Session.categories[category_id] = load_category(category_type, category_name, Session.db, category_id, position, Session.current_year, Session.current_month, Session.language)

    #Activate Category
    Session.categories[category_id].settings.clicked.connect(partial(show_category_settings, Session.categories[category_id].name))
    Session.categories[category_id].add_transaction.clicked.connect(partial(show_add_transaction_window, Session.categories[category_id].name))
    Session.categories[category_id].edit_transaction.clicked.connect(partial(show_edit_transaction_window, Session.categories[category_id].name, Session.categories[category_id].table_data))
    Session.categories[category_id].delete_transaction.clicked.connect(partial(remove_transaction, Session.categories[category_id].table_data, category_id))

    AddCategoryWindow.category_name.setText("")
    AddCategoryWindow.window.hide()
    show_information_message(LANGUAGES[Session.language]["Account"]["Category management"][8])


def load_categories():
    for category in Session.db.get_all_categories():
        Session.categories[category.id] = load_category(category.category_type, category.name, Session.db, category.id, category.position, Session.current_year, Session.current_month, Session.language)


def show_category_settings(category_name:str):
    if Session.db.category_exists(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]):
        CategorySettingsWindow.window.setWindowTitle(category_name)
        CategorySettingsWindow.window.exec()


def remove_category():
    category_name = CategorySettingsWindow.window.windowTitle()

    if Errors.delete_category_question.exec() == QMessageBox.StandardButton.Ok:
        category_id = Session.db.get_category_id(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
        Session.db.delete_category(category_id)
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

    if Session.db.category_exists(new_category_name, category_type):
        return Errors.category_exists.exec()

    category = Session.categories[Session.db.get_category_id(current_name, category_type)]

    category.name = new_category_name

    #Update connections
    category.settings.clicked.disconnect()
    category.add_transaction.clicked.disconnect()
    category.edit_transaction.clicked.disconnect()

    category.settings.clicked.connect(partial(show_category_settings, new_category_name))
    category.add_transaction.clicked.connect(partial(show_add_transaction_window, new_category_name))
    category.edit_transaction.clicked.connect(partial(show_edit_transaction_window, new_category_name, category.table_data))
    category.name_label.setText(new_category_name)

    Session.db.rename_category(category.id, new_category_name)
    RenameCategoryWindow.window.hide()
    CategorySettingsWindow.window.hide()
    RenameCategoryWindow.new_category_name.setText("")
    show_information_message(LANGUAGES[Session.language]["Account"]["Category management"][6])


def show_change_category_position(category_name:str):
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category = Session.categories[Session.db.get_category_id(category_name, category_type)]

    ChangeCategoryPositionWindow.preview_category_name.setText(category.name)
    ChangeCategoryPositionWindow.window.setWindowTitle(category.name)
    ChangeCategoryPositionWindow.preview_category_position.setText(str(category.position))

    #Remove previous categories
    while ChangeCategoryPositionWindow.categories_list_layout.count():
        widget = ChangeCategoryPositionWindow.categories_list_layout.takeAt(0).widget()
        if widget:
            widget.setParent(None)
    

    for category_object in Session.categories.values():
        if category_object is not category and category_object.type == category.type:
            add_category_to_position_list(category_object)
    
    ChangeCategoryPositionWindow.window.exec()


def change_category_position():
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = ChangeCategoryPositionWindow.preview_category_name.text()
    category = Session.categories[Session.db.get_category_id(category_name, category_type)]

    categories = [category for category in Session.categories.values() if category.type == category_type]
    categories.sort(key=lambda item:item.position)

    new_position = ChangeCategoryPositionWindow.new_position.text()
    old_position = category.position

    if new_position == "":
        return Errors.empty_fields.exec()

    if not new_position.isdigit():
        return Errors.incorrect_data_type.exec()
    new_position = int(new_position)

    if not 0 <= new_position < categories[-1].position:
        Errors.position_out_range.setText(LANGUAGES[Session.language]["Errors"][17].replace("max_position", str(categories[-1].position)))
        return Errors.position_out_range.exec()
    
    if new_position == old_position:
        return Errors.same_position.exec()


    if new_position < old_position:

        for category_object in categories:
            if new_position <= category_object.position < old_position:
                category_object.position += 1
                Session.db.change_category_position(category_object.position, category_object.id)

    else:

        for category_object in categories:
            if new_position >= category_object.position > old_position:
                category_object.position -= 1
                Session.db.change_category_position(category_object.position, category_object.id)

    category.position = new_position
    Session.db.change_category_position(new_position, category.id)
    
    remove_categories_from_list()
    load_categories()
    activate_categories()
    ChangeCategoryPositionWindow.window.hide()
    CategorySettingsWindow.window.hide()


def update_category_total_value(category_id:int):
    transactions = Session.db.get_transactions_by_month(category_id, Session.current_year, Session.current_month)
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