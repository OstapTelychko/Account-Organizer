from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QMessageBox

from DesktopQtToolkit.message_window import MessageWindow
from project_configuration import APP_NAME
from DesktopQtToolkit.qsingleton import QSingleton

from GUI.gui_constants import APP_UPGRADE_ICON, NO_INTERNET_ICON

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow



class Messages(metaclass=QSingleton):
    """Represents all application messages."""

    singleton_message = "Cannot create multiple instances of Messages class. Use WindowsRegistry instead."

    def __init__(self, main_window:MainWindow, message_windows:dict[int, MessageWindow]) -> None:

        self.incorrect_data_type = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.account_already_exists = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.zero_current_balance = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Question, APP_NAME
        )

        self.category_exists = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.delete_category_confirmation = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Question, APP_NAME
        )
        self.unselected_row = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )

        self.only_one_row = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.empty_fields = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.day_out_range = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Critical, APP_NAME
        )

        self.delete_transaction_confirmation = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Question, APP_NAME
        )
        self.load_account_question = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Question, APP_NAME
        )
        self.delete_account_warning = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Critical, APP_NAME
        )

        self.empty_expression = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )
        self.forbidden_calculator_word = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Critical, APP_NAME
        )
        self.no_category = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )

        self.no_transactions = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )
        self.no_category_name = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )
        self.position_out_range = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )

        self.same_position = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )
        self.wrong_date = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )
        self.no_selected_category = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )

        self.below_recommended_min_backups = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Critical, APP_NAME
        )
        self.delete_backup_confirmation = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Warning, APP_NAME
        )
        self.different_app_version = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )

        self.load_backup_confirmation = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Question, APP_NAME
        )
        self.above_recommended_max_backups = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.no_auto_backup = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Warning, APP_NAME
        )

        self.no_auto_removal = MessageWindow(
            main_window, message_windows, True, QMessageBox.Icon.Warning, APP_NAME
        )
        self.auto_removal_disabled = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )
        self.update_available = MessageWindow(
            main_window, message_windows, True, APP_UPGRADE_ICON, APP_NAME
        )

        self.no_internet = MessageWindow(
            main_window, message_windows, False, NO_INTERNET_ICON, APP_NAME
        )
        self.failed_update_check = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Critical, APP_NAME
        )
        self.update_finished = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Information, APP_NAME
        )

        self.shortcut_already_used = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.empty_search_fields = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )
        self.failed_update_download = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Critical, APP_NAME
        )

        self.min_validation_value_bigger_than_max = MessageWindow(
            main_window, message_windows, False, QMessageBox.Icon.Warning, APP_NAME
        )