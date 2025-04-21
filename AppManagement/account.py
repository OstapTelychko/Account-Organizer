from sys import exit
from functools import partial

from AppObjects.session import Session
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from languages import LanguageStructure

from GUI.gui_constants import ALIGN_V_CENTER

from AppManagement.balance import load_account_balance
from AppManagement.category import remove_categories_from_list, load_categories, activate_categories
from AppManagement.language import change_language_during_add_account, change_language



logger = get_logger(__name__)

def show_add_user_window():
    """Show add user window. First window if db doesn't contain any account."""

    change_language_during_add_account(Session.config.language)
    WindowsRegistry.AddAccountWindow.exec()


def add_account():
    """Add account to database. If account already exists, show warning message."""

    account_name = WindowsRegistry.AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return WindowsRegistry.Messages.empty_fields.exec()
        
    if Session.db.account_query.account_exists(account_name):
        WindowsRegistry.Messages.account_already_exists.setText(LanguageStructure.Messages.get_translation(1))
        return WindowsRegistry.Messages.account_already_exists.exec()

    raw_balance = WindowsRegistry.AddAccountWindow.current_balance.text()

    def _complete_adding_account():
        """Complete adding account. Close add account window, update user config, load accounts and load account data. Created to avoid code duplication."""

        WindowsRegistry.AddAccountWindow.done(1)

        Session.config.account_name = account_name
        Session.config.update_user_config()
        clear_accounts_layout()

        load_accounts()
        load_account_data(Session.config.account_name)
        change_language()
        logger.info(f"Account {account_name} added")  

    if raw_balance != "":
        if not raw_balance.replace(",","").replace(".","").isdigit():
            return
        
        if "." in raw_balance:
            balance = float(raw_balance)
        elif "," in raw_balance:#if balance contains "," for example: 4,5 will be 4.5 
            balance = float(".".join(raw_balance.split(",")))
        else:
            balance = int(raw_balance)

        Session.db.create_account(account_name, balance)
        _complete_adding_account()    
    else:
        WindowsRegistry.Messages.zero_current_balance.setText(LanguageStructure.Messages.get_translation(2))

        WindowsRegistry.Messages.zero_current_balance.exec()
        if WindowsRegistry.Messages.zero_current_balance.clickedButton() == WindowsRegistry.Messages.zero_current_balance.ok_button:
            Session.db.create_account(account_name, 0)
            _complete_adding_account()


def load_account_data(name:str):
    """Load account data. Load categories, set account name and balance."""

    #Remove loaded categories
    remove_categories_from_list()

    Session.config.account_name = name
    Session.db.set_account_id(Session.config.account_name)
    WindowsRegistry.SettingsWindow.account_created_date.setText(LanguageStructure.Settings.get_translation(1) + str(Session.db.account_query.get_account().created_date.strftime("%Y-%m-%d %H:%M:%S")))    
    
    Session.config.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()
    logger.info(f"Account {name} data loaded")


def load_accounts():
    """Load accounts from database. Clear account switch widgets and load all accounts."""

    Session.accounts_list = Session.db.account_query.get_all_accounts()

    for account in Session.accounts_list:
        account_switch_widget = WindowsRegistry.SwitchAccountWindow.AccountSwitchWidget()
        account_switch_widget.account_name_label.setText(account.name)
        account_switch_widget.account_balance_label.setText(LanguageStructure.MainWindow.get_translation(0) + str(account.current_balance))
        account_switch_widget.account_creation_date_label.setText(LanguageStructure.Settings.get_translation(1) + account.created_date.strftime("%Y-%m-%d %H:%M:%S"))

        account_switch_widget.switch_button.clicked.connect(partial(switch_account, account.name))
        account_switch_widget.switch_button.setText(LanguageStructure.GeneralManagement.get_translation(8))
        if account.name == Session.config.account_name:
            account_switch_widget.switch_button.setDisabled(True)

        WindowsRegistry.SwitchAccountWindow.accounts_layout.addWidget(account_switch_widget.account_widget, alignment=ALIGN_V_CENTER)
        Session.account_switch_widgets.append(account_switch_widget)
 

def clear_accounts_layout():
    """Clear account switch widgets. Remove all widgets from layout and clear account switch widgets list."""

    Session.account_switch_widgets.clear()
    while WindowsRegistry.SwitchAccountWindow.accounts_layout.count() > 0:
        widget = WindowsRegistry.SwitchAccountWindow.accounts_layout.itemAt(0).widget()
        if widget:
            widget.setParent(None) #type: ignore[call-overload] #Mypy doesn't understand that setParent can be None


def switch_account(name:str):
    """Switch account. Show warning message and load account data. Disable switch button for current account and enable for other accounts.

        Arguments
        ---------
            `name` : (str) - Account name to switch to.
    """

    WindowsRegistry.Messages.load_account_question.setText(LanguageStructure.Messages.get_translation(10).replace("account", name))
    WindowsRegistry.Messages.load_account_question.exec()

    if WindowsRegistry.Messages.load_account_question.clickedButton() == WindowsRegistry.Messages.load_account_question.ok_button:
        for widget in Session.account_switch_widgets:
            if widget.account_name_label.text() == name:
                widget.switch_button.setDisabled(True)
            else:
                widget.switch_button.setDisabled(False)
        load_account_data(name)
        logger.info(f"Account switched to {name}")
    


def remove_account():
    """Remove account. Show warning message and remove account from database. If last account is removed, close app."""

    WindowsRegistry.Messages.delete_account_warning.setText(LanguageStructure.Messages.get_translation(11).replace("account", Session.config.account_name))
    WindowsRegistry.Messages.delete_account_warning.exec()

    if WindowsRegistry.Messages.delete_account_warning.clickedButton() == WindowsRegistry.Messages.delete_account_warning.ok_button:
        Session.db.account_query.delete_account()
        clear_accounts_layout()
        load_accounts()

        if len(Session.accounts_list) != 0:
            next_name = Session.accounts_list[0].name
            for widget in Session.account_switch_widgets:
                if widget.account_name_label.text() == next_name:
                    widget.switch_button.setDisabled(True)

            load_account_data(next_name)
            logger.info(f"Account {Session.config.account_name} removed")
        else:#Close app if db is empty
            Session.config.update_user_config()
            logger.info("Last account removed. Closing app")
            exit()


def show_rename_account_window():
    """Show rename account window. Set current account name to line edit."""

    WindowsRegistry.RenameAccountWindow.new_account_name.setText(Session.config.account_name)
    WindowsRegistry.RenameAccountWindow.exec()


def rename_account():
    """Rename account. Show warning message and rename account in database. If account already exists, show warning message."""
    
    new_account_name = WindowsRegistry.RenameAccountWindow.new_account_name.text().strip()

    if new_account_name == "":
        return WindowsRegistry.Messages.empty_fields.exec()

    if Session.db.account_query.account_exists(new_account_name):
        return WindowsRegistry.Messages.account_already_exists.exec()

    Session.db.account_query.rename_account(new_account_name)

    Session.config.account_name = new_account_name
    Session.config.update_user_config()
    clear_accounts_layout()
    load_accounts()

    WindowsRegistry.RenameAccountWindow.done(1)
    logger.info(f"Account renamed to {new_account_name}")