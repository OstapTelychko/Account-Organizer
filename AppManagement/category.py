from functools import partial

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import CATEGORY_TYPE
from languages import LanguageStructure
from GUI.category import load_category, add_category_to_position_list, load_transactions_into_category_table

from AppManagement.information_message import show_information_message
from AppManagement.balance import calculate_current_balance
from AppManagement.transaction import show_add_transaction_window, show_edit_transaction_window, remove_transaction



logger = get_logger(__name__)

def remove_categories_from_list() -> None:
    """Remove all categories from Session.categories. It's used in case you need to update or load all categories."""

    app_core = AppCore.instance()
    for category in app_core.categories.copy():
        app_core.categories[category].window.deleteLater()
        app_core.categories[category].settings.deleteLater()
        app_core.categories[category].add_transaction.deleteLater()
        app_core.categories[category].edit_transaction.deleteLater()
        app_core.categories[category].delete_transaction.deleteLater()
        del app_core.categories[category]


def load_categories_data() -> None:
    """Load all categories data from database. It loads all monthly transactions for each category """

    app_core = AppCore.instance()
    for category in app_core.categories:
        category_data = app_core.categories[category].table_data
        if category_data.rowCount() != 0:#Remove current category transactions if it exist
            for row in range(1,category_data.rowCount()+1):
                category_data.removeRow(row)
        category_data.setRowCount(0)

        transactions = app_core.db.transaction_query.get_transactions_by_month(
            category,
            app_core.current_year,
            app_core.current_month
        )
        if len(transactions) != 0:
            load_transactions_into_category_table(category_data, transactions)

        update_category_total_value(category)


def create_category() -> int:
    """
    Create category. It creates a new category in the database and in the GUI.
    It also checks if the category already exists and if the name is empty.
    """

    app_core = AppCore.instance()
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = WindowsRegistry.AddCategoryWindow.category_name.text().strip()

    if category_name == "":
        return WindowsRegistry.Messages.no_category_name.exec()
    
    if app_core.db.category_query.category_exists(category_name, category_type):
        return WindowsRegistry.Messages.category_exists.exec()
    
    position = app_core.db.category_query.get_available_position(category_type) 

    app_core.db.category_query.create_category(category_name, category_type, position)
    category = app_core.db.category_query.get_category(category_name, category_type)

    if category is None:
        logger.error(f"Category {category_name} haven't been created.")
        raise RuntimeError(f"Category {category_name} haven't been created.")
    
    category_id = category.id 
    app_core.categories[category_id] = load_category(
        category_type,
        category_name,
        app_core.db,
        category_id,
        position,
        app_core.current_year,
        app_core.current_month
    )

    #Activate Category
    app_core.categories[category_id].settings.clicked.connect(
        partial(show_category_settings, app_core.categories[category_id].name)
    )
    app_core.categories[category_id].add_transaction.clicked.connect(
        partial(show_add_transaction_window, app_core.categories[category_id].name)
    )
    app_core.categories[category_id].edit_transaction.clicked.connect(
        partial(
            show_edit_transaction_window,
            app_core.categories[category_id].name,
            app_core.categories[category_id].table_data
        )
    )
    app_core.categories[category_id].delete_transaction.clicked.connect(
        partial(remove_transaction, app_core.categories[category_id].table_data, category_id)
    )
    logger.debug(f"Category {category_name} created")

    WindowsRegistry.AddCategoryWindow.category_name.setText("")
    WindowsRegistry.AddCategoryWindow.hide()
    show_information_message(LanguageStructure.Categories.get_translation(8))
    reset_focused_category()

    return 1


def load_categories() -> None:
    """Load all categories from database for current account."""

    app_core = AppCore.instance()
    for category in app_core.db.category_query.get_all_categories():
        app_core.categories[category.id] = load_category(
            category.category_type,
            category.name,
            app_core.db,
            category.id,
            category.position,
            app_core.current_year,
            app_core.current_month
        )
        logger.debug(f"Category {category.name} loaded")
    reset_focused_category()
        

