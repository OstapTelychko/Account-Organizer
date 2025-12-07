from typing import cast
from datetime import date

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore



def show_search_window() -> None:
    """Show search window."""

    categories = list(AppCore.instance().categories.values())
    WindowsRegistry.SearchWindow.categories_selection.add_categories_to_selection(categories)
    WindowsRegistry.SearchWindow.exec()


def perform_search() -> None | int:
    """Perform search based on search window parameters."""

    search_name = WindowsRegistry.SearchWindow.search_name.text()
    search_value = WindowsRegistry.SearchWindow.search_value.text()

    from_date = cast(date, WindowsRegistry.SearchWindow.date_selection.search_from_date.date().toPython())
    to_date = cast(date, WindowsRegistry.SearchWindow.date_selection.search_to_date.date().toPython())

    if (to_date - from_date).days <= 0:
        return WindowsRegistry.Messages.wrong_date.exec()
    
    if not any([search_name, search_value]):
        return WindowsRegistry.Messages.empty_search_fields.exec()
    
    WindowsRegistry.SearchWindow.categories_selection.setHidden(True)
    WindowsRegistry.SearchWindow.transactions_list.setHidden(False)

    app_core = AppCore.instance()