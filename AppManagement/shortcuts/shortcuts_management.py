from __future__ import annotations
from typing import TYPE_CHECKING
from functools import partial
from collections import Counter

from PySide6.QtGui import QKeySequence

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.session import Session
from AppObjects.shortcuts_manager import ShortcutsManager

from AppManagement.shortcuts.shortcuts_actions import move_to_next_category, move_to_previous_category, add_transaction_to_focused_category,\
select_previous_transaction, select_next_transaction, delete_transaction, edit_transaction

from languages import LanguageStructure
from Statistics.copy_statistics import show_information_message

if TYPE_CHECKING:
    from GUI.windows.shortcuts import ShortcutsWindow



def show_user_shortcuts() -> None:
    """Show user shortcuts in Shorcuts window"""

    user_shortcuts = {
        WindowsRegistry.ShortcutsWindow.close_current_window_shortcut: Session.config.shortcuts[Session.config.ShortcutId.CLOSE_CURRENT_WINDOW],
        WindowsRegistry.ShortcutsWindow.open_settings_shortcut: Session.config.shortcuts[Session.config.ShortcutId.OPEN_SETTINGS],
        WindowsRegistry.ShortcutsWindow.open_statistics_shortcut: Session.config.shortcuts[Session.config.ShortcutId.OPEN_STATISTICS],
        WindowsRegistry.ShortcutsWindow.switch_account_shortcut: Session.config.shortcuts[Session.config.ShortcutId.SWITCH_ACCOUNT],
        WindowsRegistry.ShortcutsWindow.switch_to_income_shortcut: Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_INCOME],
        WindowsRegistry.ShortcutsWindow.switch_to_expense_shortcut: Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_EXPENSE],
        WindowsRegistry.ShortcutsWindow.load_previous_month_shortcut: Session.config.shortcuts[Session.config.ShortcutId.LOAD_PREVIOUS_MONTH],
        WindowsRegistry.ShortcutsWindow.load_next_month_shortcut: Session.config.shortcuts[Session.config.ShortcutId.LOAD_NEXT_MONTH],
        WindowsRegistry.ShortcutsWindow.focus_on_next_category_shortcut: Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY],
        WindowsRegistry.ShortcutsWindow.focus_on_previous_category_shortcut: Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY],
        WindowsRegistry.ShortcutsWindow.add_transaction_to_focused_category_shortcut: Session.config.shortcuts[Session.config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY],
        WindowsRegistry.ShortcutsWindow.select_previous_transaction_shortcut: Session.config.shortcuts[Session.config.ShortcutId.SELECT_PREVIOUS_TRANSACTION],
        WindowsRegistry.ShortcutsWindow.select_next_transaction_shortcut: Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION],
        WindowsRegistry.ShortcutsWindow.delete_transaction_shortcut: Session.config.shortcuts[Session.config.ShortcutId.DELETE_TRANSACTION],
        WindowsRegistry.ShortcutsWindow.edit_transaction_shortcut: Session.config.shortcuts[Session.config.ShortcutId.EDIT_TRANSACTION]
    }

    for shortcut, shortcut_value in user_shortcuts.items():
        shortcut.shortcut_edit.setText(shortcut_value)


def enable_shortcuts_reset() -> None:
    """ Enable shortcuts reset button in Shortcuts window """

    def _reset_shortcut(shortcut: ShortcutsWindow.ShortcutWidget, default_shortcut_info: tuple[str, str]) -> None:
        """Reset shortcut to default value."""

        shortcut.shortcut_edit.setText(default_shortcut_info[0])
        Session.config.shortcuts[default_shortcut_info[1]] = default_shortcut_info[0]
        Session.config.update_user_config()
        assign_shortcuts()

    for shortcut, default_shortcut_info in ShortcutsManager.shortcut_widget_to_default_values.items():
        shortcut.reset_shortcut.clicked.connect(partial(_reset_shortcut, shortcut, default_shortcut_info))