def show_category_settings(category_name:str) -> None:
    """Show category settings.

        Arguments
        ---------
        `category_name` : (str) Name of the category to show settings for.
    """
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
    if AppCore.instance().db.category_query.category_exists(category_name, category_type):
        WindowsRegistry.CategorySettingsWindow.setWindowTitle(category_name)
        WindowsRegistry.CategorySettingsWindow.exec()


def remove_category() -> None:
    """
    Remove category. It removes the category from the database and from the GUI.
    It also shows a confirmation message before removing the category.
    """

    app_core = AppCore.instance()
    category_name = WindowsRegistry.CategorySettingsWindow.windowTitle()

    WindowsRegistry.Messages.delete_category_confirmation.exec()
    if not WindowsRegistry.Messages.delete_category_confirmation.clickedButton() == WindowsRegistry.Messages.delete_category_confirmation.ok_button:
        return
    
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
    category = app_core.db.category_query.get_category(category_name, category_type)
    if category is None:
        logger.error(f"Category {category_name} not found. Category can't be removed.")
        raise RuntimeError(f"Category {category_name} not found. Category can't be removed.")
    
    category_id = category.id
    app_core.db.category_query.delete_category(category_id)
    WindowsRegistry.CategorySettingsWindow.setWindowTitle(" ")
    WindowsRegistry.CategorySettingsWindow.hide()

    app_core.categories[category_id].window.deleteLater()
    app_core.categories[category_id].settings.deleteLater()
    app_core.categories[category_id].add_transaction.deleteLater()
    app_core.categories[category_id].edit_transaction.deleteLater()
    app_core.categories[category_id].delete_transaction.deleteLater()
    del app_core.categories[category_id]
    logger.debug(f"Category {category_name} removed")

    for category_id in app_core.categories:
        category = app_core.db.category_query.get_category_by_id(category_id)
        app_core.categories[category_id].position = category.position

    calculate_current_balance()
    reset_focused_category()
    show_information_message(LanguageStructure.Categories.get_translation(7))


def show_rename_category_window() -> None:
    WindowsRegistry.RenameCategoryWindow.setWindowTitle(WindowsRegistry.CategorySettingsWindow.windowTitle())
    WindowsRegistry.RenameCategoryWindow.exec()


def rename_category() -> int:
    """
    Rename category. It renames the category in the database and in the GUI.
    It also checks if the category already exists and if the name is empty.
    """

    app_core = AppCore.instance()
    new_category_name = WindowsRegistry.RenameCategoryWindow.new_category_name.text().strip()
    current_name = WindowsRegistry.RenameCategoryWindow.windowTitle()
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]

    if app_core.db.category_query.category_exists(new_category_name, category_type):
        return WindowsRegistry.Messages.category_exists.exec()

    db_category = app_core.db.category_query.get_category(current_name, category_type)
    if db_category is None:
        logger.error(f"Category {current_name} not found. Category can't be renamed.")
        raise RuntimeError(f"Category {current_name} not found. Category can't be renamed.")
    
    category = app_core.categories[db_category.id]
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

    app_core.db.category_query.rename_category(category.id, new_category_name)
    WindowsRegistry.RenameCategoryWindow.hide()
    WindowsRegistry.CategorySettingsWindow.hide()
    WindowsRegistry.RenameCategoryWindow.new_category_name.setText("")
    show_information_message(LanguageStructure.Categories.get_translation(6))

    return 1


