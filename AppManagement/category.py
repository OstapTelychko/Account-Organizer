from functools import partial
from PySide6.QtCore import Qt

from AppObjects.session import Session
from project_configuration import CATEGORY_TYPE
from languages import LANGUAGES

from GUI.gui_constants import ALIGNMENT
from GUI.windows.main_window import MainWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, RenameCategoryWindow, ChangeCategoryPositionWindow
from GUI.windows.messages import Messages
from GUI.category import load_category, add_category_to_position_list

from Statistics.copy_statistics import show_information_message
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
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
                name = CustomTableWidgetItem(transaction.name)
                name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                day = CustomTableWidgetItem(str(transaction.day))
                day.setTextAlignment(ALIGNMENT.AlignCenter)
                day.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                value = CustomTableWidgetItem(str(transaction.value))
                value.setTextAlignment(ALIGNMENT.AlignCenter)
                value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                transaction_id = CustomTableWidgetItem(str(transaction.id))

                category_data.setItem(row,0,name)
                category_data.setItem(row,1,day)
                category_data.setItem(row,2,value)
                category_data.setItem(row,3,transaction_id)
                total_value += transaction.value

        Session.categories[category].total_value_label.setText(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][10]+str(float(round(total_value, 2))))


def create_category():
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = AddCategoryWindow.category_name.text().strip()

    if category_name == "":
        return Messages.no_category_name.exec()
    
    if Session.db.category_exists(category_name, category_type):
        return Messages.category_exists.exec()
    
    position = Session.db.get_available_position(category_type) 

    Session.db.create_category(category_name, category_type, position)
    category_id = Session.db.get_category(category_name, category_type).id 
    Session.categories[category_id] = load_category(category_type, category_name, Session.db, category_id, position, Session.current_year, Session.current_month, Session.language)

    #Activate Category
    Session.categories[category_id].settings.clicked.connect(partial(show_category_settings, Session.categories[category_id].name))
    Session.categories[category_id].add_transaction.clicked.connect(partial(show_add_transaction_window, Session.categories[category_id].name))
    Session.categories[category_id].edit_transaction.clicked.connect(partial(show_edit_transaction_window, Session.categories[category_id].name, Session.categories[category_id].table_data))
    Session.categories[category_id].delete_transaction.clicked.connect(partial(remove_transaction, Session.categories[category_id].table_data, category_id))

    AddCategoryWindow.category_name.setText("")
    AddCategoryWindow.window.hide()
    show_information_message(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][8])


def load_categories():
    for category in Session.db.get_all_categories():
        Session.categories[category.id] = load_category(category.category_type, category.name, Session.db, category.id, category.position, Session.current_year, Session.current_month, Session.language)


def show_category_settings(category_name:str):
    if Session.db.category_exists(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]):
        CategorySettingsWindow.window.setWindowTitle(category_name)
        CategorySettingsWindow.window.exec()


def remove_category():
    category_name = CategorySettingsWindow.window.windowTitle()

    Messages.delete_category_confirmation.exec()
    if Messages.delete_category_confirmation.clickedButton() == Messages.delete_category_confirmation.ok_button:
        category_id = Session.db.get_category(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]).id
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
        show_information_message(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][7])


def rename_category():
    new_category_name = RenameCategoryWindow.new_category_name.text().strip()
    current_name = RenameCategoryWindow.window.windowTitle()
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]

    if Session.db.category_exists(new_category_name, category_type):
        return Messages.category_exists.exec()

    category = Session.categories[Session.db.get_category(current_name, category_type).id]

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
    show_information_message(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][6])


def show_change_category_position(category_name:str):
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    selected_category = Session.db.get_category(category_name, category_type)

    ChangeCategoryPositionWindow.preview_category_name.setText(selected_category.name)
    ChangeCategoryPositionWindow.window.setWindowTitle(selected_category.name)
    ChangeCategoryPositionWindow.preview_category_position.setText(str(selected_category.position))

    #Remove previous categories
    while ChangeCategoryPositionWindow.categories_list_layout.count():
        widget = ChangeCategoryPositionWindow.categories_list_layout.takeAt(0).widget()
        if widget:
            widget.setParent(None)
    

    for category in Session.db.get_all_categories():
        if category is not selected_category and category.category_type == selected_category.category_type:
            add_category_to_position_list(category)
    
    ChangeCategoryPositionWindow.window.exec()


def change_category_position():
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = ChangeCategoryPositionWindow.preview_category_name.text()
    category = Session.db.get_category(category_name, category_type)

    new_position = ChangeCategoryPositionWindow.new_position.text()
    old_position = category.position
    max_position = Session.db.get_available_position(category_type)-1

    if new_position == "":
        return Messages.empty_fields.exec()

    if not new_position.isdigit():
        return Messages.incorrect_data_type.exec()
    new_position = int(new_position)

    if not 0 <= new_position <= max_position:
        Messages.position_out_range.setText(LANGUAGES[Session.language]["Messages"][17].replace("max_position", str(max_position)))
        return Messages.position_out_range.exec()
    
    if new_position == old_position:
        return Messages.same_position.exec()

    Session.db.change_category_position(new_position, old_position, category.id, category_type)
    
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
    Session.categories[category_id].total_value_label.setText(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][10]+str(round(total_value, 2)))


def activate_categories():
    for category in Session.categories:
        Session.categories[category].settings.clicked.connect(partial(show_category_settings, Session.categories[category].name))
        Session.categories[category].add_transaction.clicked.connect(partial(show_add_transaction_window, Session.categories[category].name))
        Session.categories[category].edit_transaction.clicked.connect(partial(show_edit_transaction_window, Session.categories[category].name, Session.categories[category].table_data))
        Session.categories[category].delete_transaction.clicked.connect(partial(remove_transaction, Session.categories[category].table_data, category))