def assign_shortcuts() -> None:
    """
    Assign shortcuts to the application.
    """

    ShortcutsManager.clear_shortcuts()

    for sub_window in WindowsRegistry.MainWindow.sub_windows.values():
        ShortcutsManager.add_shortcut(QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.CLOSE_CURRENT_WINDOW]), sub_window, partial(lambda sub_window: sub_window.done(1), sub_window))

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.OPEN_SETTINGS]),
        WindowsRegistry.MainWindow, WindowsRegistry.SettingsWindow.exec)    

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.OPEN_STATISTICS]),
        WindowsRegistry.MainWindow, WindowsRegistry.StatisticsWindow.exec)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_ACCOUNT]),
        WindowsRegistry.MainWindow, WindowsRegistry.SwitchAccountWindow.exec)
    
    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_INCOME]),
        WindowsRegistry.MainWindow, lambda: WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(0))

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SWITCH_TO_EXPENSE]),
        WindowsRegistry.MainWindow, lambda: WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(1))
    
    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.LOAD_PREVIOUS_MONTH]),
        WindowsRegistry.MainWindow, WindowsRegistry.MainWindow.previous_month_button.click)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.LOAD_NEXT_MONTH]),
        WindowsRegistry.MainWindow, WindowsRegistry.MainWindow.next_month_button.click)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY]),
        WindowsRegistry.MainWindow, move_to_next_category)
    
    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY]),
        WindowsRegistry.MainWindow, move_to_previous_category)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY]),
        WindowsRegistry.MainWindow, add_transaction_to_focused_category)
    
    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_PREVIOUS_TRANSACTION]),
        WindowsRegistry.MainWindow, select_previous_transaction)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.SELECT_NEXT_TRANSACTION]),
        WindowsRegistry.MainWindow, select_next_transaction)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.DELETE_TRANSACTION]),
        WindowsRegistry.MainWindow, delete_transaction)

    ShortcutsManager.add_shortcut(
        QKeySequence(Session.config.shortcuts[Session.config.ShortcutId.EDIT_TRANSACTION]),
        WindowsRegistry.MainWindow, edit_transaction)
    

def save_shortcuts() -> int:
    """Save shortcuts to user config."""

    shortcuts = {
        Session.config.ShortcutId.CLOSE_CURRENT_WINDOW: WindowsRegistry.ShortcutsWindow.close_current_window_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.OPEN_SETTINGS: WindowsRegistry.ShortcutsWindow.open_settings_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.OPEN_STATISTICS: WindowsRegistry.ShortcutsWindow.open_statistics_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.SWITCH_ACCOUNT: WindowsRegistry.ShortcutsWindow.switch_account_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.SWITCH_TO_INCOME: WindowsRegistry.ShortcutsWindow.switch_to_income_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.SWITCH_TO_EXPENSE: WindowsRegistry.ShortcutsWindow.switch_to_expense_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.LOAD_PREVIOUS_MONTH: WindowsRegistry.ShortcutsWindow.load_previous_month_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.LOAD_NEXT_MONTH: WindowsRegistry.ShortcutsWindow.load_next_month_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.FOCUS_ON_NEXT_CATEGORY: WindowsRegistry.ShortcutsWindow.focus_on_next_category_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY: WindowsRegistry.ShortcutsWindow.focus_on_previous_category_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY: WindowsRegistry.ShortcutsWindow.add_transaction_to_focused_category_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.SELECT_PREVIOUS_TRANSACTION: WindowsRegistry.ShortcutsWindow.select_previous_transaction_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.SELECT_NEXT_TRANSACTION: WindowsRegistry.ShortcutsWindow.select_next_transaction_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.DELETE_TRANSACTION: WindowsRegistry.ShortcutsWindow.delete_transaction_shortcut.shortcut_edit.text(),
        Session.config.ShortcutId.EDIT_TRANSACTION: WindowsRegistry.ShortcutsWindow.edit_transaction_shortcut.shortcut_edit.text()
    }

    shortcuts_keystrokes_occurrences = Counter(shortcuts.values())
    repeated_shortcuts = [shortcut for shortcut, count in shortcuts_keystrokes_occurrences.items() if count > 1]

    if repeated_shortcuts:
        formatted_text = LanguageStructure.Messages.get_translation(33).replace("keystroke_value", repeated_shortcuts[0])
        WindowsRegistry.Messages.shortcut_already_used.setText(formatted_text)
        return WindowsRegistry.Messages.shortcut_already_used.exec()
            
    for shortcut_id, shortcut_value in shortcuts.items():
        Session.config.shortcuts[shortcut_id] = shortcut_value

    Session.config.update_user_config()
    assign_shortcuts()
    show_information_message(LanguageStructure.ShortcutsManagement.get_translation(1))
    WindowsRegistry.ShortcutsWindow.done(1)
    return 1


def load_shortcuts() -> None:
    """Load shortcuts from user config and assign them to the application."""

    assign_shortcuts()
    enable_shortcuts_reset()
    show_user_shortcuts()