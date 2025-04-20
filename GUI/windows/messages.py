from PySide6.QtWidgets import QMessageBox

from DesktopQtToolkit.message_window import MessageWindow
from project_configuration import APP_NAME

from GUI.gui_constants import APP_ICON, APP_UPGRADE_ICON, NO_INTERNET_ICON
from GUI.windows.main_window import MainWindow



class Messages():
    """Represents all application messages."""

    incorrect_data_type = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    account_already_exists  = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    zero_current_balance = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Question, APP_NAME, APP_ICON)
    
    category_exists = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    delete_category_confirmation = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Question, APP_NAME, APP_ICON)
    unselected_row = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)

    only_one_row = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    empty_fields = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    day_out_range = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Critical, APP_NAME, APP_ICON)

    delete_transaction_confirmation = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Question, APP_NAME, APP_ICON)
    load_account_question =  MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Question, APP_NAME, APP_ICON)
    delete_account_warning = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Critical, APP_NAME, APP_ICON)

    empty_expression = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)
    forbidden_calculator_word = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Critical, APP_NAME, APP_ICON)
    no_category = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)

    no_transactions = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)
    no_category_name = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)
    position_out_range = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)

    same_position = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)
    wrong_date = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)
    no_selected_category = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)

    below_recommended_min_backups = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Critical, APP_NAME, APP_ICON)
    delete_buckup_confirmation = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    different_app_version = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)

    load_backup_confirmation = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Question, APP_NAME, APP_ICON)
    above_recommended_max_backups = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    no_auto_backup = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)

    no_auto_removal = MessageWindow(MainWindow.window, MainWindow.message_windows, True, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    auto_removal_disabled = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)
    update_available = MessageWindow(MainWindow.window, MainWindow.message_windows, True, APP_UPGRADE_ICON, APP_NAME, APP_ICON)

    no_internet = MessageWindow(MainWindow.window, MainWindow.message_windows, False, NO_INTERNET_ICON, APP_NAME, APP_ICON)
    failed_update_check = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Critical, APP_NAME, APP_ICON)
    update_finished = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Information, APP_NAME, APP_ICON)