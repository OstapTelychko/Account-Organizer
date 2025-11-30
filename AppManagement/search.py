from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore



def show_search_window() -> None:
    """Show search window."""


    categories = list(AppCore.instance().categories.values())
    WindowsRegistry.SearchWindow.categories_selection.add_categories_to_selection(categories)
    WindowsRegistry.SearchWindow.exec()