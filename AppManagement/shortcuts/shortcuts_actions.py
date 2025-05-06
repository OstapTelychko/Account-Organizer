from __future__ import annotations
from typing import cast
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from AppObjects.session import Session
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger

from project_configuration import CATEGORY_TYPE
from GUI.gui_constants import FOCUSED_SHADOW_EFFECT_ARGUMENTS


    


logger = get_logger(__name__)

def move_to_next_category() -> None:
    """Move focus to the next category in the list of categories."""

    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if len(income_categories) > 1:
            if Session.focused_income_category is None:
                logger.error("Focused income category is None")
                raise ValueError("Focused income category is None")

            current_index = income_categories.index(Session.focused_income_category)
            next_index = (current_index + 1) % len(income_categories)

            Session.focused_income_category.table_data.setGraphicsEffect(cast(QGraphicsDropShadowEffect, None))
            Session.focused_income_category = income_categories[next_index]
            Session.focused_income_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_income_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Incomes_scroll.ensureWidgetVisible(Session.focused_income_category.table_data, 300)
    
    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if len(expense_categories) > 1:
            if Session.focused_expense_category is None:
                logger.error("Focused expense category is None")
                raise ValueError("Focused expense category is None")

            current_index = expense_categories.index(Session.focused_expense_category)
            next_index = (current_index + 1) % len(expense_categories)

            Session.focused_expense_category.table_data.setGraphicsEffect(cast(QGraphicsDropShadowEffect, None))
            Session.focused_expense_category = expense_categories[next_index]
            Session.focused_expense_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_expense_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Expenses_scroll.ensureWidgetVisible(Session.focused_expense_category.table_data, 300)


def move_to_previous_category() -> None:
    """Move focus to the previous category in the list of categories."""

    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if len(income_categories) > 1:
            if Session.focused_income_category is None:
                logger.error("Focused income category is None")
                raise ValueError("Focused income category is None")

            current_index = income_categories.index(Session.focused_income_category)
            previous_index = (current_index - 1) % len(income_categories)

            Session.focused_income_category.table_data.setGraphicsEffect(cast(QGraphicsDropShadowEffect, None))
            Session.focused_income_category = income_categories[previous_index]
            Session.focused_income_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_income_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Incomes_scroll.ensureWidgetVisible(Session.focused_income_category.table_data, 300)
    
    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if len(expense_categories) > 1:
            if Session.focused_expense_category is None:
                logger.error("Focused expense category is None")
                raise ValueError("Focused expense category is None")

            current_index = expense_categories.index(Session.focused_expense_category)
            previous_index = (current_index - 1) % len(expense_categories)

            Session.focused_expense_category.table_data.setGraphicsEffect(cast(QGraphicsDropShadowEffect, None))
            Session.focused_expense_category = expense_categories[previous_index]
            Session.focused_expense_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_expense_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Expenses_scroll.ensureWidgetVisible(Session.focused_expense_category.table_data, 300)


def add_transaction_to_focused_category() -> None:
    """
    Adds a transaction to the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.add_transaction.click()

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.add_transaction.click()


def select_previous_transaction() -> None:
    """Selects the previous transaction in the focused category."""

    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            current_index = Session.focused_income_category.table_data.currentRow()
    
            if current_index > 0:
                Session.focused_income_category.table_data.selectRow(current_index - 1)
            elif current_index == 0 and Session.focused_income_category.table_data.rowCount() == 1:
                Session.focused_income_category.table_data.selectRow(0)

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            current_index = Session.focused_expense_category.table_data.currentRow()

            if current_index > 0:
                Session.focused_expense_category.table_data.selectRow(current_index - 1)
            elif current_index == 0 and Session.focused_expense_category.table_data.rowCount() == 1:
                Session.focused_expense_category.table_data.selectRow(0)


def select_next_transaction() -> None:
    """
    Selects the next transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            current_index = Session.focused_income_category.table_data.currentRow()

            if current_index < Session.focused_income_category.table_data.rowCount() - 1:
                Session.focused_income_category.table_data.selectRow(current_index + 1)
            elif current_index == 0 and Session.focused_income_category.table_data.rowCount() == 1:
                Session.focused_income_category.table_data.selectRow(0)

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            current_index = Session.focused_expense_category.table_data.currentRow()
            
            if current_index < Session.focused_expense_category.table_data.rowCount() - 1:
                Session.focused_expense_category.table_data.selectRow(current_index + 1)
            elif current_index == 0 and Session.focused_expense_category.table_data.rowCount() == 1:
                Session.focused_expense_category.table_data.selectRow(0)


def delete_transaction() -> None:
    """
    Deletes the selected transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.delete_transaction.click()

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.delete_transaction.click()


def edit_transaction() -> None:
    """
    Edits the selected transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.edit_transaction.click()

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.edit_transaction.click()
