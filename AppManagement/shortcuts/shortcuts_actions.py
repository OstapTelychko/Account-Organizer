from __future__ import annotations
from typing import cast

from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger

from DesktopQtToolkit.default_drop_shadow_effect import DefaultDropShadowEffect
from DesktopQtToolkit.horizontal_scroll_area import HorizontalScrollArea
from project_configuration import CategoryType


    


logger = get_logger(__name__)

def switch_tab(step:int) -> None:
    """Switch the main window to another tab of categories. Switching wraps around the first and last tabs.

        Arguments
        ---------
            `step` : (int) - Number of tabs to move by. `1` opens the next tab, `-1` the previous one.
    """

    tabs = WindowsRegistry.MainWindow.Incomes_and_expenses
    tabs.setCurrentIndex((tabs.currentIndex() + step) % tabs.count())


def move_category_focus(step:int) -> None:
    """Move focus between categories of the opened tab. Focus wraps around the ends of the list.

        Arguments
        ---------
            `step` : (int) - Number of categories to move by. `1` focuses the next category, `-1` the previous one.
    """

    app_core = AppCore.instance()
    category_type = CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    categories = [category for category in app_core.categories.values() if category.type == category_type]
    if len(categories) < 2:
        return

    focused_category = app_core.focused_categories.get(category_type)
    if focused_category is None:
        logger.error(f"Focused {category_type} category is None")
        raise ValueError(f"Focused {category_type} category is None")

    focused_category.table_data.setGraphicsEffect(cast(DefaultDropShadowEffect, None))
    focused_category = categories[(categories.index(focused_category) + step) % len(categories)]
    app_core.focused_categories[category_type] = focused_category
    focused_category.table_data.setGraphicsEffect(
        DefaultDropShadowEffect(focused_category.table_data, focused=True)
    )
    # Every tab of the main window is a scroll area with categories of one type
    cast(HorizontalScrollArea, WindowsRegistry.MainWindow.Incomes_and_expenses.currentWidget()).ensureWidgetVisible(
        focused_category.table_data, 300
    )


def add_transaction_to_focused_category() -> None:
    """
    Adds a transaction to the focused category.
    """

    focused_category = AppCore.instance().focused_categories.get(
        CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    )
    if focused_category is not None:
        focused_category.add_transaction.click()


def select_previous_transaction() -> None:
    """Selects the previous transaction in the focused category."""

    focused_category = AppCore.instance().focused_categories.get(
        CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    )
    if focused_category is None:
        return

    table = focused_category.table_data
    current_index = table.currentRow()
    if current_index > 0:
        table.selectRow(current_index - 1)
    elif current_index == 0 and table.rowCount() == 1:
        table.selectRow(0)


def select_next_transaction() -> None:
    """
    Selects the next transaction in the focused category.
    """

    focused_category = AppCore.instance().focused_categories.get(
        CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    )
    if focused_category is None:
        return

    table = focused_category.table_data
    current_index = table.currentRow()
    if current_index < table.rowCount() - 1:
        table.selectRow(current_index + 1)
    elif current_index == 0 and table.rowCount() == 1:
        table.selectRow(0)


def delete_transaction() -> None:
    """
    Deletes the selected transaction in the focused category.
    """

    focused_category = AppCore.instance().focused_categories.get(
        CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    )
    if focused_category is not None:
        focused_category.delete_transaction.click()


def edit_transaction() -> None:
    """
    Edits the selected transaction in the focused category.
    """

    focused_category = AppCore.instance().focused_categories.get(
        CategoryType.get(WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex())
    )
    if focused_category is not None:
        focused_category.edit_transaction.click()
