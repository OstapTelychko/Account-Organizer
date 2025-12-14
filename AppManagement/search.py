from typing import cast
from datetime import date

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger

from languages import LanguageStructure
from project_configuration import CATEGORY_TYPE


logger = get_logger(__name__)

def show_search_window() -> None:
    """Show search window."""

    categories = list(AppCore.instance().categories.values())
    WindowsRegistry.SearchWindow.categories_selection.add_categories_to_selection(categories)
    WindowsRegistry.SearchWindow.categories_selection.add_all_incomes_categories.click()
    WindowsRegistry.SearchWindow.categories_selection.add_all_expenses_categories.click()
    WindowsRegistry.SearchWindow.exec()


def perform_search() -> None | int:
    """Perform search based on search window parameters."""

    search_name = WindowsRegistry.SearchWindow.search_name.text()
    search_value_text = WindowsRegistry.SearchWindow.search_value.text()
    search_value = float(search_value_text) if search_value_text else None
    search_value_operand = WindowsRegistry.SearchWindow.value_operands.currentText()

    from_date = cast(date, WindowsRegistry.SearchWindow.date_selection.search_from_date.date().toPython())
    to_date = cast(date, WindowsRegistry.SearchWindow.date_selection.search_to_date.date().toPython())

    categories_id = list(WindowsRegistry.SearchWindow.categories_selection.selected_categories_data.keys())

    if (to_date - from_date).days <= 0:
        return WindowsRegistry.Messages.wrong_date.exec()
    
    if not any([search_name, search_value]):
        return WindowsRegistry.Messages.empty_search_fields.exec()
    
    WindowsRegistry.SearchWindow.categories_selection.setHidden(True)
    WindowsRegistry.SearchWindow.transactions_list.setHidden(False)
    WindowsRegistry.SearchWindow.transactions_list.clear()
    
    logger.debug(
        f"Performing search with name: {search_name}, value: {search_value} operand: {search_value_operand},"
        f" from_date: {from_date}, to_date: {to_date}, categories_id: {categories_id}"
    )
    app_core = AppCore.instance()
    transactions = app_core.db.search_query.search_transactions(
        name_substring=search_name,
        value=search_value,
        value_operand=search_value_operand,
        from_date=from_date,
        to_date=to_date,
        categories_id=categories_id
    )
    logger.debug(f"Found {len(transactions)} transactions matching search criteria")

    for transaction in transactions:
        transaction_name = transaction.name
        if transaction_name == "":
            transaction_name = LanguageStructure.Statistics.get_translation(12)
        
        category = app_core.categories[transaction.category_id]
        category_name = category.name
        if category.type == CATEGORY_TYPE[0]:
            transaction_color = "rgb(0,205,0)"
        else:
            transaction_color = "rgb(205,0,0)"

        WindowsRegistry.SearchWindow.transactions_list.addItem(
            f"<b style='color:{transaction_color}'>{transaction_name}</b> ({category_name}) <br>"
            f"Date: <b>{transaction.date}</b>  Value: <b>{transaction.value}</b>"
        )
    return None