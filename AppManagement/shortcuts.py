from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QShortcut, QKeySequence
from functools import partial

from AppObjects.session import Session
from project_configuration import CATEGORY_TYPE

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.statistics import StatisticsWindow
from GUI.windows.account import SwitchAccountWindow
from GUI.gui_constants import FOCUSED_SHADOW_EFFECT_ARGUMENTS



def move_to_next_category():
    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if len(income_categories) > 1:
            current_index = income_categories.index(Session.focused_income_category)
            next_index = (current_index + 1) % len(income_categories)

            Session.focused_income_category.table_data.setGraphicsEffect(None)
            Session.focused_income_category = income_categories[next_index]
            Session.focused_income_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_income_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            MainWindow.Incomes_scroll.ensureWidgetVisible(Session.focused_income_category.table_data, 300)
    
    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if len(expense_categories) > 1:
            current_index = expense_categories.index(Session.focused_expense_category)
            next_index = (current_index + 1) % len(expense_categories)

            Session.focused_expense_category.table_data.setGraphicsEffect(None)
            Session.focused_expense_category = expense_categories[next_index]
            Session.focused_expense_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_expense_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            MainWindow.Expenses_scroll.ensureWidgetVisible(Session.focused_expense_category.table_data, 300)


def move_to_previous_category():
    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if len(income_categories) > 1:
            current_index = income_categories.index(Session.focused_income_category)
            previous_index = (current_index - 1) % len(income_categories)

            Session.focused_income_category.table_data.setGraphicsEffect(None)
            Session.focused_income_category = income_categories[previous_index]
            Session.focused_income_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_income_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            MainWindow.Incomes_scroll.ensureWidgetVisible(Session.focused_income_category.table_data, 300)
    
    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if len(expense_categories) > 1:
            current_index = expense_categories.index(Session.focused_expense_category)
            previous_index = (current_index - 1) % len(expense_categories)

            Session.focused_expense_category.table_data.setGraphicsEffect(None)
            Session.focused_expense_category = expense_categories[previous_index]
            Session.focused_expense_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_expense_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            MainWindow.Expenses_scroll.ensureWidgetVisible(Session.focused_expense_category.table_data, 300)


def add_transaction_to_focused_category():
    """
    Adds a transaction to the focused category.
    """
    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.add_transaction.click()

    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.add_transaction.click()


def select_previous_transaction():
    """
    Selects the previous transaction in the focused category.
    """
    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            current_index = Session.focused_income_category.table_data.currentRow()
            if current_index > 0:
                Session.focused_income_category.table_data.selectRow(current_index - 1)

    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            current_index = Session.focused_expense_category.table_data.currentRow()
            if current_index > 0:
                Session.focused_expense_category.table_data.selectRow(current_index - 1)


def select_next_transaction():
    """
    Selects the next transaction in the focused category.
    """
    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            current_index = Session.focused_income_category.table_data.currentRow()
            if current_index < Session.focused_income_category.table_data.rowCount() - 1:
                Session.focused_income_category.table_data.selectRow(current_index + 1)

    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            current_index = Session.focused_expense_category.table_data.currentRow()
            if current_index < Session.focused_expense_category.table_data.rowCount() - 1:
                Session.focused_expense_category.table_data.selectRow(current_index + 1)


def delete_transaction():
    """
    Deletes the selected transaction in the focused category.
    """
    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.delete_transaction.click()

    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.delete_transaction.click()


def edit_transaction():
    """
    Edits the selected transaction in the focused category.
    """
    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.edit_transaction.click()

    elif MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.edit_transaction.click()


def assign_shortcuts():
    """
    Assign shortcuts to the application.
    """

    for sub_window in MainWindow.sub_windows.values():
        close_current_window_shortcut = QShortcut(
            QKeySequence(Session.shortcuts[Session.ShortcutId.CLOSE_CURRENT_WINDOW]),
            sub_window)
        close_current_window_shortcut.activated.connect(partial(lambda sub_window: sub_window.done(1), sub_window))
    
    open_settings_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.OPEN_SETTINGS]),
        MainWindow.window)
    open_settings_shortcut.activated.connect(SettingsWindow.window.exec)

    open_statistics_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.OPEN_STATISTICS]),
        MainWindow.window)
    open_statistics_shortcut.activated.connect(StatisticsWindow.window.exec)

    switch_account_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.SWITCH_ACCOUNT]),
        MainWindow.window)
    switch_account_shortcut.activated.connect(SwitchAccountWindow.window.exec)

    switch_to_income_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.SWITCH_TO_INCOME]),
        MainWindow.window)
    switch_to_income_shortcut.activated.connect(lambda: MainWindow.Incomes_and_expenses.setCurrentIndex(0))

    switch_to_expense_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.SWITCH_TO_EXPENSE]),
        MainWindow.window)
    switch_to_expense_shortcut.activated.connect(lambda: MainWindow.Incomes_and_expenses.setCurrentIndex(1))

    load_previous_month_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.LOAD_PREVIOUS_MONTH]),
        MainWindow.window)
    load_previous_month_shortcut.activated.connect(MainWindow.previous_month_button.click)

    load_next_month_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.LOAD_NEXT_MONTH]),
        MainWindow.window)
    load_next_month_shortcut.activated.connect(MainWindow.next_month_button.click)

    move_to_next_category_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.FOCUS_ON_NEXT_CATEGORY]),
        MainWindow.window)
    move_to_next_category_shortcut.activated.connect(move_to_next_category)

    move_to_previous_category_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]),
        MainWindow.window)
    move_to_previous_category_shortcut.activated.connect(move_to_previous_category)

    add_transaction_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]),
        MainWindow.window)
    add_transaction_shortcut.activated.connect(add_transaction_to_focused_category)

    select_previous_transaction_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_PREVIOUS_TRANSACTION]),
        MainWindow.window)
    select_previous_transaction_shortcut.activated.connect(select_previous_transaction)

    select_next_transaction_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.SELECT_NEXT_TRANSACTION]),
        MainWindow.window)
    select_next_transaction_shortcut.activated.connect(select_next_transaction)

    delete_transaction_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.DELETE_TRANSACTION]),
        MainWindow.window)
    delete_transaction_shortcut.activated.connect(delete_transaction)

    edit_transaction_shortcut = QShortcut(
        QKeySequence(Session.shortcuts[Session.ShortcutId.EDIT_TRANSACTION]),
        MainWindow.window)
    edit_transaction_shortcut.activated.connect(edit_transaction)