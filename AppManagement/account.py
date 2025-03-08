from sys import exit

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


def add_user():
    account_name = AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return Messages.empty_fields.exec()
        
    if Session.db.account_exists(account_name):
        Messages.account_alredy_exists.setText(LANGUAGES[Session.language]["Messages"][1])
        return Messages.account_alredy_exists.exec()

    balance = AddAccountWindow.current_balance.text()

    def complete_adding_account():
        AddAccountWindow.window.hide()

        Session.account_name = account_name
        Session.update_user_config()

        SettingsWindow.accounts.addItem(account_name)
        Session.accounts_list.append(Session.account_name)
        Session.switch_account = False
        load_account_data(Session.account_name)
        SettingsWindow.accounts.setCurrentText(Session.account_name)
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
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.language]["Windows"]["Settings"][1] + str(Session.db.get_account().created_date.strftime("%Y-%m-%d %H:%M:%S")))    
    
    Session.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()
    logger.info(f"Account {name} data loaded")


def load_accounts():
    Session.accounts_list = Session.db.get_all_accounts()

    for account in Session.accounts_list:
        account_layout_item = SwitchAccountWindow.AccountLayoutItem()
        account_layout_item.account_name_label.setText(account.name)
        account_layout_item.account_balance_label.setText(LANGUAGES[Session.language]["Windows"]["Main"][0] + str(account.current_balance))
        account_layout_item.account_creation_date_label.setText(LANGUAGES[Session.language]["Windows"]["Settings"][1] + account.created_date.strftime("%Y-%m-%d %H:%M:%S"))

        SwitchAccountWindow.accounts_layout.addWidget(account_layout_item.account_layout_item, alignment=ALIGN_V_CENTER)
 



def switch_account(name:str):
    if Session.switch_account:
        Messages.load_account_question.setText(LANGUAGES[Session.language]["Messages"][10].replace("account", name))

        Messages.load_account_question.exec()
        if Messages.load_account_question.clickedButton() == Messages.load_account_question.ok_button:
            load_account_data(name)
            logger.info(f"Account switched to {name}")
        else:
            Session.switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.account_name)
    else:
        Session.switch_account = True


def remove_account():
    Messages.delete_account_warning.setText(LANGUAGES[Session.language]["Messages"][11].replace("account", Session.account_name))

    Messages.delete_account_warning.exec()
    if Messages.delete_account_warning.clickedButton() == Messages.delete_account_warning.ok_button:
        Session.db.delete_account()
        Session.switch_account = False
        SettingsWindow.accounts.removeItem(Session.accounts_list.index(Session.account_name))
        Session.accounts_list.remove(Session.account_name)

        if len(Session.accounts_list) != 0:
            load_account_data(Session.accounts_list[0])
            Session.switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.accounts_list[0])
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

    if Session.db.account_exists(new_account_name):
        return Messages.account_alredy_exists.exec()

    Session.db.rename_account(new_account_name)

    Session.accounts_list[Session.accounts_list.index(Session.account_name)] = new_account_name
    Session.account_name = new_account_name
    Session.update_user_config()

    Session.switch_account = False
    SettingsWindow.accounts.clear()

    Session.switch_account = False
    SettingsWindow.accounts.addItems(Session.accounts_list)

    Session.switch_account = False
    SettingsWindow.accounts.setCurrentText(Session.account_name)

    RenameAccountWindow.window.hide()
    logger.info(f"Account renamed to {new_account_name}")