def show_change_category_position(category_name:str) -> None:
    """
    Show change category position window.
    It shows the current category position and all other categories in the same type.
    """

    app_core = AppCore.instance()
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
    selected_category = app_core.db.category_query.get_category(category_name, category_type)
    if selected_category is None:
        logger.error(f"Category {category_name} not found. Category position can't be changed.")
        raise RuntimeError(f"Category {category_name} not found. Category position can't be changed.")

    WindowsRegistry.ChangeCategoryPositionWindow.preview_category_name.setText(selected_category.name)
    WindowsRegistry.ChangeCategoryPositionWindow.setWindowTitle(selected_category.name)
    WindowsRegistry.ChangeCategoryPositionWindow.preview_category_position.setText(str(selected_category.position))

    #Remove previous categories
    while WindowsRegistry.ChangeCategoryPositionWindow.categories_list_layout.count():
        widget = WindowsRegistry.ChangeCategoryPositionWindow.categories_list_layout.takeAt(0).widget()
        if widget:
            widget.setParent(None) #type: ignore[call-overload] #Mypy doesn't know that None just means that the widget will be deleted
    

    for category_id, category in app_core.categories.items():
        if category_id != selected_category.id and category.type == selected_category.category_type:
            add_category_to_position_list(category)
    
    WindowsRegistry.ChangeCategoryPositionWindow.exec()


def change_category_position() -> int:
    """
    Change category position. It changes the category position in the database and in the GUI.
    It also checks if the new position is valid.
    """

    app_core = AppCore.instance()
    category_type = CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
    category_name = WindowsRegistry.ChangeCategoryPositionWindow.preview_category_name.text()
    category = app_core.db.category_query.get_category(category_name, category_type)

    if category is None:
        logger.error(f"Category {category_name} not found. Category position can't be changed.")
        raise RuntimeError(f"Category {category_name} not found. Category position can't be changed.")

    raw_new_position = WindowsRegistry.ChangeCategoryPositionWindow.new_position.text()
    old_position = category.position
    max_position = app_core.db.category_query.get_available_position(category_type)-1

    if raw_new_position == "":
        return WindowsRegistry.Messages.empty_fields.exec()

    if not raw_new_position.isdigit():
        return WindowsRegistry.Messages.incorrect_data_type.exec()
    new_position = int(raw_new_position)

    if not 0 <= new_position <= max_position:
        WindowsRegistry.Messages.position_out_range.setText(
            LanguageStructure.Messages.get_translation(17).replace("%max_position%", str(max_position))
        )
        return WindowsRegistry.Messages.position_out_range.exec()
    
    if new_position == old_position:
        return WindowsRegistry.Messages.same_position.exec()

    app_core.db.category_query.change_category_position(new_position, old_position, category.id, category_type)
    logger.debug(f"Category {category_name} position ({old_position}) changed to {new_position}")
    
    remove_categories_from_list()
    load_categories()
    activate_categories()
    WindowsRegistry.ChangeCategoryPositionWindow.hide()
    WindowsRegistry.CategorySettingsWindow.hide()

    return 1


def update_category_total_value(category_id:int) -> None:
    """Update category total value. It updates the total value label for the category in the GUI."""

    app_core = AppCore.instance()
    app_core.categories[category_id].total_value_label.setText(
        LanguageStructure.Categories.get_translation(10) +
        str(round(app_core.db.statistics_query.get_monthly_transactions_sum(
            category_id, app_core.current_year, app_core.current_month
        ), 2)))


def activate_categories() -> None:
    """Activate all categories. It connects all category buttons to their respective functions."""

    for category_id, category in AppCore.instance().categories.items():
        category.settings.clicked.connect(partial(show_category_settings, category.name))
        category.add_transaction.clicked.connect(partial(show_add_transaction_window, category.name))
        category.edit_transaction.clicked.connect(partial(show_edit_transaction_window, category.name, category.table_data))
        category.delete_transaction.clicked.connect(partial(remove_transaction, category.table_data, category_id))
        logger.debug(f"Category {category.name} activated")


def reset_focused_category() -> None:
    """Reset focused category. It sets the focused income and expense categories to the first category of their type."""

    app_core = AppCore.instance()
    income_categories = list([category for category in app_core.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in app_core.categories.values() if category.type == CATEGORY_TYPE[1]])

    if len(income_categories) != 0:
        app_core.focused_income_category = income_categories[0]
    else:
        app_core.focused_income_category = None
    
    if len(expense_categories) != 0:
        app_core.focused_expense_category = expense_categories[0]
    else:
        app_core.focused_expense_category = None