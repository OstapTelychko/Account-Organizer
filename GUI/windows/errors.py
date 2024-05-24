from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

from GUI.windows.main import APP_ICON




errors_list = []
def create_error(type_confirm:bool, icon:QMessageBox.Icon) -> QMessageBox:
    error = QMessageBox()
    error.setWindowFlags(Qt.WindowType.Drawer)
    error.addButton(QMessageBox.StandardButton.Ok)
    error.setWindowTitle("Account Organizer")
    if type_confirm:
        error.addButton(QMessageBox.StandardButton.Cancel)  
    error.setWindowIcon(APP_ICON)
    error.setIcon(icon)
    errors_list.append(error)
    return error



class Errors():
    incorrect_data_type = create_error(False, QMessageBox.Icon.Warning)
    account_alredy_exists  = create_error(False, QMessageBox.Icon.Warning)
    zero_current_balance = create_error(True, QMessageBox.Icon.Question)
    category_exists = create_error(False, QMessageBox.Icon.Warning)
    delete_category_confirmation = create_error(True, QMessageBox.Icon.Question)
    unselected_row = create_error(False, QMessageBox.Icon.Warning)
    only_one_row = create_error(False, QMessageBox.Icon.Warning)
    empty_fields = create_error(False, QMessageBox.Icon.Warning)
    day_out_range = create_error(False, QMessageBox.Icon.Critical)
    delete_transaction_confirmation = create_error(True, QMessageBox.Icon.Question)
    load_account_question =  create_error(True, QMessageBox.Icon.Question)
    delete_account_warning = create_error(True, QMessageBox.Icon.Critical)
    empty_expression = create_error(False, QMessageBox.Icon.Information)
    forbidden_calculator_word = create_error(False, QMessageBox.Icon.Critical)
    no_category = create_error(False, QMessageBox.Icon.Information)
    no_transactions = create_error(False, QMessageBox.Icon.Information)
    no_category_name = create_error(False, QMessageBox.Icon.Information)
    position_out_range = create_error(False, QMessageBox.Icon.Warning)
    same_position = create_error(False, QMessageBox.Icon.Information)
    wrong_date = create_error(False, QMessageBox.Icon.Information)
    no_selected_category = create_error(False, QMessageBox.Icon.Information)