from sys import exit
from functools import partial

from AppObjects.session import Session
from AppObjects.logger import get_logger
from languages import LanguageStructure

from GUI.gui_constants import ALIGN_V_CENTER
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow, SwitchAccountWindow
from GUI.windows.messages import Messages

from AppManagement.balance import load_account_balance
from AppManagement.category import remove_categories_from_list, load_categories, activate_categories
from AppManagement.language import change_language_during_add_account, change_language



logger = get_logger(__name__)

def show_add_user_window():
    """Show add user window. First window if db doesn't contain any account."""

    change_language_during_add_account(Session.language)
    AddAccountWindow.window.exec()


def add_acccount():
    """Add account to database. If account already exists, show warning message."""

    account_name = AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return Messages.empty_fields.exec()
        
    if Session.db.account_query.account_exists(account_name):
        Messages.account_alredy_exists.setText(LanguageStructure.Messages.get_translation(1))
        return Messages.account_alredy_exists.exec()

    balance = AddAccountWindow.current_balance.text()

    def _complete_adding_account():
        """Complete adding account. Close add account window, update user config, load accounts and load account data. Created to avoid code duplication."""

        AddAccountWindow.window.done(1)

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
            _complete_adding_account()    
    else:
        Messages.zero_current_balance.setText(LanguageStructure.Messages.get_translation(2))

        Messages.zero_current_balance.exec()
        if Messages.zero_current_balance.clickedButton() == Messages.zero_current_balance.ok_button:
            Session.db.create_account(account_name, 0)
            _complete_adding_account()


def load_account_data(name:str):
    """Load account data. Load categories, set account name and balance."""

    #Remove loaded categories
    remove_categories_from_list()

    Session.account_name = name
    Session.db.set_account_id(Session.account_name)
    SettingsWindow.account_created_date.setText(LanguageStructure.Settings.get_translation(1) + str(Session.db.account_query.get_account().created_date.strftime("%Y-%m-%d %H:%M:%S")))    
    
    Session.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()
    logger.info(f"Account {name} data loaded")


def load_accounts():
    """Load accounts from database. Clear account switch widgets and load all accounts."""

    Session.accounts_list = Session.db.account_query.get_all_accounts()

    for account in Session.accounts_list:
        account_switch_widget = SwitchAccountWindow.AccountSwitchWidget()
        account_switch_widget.account_name_label.setText(account.name)
        account_switch_widget.account_balance_label.setText(LanguageStructure.MainWindow.get_translation(0) + str(account.current_balance))
        account_switch_widget.account_creation_date_label.setText(LanguageStructure.Settings.get_translation(1) + account.created_date.strftime("%Y-%m-%d %H:%M:%S"))

        account_switch_widget.switch_button.clicked.connect(partial(switch_account, account.name))
        account_switch_widget.switch_button.setText(LanguageStructure.GeneralManagement.get_translation(8))
        if account.name == Session.account_name:
            account_switch_widget.switch_button.setDisabled(True)

        SwitchAccountWindow.accounts_layout.addWidget(account_switch_widget.account_widget, alignment=ALIGN_V_CENTER)
        Session.account_switch_widgets.append(account_switch_widget)
 

def clear_accounts_layout():
    """Clear account switch widgets. Remove all widgets from layout and clear account switch widgets list."""

    Session.account_switch_widgets.clear()
    while SwitchAccountWindow.accounts_layout.count() > 0:
        widget = SwitchAccountWindow.accounts_layout.itemAt(0).widget()
        if widget:
            widget.setParent(None)


def switch_account(name:str):
    """Switch account. Show warning message and load account data. Disable switch button for current account and enable for other accounts.

        Arguments
        ---------
            `name` : (str) - Account name to switch to.
    """

    Messages.load_account_question.setText(LanguageStructure.Messages.get_translation(10).replace("account", name))
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
    """Remove account. Show warning message and remove account from database. If last account is removed, close app."""

    Messages.delete_account_warning.setText(LanguageStructure.Messages.get_translation(11).replace("account", Session.account_name))
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
    """Show rename account window. Set current account name to line edit."""

    RenameAccountWindow.new_account_name.setText(Session.account_name)
    RenameAccountWindow.window.exec()


def rename_account():
    """Rename account. Show warning message and rename account in database. If account already exists, show warning message."""
    
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

    RenameAccountWindow.window.done(1)
    logger.info(f"Account renamed to {new_account_name}")