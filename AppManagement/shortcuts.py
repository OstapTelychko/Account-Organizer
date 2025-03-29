from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from functools import partial

from AppObjects.session import Session
from project_configuration import CATEGORY_TYPE

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.statistics import StatisticsWindow
from GUI.windows.account import SwitchAccountWindow



def move_to_next_category():
    if MainWindow.Incomes_and_expenses.currentIndex() == 0:
        categories = iter([category for category in Session.categories.values() if category.type == CATEGORY_TYPE[0]])
        next()


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