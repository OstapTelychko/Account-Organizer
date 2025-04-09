from functools import partial
from PySide6.QtCore import Qt

from AppObjects.session import Session
from AppObjects.logger import get_logger
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



logger = get_logger(__name__)

def remove_categories_from_list():
    """Remove all categories from Session.categories. It's used in case you need to update or load all categories."""

    for category in Session.categories.copy():
        Session.categories[category].window.deleteLater()
        Session.categories[category].settings.deleteLater()
        Session.categories[category].add_transaction.deleteLater()
        Session.categories[category].edit_transaction.deleteLater()
        Session.categories[category].delete_transaction.deleteLater()
        del Session.categories[category]


def load_categories_data():
    """Load all categories data from database. It loads all monthly transactions for each category """

    for category in Session.categories:
        category_data = Session.categories[category].table_data
        if category_data.rowCount() != 0:#Remove current category transactions if it exist
            for row in range(1,category_data.rowCount()+1):
                category_data.removeRow(row)
        category_data.setRowCount(0)

        transactions = Session.db.transaction_query.get_transactions_by_month(category, Session.current_year, Session.current_month)
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

        update_category_total_value(category)


def create_category():
    """Create category. It creates a new category in the database and in the GUI. It also checks if the category already exists and if the name is empty."""

    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = AddCategoryWindow.category_name.text().strip()

    if category_name == "":
        return Messages.no_category_name.exec()
    
    if Session.db.category_query.category_exists(category_name, category_type):
        return Messages.category_exists.exec()
    
    position = Session.db.category_query.get_available_position(category_type) 

    Session.db.category_query.create_category(category_name, category_type, position)
    category_id = Session.db.category_query.get_category(category_name, category_type).id 
    Session.categories[category_id] = load_category(category_type, category_name, Session.db, category_id, position, Session.current_year, Session.current_month, Session.language)

    #Activate Category
    Session.categories[category_id].settings.clicked.connect(partial(show_category_settings, Session.categories[category_id].name))
    Session.categories[category_id].add_transaction.clicked.connect(partial(show_add_transaction_window, Session.categories[category_id].name))
    Session.categories[category_id].edit_transaction.clicked.connect(partial(show_edit_transaction_window, Session.categories[category_id].name, Session.categories[category_id].table_data))
    Session.categories[category_id].delete_transaction.clicked.connect(partial(remove_transaction, Session.categories[category_id].table_data, category_id))
    logger.debug(f"Category {category_name} created")

    AddCategoryWindow.category_name.setText("")
    AddCategoryWindow.window.hide()
    show_information_message(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][8])
    reset_focused_category()


def load_categories():
    """Load all categories from database for current account."""

    for category in Session.db.category_query.get_all_categories():
        Session.categories[category.id] = load_category(category.category_type, category.name, Session.db, category.id, category.position, Session.current_year, Session.current_month, Session.language)
        logger.debug(f"Category {category.name} loaded")
    reset_focused_category()
        

def show_category_settings(category_name:str):
    """Show category settings.

        Arguments
        ---------
        `category_name` : (str) Name of the category to show settings for.
    """

    if Session.db.category_query.category_exists(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]):
        CategorySettingsWindow.window.setWindowTitle(category_name)
        CategorySettingsWindow.window.exec()


def remove_category():
    """Remove category. It removes the category from the database and from the GUI. It also shows a confirmation message before removing the category."""

    category_name = CategorySettingsWindow.window.windowTitle()

    Messages.delete_category_confirmation.exec()
    if Messages.delete_category_confirmation.clickedButton() == Messages.delete_category_confirmation.ok_button:
        category_id = Session.db.category_query.get_category(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]).id
        Session.db.category_query.delete_category(category_id)
        CategorySettingsWindow.window.setWindowTitle(" ")
        CategorySettingsWindow.window.hide()

        Session.categories[category_id].window.deleteLater()
        Session.categories[category_id].settings.deleteLater()
        Session.categories[category_id].add_transaction.deleteLater()
        Session.categories[category_id].edit_transaction.deleteLater()
        Session.categories[category_id].delete_transaction.deleteLater()
        del Session.categories[category_id]
        logger.debug(f"Category {category_name} removed")

        calculate_current_balance()
        reset_focused_category()
        show_information_message(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][7])


