from PySide6.QtWidgets import QMessageBox

from DesktopQtToolkit.message_window import MessageWindow
from project_configuration import APP_NAME

from GUI.gui_constants import APP_ICON
from GUI.windows.main_window import MainWindow



class Messages():
    incorrect_data_type = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
    account_alredy_exists  = MessageWindow(MainWindow.window, MainWindow.message_windows, False, QMessageBox.Icon.Warning, APP_NAME, APP_ICON)
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