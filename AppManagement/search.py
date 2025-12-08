from typing import cast
from datetime import date

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore



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

    app_core = AppCore.instance()
    transactions = app_core.db.search_query.search_transactions(
        name_substring=search_name,
        value=search_value,
        value_operand=search_value_operand,
        from_date=from_date,
        to_date=to_date,
        categories_id=categories_id
    )
    WindowsRegistry.SearchWindow.transactions_list.addItems(map(str, transactions))