def rename_category():
    """Rename category. It renames the category in the database and in the GUI. It also checks if the category already exists and if the name is empty."""

    new_category_name = RenameCategoryWindow.new_category_name.text().strip()
    current_name = RenameCategoryWindow.window.windowTitle()
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]

    if Session.db.category_query.category_exists(new_category_name, category_type):
        return Messages.category_exists.exec()

    category = Session.categories[Session.db.category_query.get_category(current_name, category_type).id]
    category.name = new_category_name

    #Update connections
    category.settings.clicked.disconnect()
    category.add_transaction.clicked.disconnect()
    category.edit_transaction.clicked.disconnect()

    category.settings.clicked.connect(partial(show_category_settings, new_category_name))
    category.add_transaction.clicked.connect(partial(show_add_transaction_window, new_category_name))
    category.edit_transaction.clicked.connect(partial(show_edit_transaction_window, new_category_name, category.table_data))
    category.name_label.setText(new_category_name)
    logger.debug(f"Category {current_name} renamed to {new_category_name}")

    Session.db.category_query.rename_category(category.id, new_category_name)
    RenameCategoryWindow.window.hide()
    CategorySettingsWindow.window.hide()
    RenameCategoryWindow.new_category_name.setText("")
    show_information_message(LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][6])


def show_change_category_position(category_name:str):
    """Show change category position window. It shows the current category position and all other categories in the same type."""

    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    selected_category = Session.db.category_query.get_category(category_name, category_type)

    ChangeCategoryPositionWindow.preview_category_name.setText(selected_category.name)
    ChangeCategoryPositionWindow.window.setWindowTitle(selected_category.name)
    ChangeCategoryPositionWindow.preview_category_position.setText(str(selected_category.position))

    #Remove previous categories
    while ChangeCategoryPositionWindow.categories_list_layout.count():
        widget = ChangeCategoryPositionWindow.categories_list_layout.takeAt(0).widget()
        if widget:
            widget.setParent(None)
    

    for category in Session.db.category_query.get_all_categories():
        if category is not selected_category and category.category_type == selected_category.category_type:
            add_category_to_position_list(category)
    
    ChangeCategoryPositionWindow.window.exec()


def change_category_position():
    """Change category position. It changes the category position in the database and in the GUI. It also checks if the new position is valid"""

    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = ChangeCategoryPositionWindow.preview_category_name.text()
    category = Session.db.category_query.get_category(category_name, category_type)

    new_position = ChangeCategoryPositionWindow.new_position.text()
    old_position = category.position
    max_position = Session.db.category_query.get_available_position(category_type)-1

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

    Session.db.category_query.change_category_position(new_position, old_position, category.id, category_type)
    logger.debug(f"Category {category_name} position ({old_position}) changed to {new_position}")
    
    remove_categories_from_list()
    load_categories()
    activate_categories()
    ChangeCategoryPositionWindow.window.hide()
    CategorySettingsWindow.window.hide()


def update_category_total_value(category_id:int):
    """Update category total value. It updates the total value label for the category in the GUI."""

    Session.categories[category_id].total_value_label.setText(
        LANGUAGES[Session.language]["Windows"]["Main"]["Categories"][10] +
        str(round(Session.db.statistics_query.get_monthly_transactions_sum(category_id, Session.current_year, Session.current_month), 2)))


def activate_categories():
    """Activate all categories. It connects all category buttons to their respective functions."""

    for category_id, category in Session.categories.items():
        category.settings.clicked.connect(partial(show_category_settings, category.name))
        category.add_transaction.clicked.connect(partial(show_add_transaction_window, category.name))
        category.edit_transaction.clicked.connect(partial(show_edit_transaction_window, category.name, category.table_data))
        category.delete_transaction.clicked.connect(partial(remove_transaction, category.table_data, category_id))
        logger.debug(f"Category {category.name} activated")


def reset_focused_category():
    """Reset focused category. It sets the focused income and expense categories to the first category of their type."""

    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if len(income_categories) != 0:
        Session.focused_income_category = income_categories[0]
    else:
        Session.focused_income_category = None
    
    if len(expense_categories) != 0:
        Session.focused_expense_category = expense_categories[0]
    else:
        Session.focused_expense_category = None