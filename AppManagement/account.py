from sys import exit
from functools import partial

from AppObjects.session import Session
from AppObjects.logger import get_logger
from languages import LANGUAGES

from GUI.gui_constants import ALIGN_V_CENTER
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow, SwitchAccountWindow
from GUI.windows.messages import Messages

from AppManagement.balance import load_account_balance
from AppManagement.category import remove_categories_from_list, load_categories, activate_categories
from AppManagement.language import change_language_during_add_account, change_language



logger = get_logger(__name__)

def show_add_user_window():
    change_language_during_add_account(Session.language)
    AddAccountWindow.window.exec()


def add_acccount():
    account_name = AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return Messages.empty_fields.exec()
        
    if Session.db.account_query.account_exists(account_name):
        Messages.account_alredy_exists.setText(LANGUAGES[Session.language]["Messages"][1])
        return Messages.account_alredy_exists.exec()

    balance = AddAccountWindow.current_balance.text()

    def complete_adding_account():
        AddAccountWindow.window.hide()

        Session.account_name = account_name
        Session.update_user_config()
        clear_accounts_layout()

        load_accounts()
        load_account_data(Session.account_name)
        change_language()
        logger.info(f"Account {account_name} added")  

    if balance != "":
        if balance.replace(",","").replace(".","").isdigit():

            if balance.find("."):
                balance = float(balance)
            elif balance.find(","):#if balance contains "," for example: 4,5 will be 4.5 
                balance = float(".".join(balance.split(",")))
            else:
                balance = int(balance)

            Session.db.create_account(account_name, balance)
            complete_adding_account()    
    else:
        Messages.zero_current_balance.setText(LANGUAGES[Session.language]["Messages"][2])

        Messages.zero_current_balance.exec()
        if Messages.zero_current_balance.clickedButton() == Messages.zero_current_balance.ok_button:
            Session.db.create_account(account_name, 0)
            complete_adding_account()


def load_account_data(name:str):
    #Remove loaded categories
    remove_categories_from_list()

    Session.account_name = name
    Session.db.set_account_id(Session.account_name)
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.language]["Windows"]["Settings"][1] + str(Session.db.account_query.get_account().created_date.strftime("%Y-%m-%d %H:%M:%S")))    
    
    Session.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()
    logger.info(f"Account {name} data loaded")


def load_accounts():
    Session.accounts_list = Session.db.account_query.get_all_accounts()

    for account in Session.accounts_list:
        account_switch_widget = SwitchAccountWindow.AccountSwitchWidget()
        account_switch_widget.account_name_label.setText(account.name)
        account_switch_widget.account_balance_label.setText(LANGUAGES[Session.language]["Windows"]["Main"][0] + str(account.current_balance))
        account_switch_widget.account_creation_date_label.setText(LANGUAGES[Session.language]["Windows"]["Settings"][1] + account.created_date.strftime("%Y-%m-%d %H:%M:%S"))

        account_switch_widget.switch_button.clicked.connect(partial(switch_account, account.name))
        account_switch_widget.switch_button.setText(LANGUAGES[Session.language]["General management"][8])
        if account.name == Session.account_name:
            account_switch_widget.switch_button.setDisabled(True)

        SwitchAccountWindow.accounts_layout.addWidget(account_switch_widget.account_widget, alignment=ALIGN_V_CENTER)
        Session.account_switch_widgets.append(account_switch_widget)
 

def clear_accounts_layout():
    Session.account_switch_widgets.clear()
    while SwitchAccountWindow.accounts_layout.count() > 0:
        widget = SwitchAccountWindow.accounts_layout.itemAt(0).widget()
        if widget:
            widget.setParent(None)


def switch_account(name:str):
    Messages.load_account_question.setText(LANGUAGES[Session.language]["Messages"][10].replace("account", name))

    Messages.load_account_question.exec()
    if Messages.load_account_question.clickedButton() == Messages.load_account_question.ok_button:
        for widget in Session.account_switch_widgets:
            if widget.account_name_label.text() == name:
                widget.switch_button.setDisabled(True)
            else:
                widget.switch_button.setDisabled(False)
        load_account_data(name)
        logger.info(f"Account switched to {name}")
    


def remove_account():
    Messages.delete_account_warning.setText(LANGUAGES[Session.language]["Messages"][11].replace("account", Session.account_name))

    Messages.delete_account_warning.exec()
    if Messages.delete_account_warning.clickedButton() == Messages.delete_account_warning.ok_button:
        Session.db.account_query.delete_account()
        clear_accounts_layout()
        load_accounts()

        if len(Session.accounts_list) != 0:
            next_name = Session.accounts_list[0].name
            for widget in Session.account_switch_widgets:
                if widget.account_name_label.text() == next_name:
                    widget.switch_button.setDisabled(True)

            load_account_data(next_name)
            logger.info(f"Account {Session.account_name} removed")
        else:#Close app if db is empty
            Session.update_user_config()
            logger.info("Last account removed. Closing app")
            exit()


def show_rename_account_window():
    RenameAccountWindow.new_account_name.setText(Session.account_name)
    RenameAccountWindow.window.exec()


def rename_account():
    new_account_name = RenameAccountWindow.new_account_name.text().strip()

    if new_account_name == "":
        return Messages.empty_fields.exec()

    if Session.db.account_query.account_exists(new_account_name):
        return Messages.account_alredy_exists.exec()

    Session.db.account_query.rename_account(new_account_name)

    Session.account_name = new_account_name
    Session.update_user_config()
    clear_accounts_layout()
    load_accounts()

    RenameAccountWindow.window.hide()
    logger.info(f"Account renamed to {new_account_name}")