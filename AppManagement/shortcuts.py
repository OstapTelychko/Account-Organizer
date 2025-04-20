from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QShortcut, QKeySequence
from functools import partial

from AppObjects.session import Session
from AppObjects.windows_registry import WindowsRegistry
from project_configuration import CATEGORY_TYPE

from AppObjects.windows_registry import WindowsRegistry
from GUI.gui_constants import FOCUSED_SHADOW_EFFECT_ARGUMENTS



def move_to_next_category():
    """Move focus to the next category in the list of categories."""

    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if len(income_categories) > 1:
            current_index = income_categories.index(Session.focused_income_category)
            next_index = (current_index + 1) % len(income_categories)

            Session.focused_income_category.table_data.setGraphicsEffect(None)
            Session.focused_income_category = income_categories[next_index]
            Session.focused_income_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_income_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Incomes_scroll.ensureWidgetVisible(Session.focused_income_category.table_data, 300)
    
    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if len(expense_categories) > 1:
            current_index = expense_categories.index(Session.focused_expense_category)
            next_index = (current_index + 1) % len(expense_categories)

            Session.focused_expense_category.table_data.setGraphicsEffect(None)
            Session.focused_expense_category = expense_categories[next_index]
            Session.focused_expense_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_expense_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Expenses_scroll.ensureWidgetVisible(Session.focused_expense_category.table_data, 300)


def move_to_previous_category():
    """Move focus to the previous category in the list of categories."""

    income_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
    expense_categories = list([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[1]])

    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if len(income_categories) > 1:
            current_index = income_categories.index(Session.focused_income_category)
            previous_index = (current_index - 1) % len(income_categories)

            Session.focused_income_category.table_data.setGraphicsEffect(None)
            Session.focused_income_category = income_categories[previous_index]
            Session.focused_income_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_income_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Incomes_scroll.ensureWidgetVisible(Session.focused_income_category.table_data, 300)
    
    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if len(expense_categories) > 1:
            current_index = expense_categories.index(Session.focused_expense_category)
            previous_index = (current_index - 1) % len(expense_categories)

            Session.focused_expense_category.table_data.setGraphicsEffect(None)
            Session.focused_expense_category = expense_categories[previous_index]
            Session.focused_expense_category.table_data.setGraphicsEffect(QGraphicsDropShadowEffect(Session.focused_expense_category.table_data,**FOCUSED_SHADOW_EFFECT_ARGUMENTS))
            WindowsRegistry.MainWindow.Expenses_scroll.ensureWidgetVisible(Session.focused_expense_category.table_data, 300)


def add_transaction_to_focused_category():
    """
    Adds a transaction to the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.add_transaction.click()

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.add_transaction.click()


def select_previous_transaction():
    """
    Selects the previous transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            current_index = Session.focused_income_category.table_data.currentRow()
            if current_index > 0:
                Session.focused_income_category.table_data.selectRow(current_index - 1)

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            current_index = Session.focused_expense_category.table_data.currentRow()
            if current_index > 0:
                Session.focused_expense_category.table_data.selectRow(current_index - 1)


def select_next_transaction():
    """
    Selects the next transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            current_index = Session.focused_income_category.table_data.currentRow()

            if current_index < Session.focused_income_category.table_data.rowCount() - 1:
                Session.focused_income_category.table_data.selectRow(current_index + 1)

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            current_index = Session.focused_expense_category.table_data.currentRow()
            
            if current_index < Session.focused_expense_category.table_data.rowCount() - 1:
                Session.focused_expense_category.table_data.selectRow(current_index + 1)


def delete_transaction():
    """
    Deletes the selected transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.delete_transaction.click()

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.delete_transaction.click()


def edit_transaction():
    """
    Edits the selected transaction in the focused category.
    """
    if WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 0:
        if Session.focused_income_category is not None:
            Session.focused_income_category.edit_transaction.click()

    elif WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex() == 1:
        if Session.focused_expense_category is not None:
            Session.focused_expense_category.edit_transaction.click()


def assign_shortcuts():
    """
    Assign shortcuts to the application.
    """

    for sub_window in WindowsRegistry.MainWindow.sub_windows.values():
        close_current_window_shortcut = QShortcut(
            QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.CLOSE_CURRENT_WINDOW]),
            sub_window)
        close_current_window_shortcut.activated.connect(partial(lambda sub_window: sub_window.done(1), sub_window))
    
    open_settings_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.OPEN_SETTINGS]),
        WindowsRegistry.MainWindow)
    open_settings_shortcut.activated.connect(WindowsRegistry.SettingsWindow.exec)

    open_statistics_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.OPEN_STATISTICS]),
        WindowsRegistry.MainWindow)
    open_statistics_shortcut.activated.connect(WindowsRegistry.StatisticsWindow.exec)

    switch_account_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_ACCOUNT]),
        WindowsRegistry.MainWindow)
    switch_account_shortcut.activated.connect(WindowsRegistry.SwitchAccountWindow.exec)

    switch_to_income_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_INCOME]),
        WindowsRegistry.MainWindow)
    switch_to_income_shortcut.activated.connect(lambda: WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(0))

    switch_to_expense_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_EXPENSE]),
        WindowsRegistry.MainWindow)
    switch_to_expense_shortcut.activated.connect(lambda: WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(1))

    load_previous_month_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.LOAD_PREVIOUS_MONTH]),
        WindowsRegistry.MainWindow)
    load_previous_month_shortcut.activated.connect(WindowsRegistry.MainWindow.previous_month_button.click)

    load_next_month_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.LOAD_NEXT_MONTH]),
        WindowsRegistry.MainWindow)
    load_next_month_shortcut.activated.connect(WindowsRegistry.MainWindow.next_month_button.click)

    move_to_next_category_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY]),
        WindowsRegistry.MainWindow)
    move_to_next_category_shortcut.activated.connect(move_to_next_category)

    move_to_previous_category_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]),
        WindowsRegistry.MainWindow)
    move_to_previous_category_shortcut.activated.connect(move_to_previous_category)

    add_transaction_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]),
        WindowsRegistry.MainWindow)
    add_transaction_shortcut.activated.connect(add_transaction_to_focused_category)

    select_previous_transaction_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_PREVIOUS_TRANSACTION]),
        WindowsRegistry.MainWindow)
    select_previous_transaction_shortcut.activated.connect(select_previous_transaction)

    select_next_transaction_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]),
        WindowsRegistry.MainWindow)
    select_next_transaction_shortcut.activated.connect(select_next_transaction)

    delete_transaction_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.DELETE_TRANSACTION]),
        WindowsRegistry.MainWindow)
    delete_transaction_shortcut.activated.connect(delete_transaction)

    edit_transaction_shortcut = QShortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.EDIT_TRANSACTION]),
        WindowsRegistry.MainWindow)
    edit_transaction_shortcut.activated.connect(edit_transaction)