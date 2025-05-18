from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QShortcut

from AppObjects.windows_registry import WindowsRegistry
from AppObjects.user_config import UserConfig
from AppObjects.session import Session

if TYPE_CHECKING:
    from typing import Callable
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QKeySequence


class ShortcutsManager:
    """Manages shortcuts in the application and allows dynamic updates"""

    active_shortcuts:list[QShortcut] = []

    shortcut_widget_to_translations = {
        WindowsRegistry.ShortcutsWindow.close_current_window_shortcut: 0,
        WindowsRegistry.ShortcutsWindow.open_settings_shortcut: 1,
        WindowsRegistry.ShortcutsWindow.open_statistics_shortcut: 2,
        WindowsRegistry.ShortcutsWindow.switch_account_shortcut: 3,
        WindowsRegistry.ShortcutsWindow.switch_to_income_shortcut: 4,
        WindowsRegistry.ShortcutsWindow.switch_to_expense_shortcut: 5,
        WindowsRegistry.ShortcutsWindow.load_previous_month_shortcut: 6,
        WindowsRegistry.ShortcutsWindow.load_next_month_shortcut: 7,
        WindowsRegistry.ShortcutsWindow.focus_on_next_category_shortcut: 8,
        WindowsRegistry.ShortcutsWindow.focus_on_previous_category_shortcut: 9,
        WindowsRegistry.ShortcutsWindow.add_transaction_to_focused_category_shortcut: 10,
        WindowsRegistry.ShortcutsWindow.select_previous_transaction_shortcut: 11,
        WindowsRegistry.ShortcutsWindow.select_next_transaction_shortcut: 12,
        WindowsRegistry.ShortcutsWindow.delete_transaction_shortcut: 13,
        WindowsRegistry.ShortcutsWindow.edit_transaction_shortcut: 14
    }

    user_config = UserConfig(Session.test_mode)
    default_shortcuts_values = user_config.shortcuts

    shortcut_widget_to_default_values = {
        WindowsRegistry.ShortcutsWindow.close_current_window_shortcut: (default_shortcuts_values[user_config.ShortcutId.CLOSE_CURRENT_WINDOW], user_config.ShortcutId.CLOSE_CURRENT_WINDOW),
        WindowsRegistry.ShortcutsWindow.open_settings_shortcut: (default_shortcuts_values[user_config.ShortcutId.OPEN_SETTINGS], user_config.ShortcutId.OPEN_SETTINGS),
        WindowsRegistry.ShortcutsWindow.open_statistics_shortcut: (default_shortcuts_values[user_config.ShortcutId.OPEN_STATISTICS], user_config.ShortcutId.OPEN_STATISTICS),
        WindowsRegistry.ShortcutsWindow.switch_account_shortcut: (default_shortcuts_values[user_config.ShortcutId.SWITCH_ACCOUNT], user_config.ShortcutId.SWITCH_ACCOUNT),
        WindowsRegistry.ShortcutsWindow.switch_to_income_shortcut: (default_shortcuts_values[user_config.ShortcutId.SWITCH_TO_INCOME], user_config.ShortcutId.SWITCH_TO_INCOME),
        WindowsRegistry.ShortcutsWindow.switch_to_expense_shortcut: (default_shortcuts_values[user_config.ShortcutId.SWITCH_TO_EXPENSE], user_config.ShortcutId.SWITCH_TO_EXPENSE),
        WindowsRegistry.ShortcutsWindow.load_previous_month_shortcut: (default_shortcuts_values[user_config.ShortcutId.LOAD_PREVIOUS_MONTH], user_config.ShortcutId.LOAD_PREVIOUS_MONTH),
        WindowsRegistry.ShortcutsWindow.load_next_month_shortcut: (default_shortcuts_values[user_config.ShortcutId.LOAD_NEXT_MONTH], user_config.ShortcutId.LOAD_NEXT_MONTH),
        WindowsRegistry.ShortcutsWindow.focus_on_next_category_shortcut: (default_shortcuts_values[user_config.ShortcutId.FOCUS_ON_NEXT_CATEGORY], user_config.ShortcutId.FOCUS_ON_NEXT_CATEGORY),
        WindowsRegistry.ShortcutsWindow.focus_on_previous_category_shortcut: (default_shortcuts_values[user_config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY], user_config.ShortcutId.FOCUS_ON_PREVIOUS_CATEGORY),
        WindowsRegistry.ShortcutsWindow.add_transaction_to_focused_category_shortcut: (default_shortcuts_values[user_config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY], user_config.ShortcutId.ADD_TRANSACTION_TO_FOCUSED_CATEGORY),
        WindowsRegistry.ShortcutsWindow.select_previous_transaction_shortcut: (default_shortcuts_values[user_config.ShortcutId.SELECT_PREVIOUS_TRANSACTION], user_config.ShortcutId.SELECT_PREVIOUS_TRANSACTION),
        WindowsRegistry.ShortcutsWindow.select_next_transaction_shortcut: (default_shortcuts_values[user_config.ShortcutId.SELECT_NEXT_TRANSACTION], user_config.ShortcutId.SELECT_NEXT_TRANSACTION),
        WindowsRegistry.ShortcutsWindow.delete_transaction_shortcut: (default_shortcuts_values[user_config.ShortcutId.DELETE_TRANSACTION], user_config.ShortcutId.DELETE_TRANSACTION),
        WindowsRegistry.ShortcutsWindow.edit_transaction_shortcut: (default_shortcuts_values[user_config.ShortcutId.EDIT_TRANSACTION], user_config.ShortcutId.EDIT_TRANSACTION)
    }

    @staticmethod
    def add_shortcut(key_sequence:QKeySequence, parent:QWidget, action:Callable[[], None|int]) -> None:
        """Adds a shortcut to the application and connects it to an action"""

        shortcut = QShortcut(key_sequence, parent)
        shortcut.activated.connect(action)
        ShortcutsManager.active_shortcuts.append(shortcut)
    

    @staticmethod
    def clear_shortcuts() -> None:
        """Clears all active shortcuts"""
        
        for shortcut in ShortcutsManager.active_shortcuts:
            shortcut.setEnabled(False)
            shortcut.activated.disconnect()
            shortcut.setParent(None) #type: ignore[arg-type] #Mypy doesn't accept None as valid parent
            
        ShortcutsManager.active_shortcuts.clear()
    