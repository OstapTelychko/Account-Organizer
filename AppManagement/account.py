from sys import exit
from functools import partial

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from languages import LanguageStructure

from GUI.gui_constants import ALIGN_V_CENTER

from AppManagement.balance import load_account_balance
from AppManagement.category import remove_categories_from_list, load_categories, activate_categories
from AppManagement.language import change_language_during_add_account, change_language



logger = get_logger(__name__)

def show_add_user_window() -> None:
    """Show add user window. First window if db doesn't contain any account."""

    change_language_during_add_account(AppCore.instance().config.language)
    WindowsRegistry.AddAccountWindow.exec()


def add_account() -> int:
    """Add account to database. If account already exists, show warning message."""

    app_core = AppCore.instance()
    account_name = WindowsRegistry.AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return WindowsRegistry.Messages.empty_fields.exec()
        
    if app_core.db.account_query.account_exists(account_name):
        WindowsRegistry.Messages.account_already_exists.setText(LanguageStructure.Messages.get_translation(1))
        return WindowsRegistry.Messages.account_already_exists.exec()

    raw_balance = WindowsRegistry.AddAccountWindow.current_balance.text()

    def _complete_adding_account() -> None:
        """
        Complete adding account. Close add account window, update user config, load accounts and load account data.
        Created to avoid code duplication.
        """

        WindowsRegistry.AddAccountWindow.done(1)

        app_core.config.account_name = account_name
        app_core.config.update_user_config()
        clear_accounts_layout()

        load_accounts()
        load_account_data(app_core.config.account_name)
        change_language()
        logger.info(f"Account {account_name} added")  

    if raw_balance != "":
        if not raw_balance.replace(",","").replace(".","").isdigit():
            return 0
        
        if "." in raw_balance:
            balance = float(raw_balance)
        elif "," in raw_balance:#if balance contains "," for example: 4,5 will be 4.5 
            balance = float(".".join(raw_balance.split(",")))
        else:
            balance = int(raw_balance)

        app_core.db.create_account(account_name, balance)
        _complete_adding_account()    
    else:
        WindowsRegistry.Messages.zero_current_balance.setText(LanguageStructure.Messages.get_translation(2))

        WindowsRegistry.Messages.zero_current_balance.exec()
        if WindowsRegistry.Messages.zero_current_balance.clickedButton() == WindowsRegistry.Messages.zero_current_balance.ok_button:
            app_core.db.create_account(account_name, 0)
            _complete_adding_account()
    
    return 1


def load_account_data(name:str) -> None:
    """Load account data. Load categories, set account name and balance."""

    app_core = AppCore.instance()
    #Remove loaded categories
    remove_categories_from_list()

    app_core.config.account_name = name
    app_core.db.set_account_id(app_core.config.account_name)
    WindowsRegistry.SettingsWindow.account_created_date.setText(
        LanguageStructure.Settings.get_translation(1) 
        + str(app_core.db.account_query.get_account().created_date.strftime("%Y-%m-%d %H:%M:%S"))
    )    
    
    app_core.config.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()
    logger.info(f"Account {name} data loaded")


def load_accounts() -> None:
    """Load accounts from database. Clear account switch widgets and load all accounts."""

    app_core = AppCore.instance()
    app_core.accounts_list = app_core.db.account_query.get_all_accounts()

    for account in app_core.accounts_list:
        account_switch_widget = WindowsRegistry.SwitchAccountWindow.AccountSwitchWidget()
        account_switch_widget.account_name_label.setText(account.name)
        account_switch_widget.account_balance_label.setText(
            LanguageStructure.MainWindow.get_translation(0) + str(account.current_balance))
        account_switch_widget.account_creation_date_label.setText(
            LanguageStructure.Settings.get_translation(1) + account.created_date.strftime("%Y-%m-%d %H:%M:%S")
        )

        account_switch_widget.switch_button.clicked.connect(partial(switch_account, account.name))
        account_switch_widget.switch_button.setText(LanguageStructure.GeneralManagement.get_translation(8))
        if account.name == app_core.config.account_name:
            account_switch_widget.switch_button.setDisabled(True)

        WindowsRegistry.SwitchAccountWindow.accounts_layout.addWidget(account_switch_widget.account_widget, alignment=ALIGN_V_CENTER)
        WindowsRegistry.SwitchAccountWindow.account_switch_widgets.append(account_switch_widget)
 

def clear_accounts_layout() -> None:
    """Clear account switch widgets. Remove all widgets from layout and clear account switch widgets list."""

    WindowsRegistry.SwitchAccountWindow.account_switch_widgets.clear()
    while WindowsRegistry.SwitchAccountWindow.accounts_layout.count() > 0:
        widget = WindowsRegistry.SwitchAccountWindow.accounts_layout.itemAt(0).widget()
        if widget:
            widget.setParent(None) #type: ignore[call-overload] #Mypy doesn't understand that setParent can be None


def switch_account(name:str) -> None:
    """
        Switch account. Show warning message and load account data.
        Disable switch button for current account and enable for other accounts.

        Arguments
        ---------
            `name` : (str) - Account name to switch to.
    """

    WindowsRegistry.Messages.load_account_question.setText(
        LanguageStructure.Messages.get_translation(10).replace("%account%", name))
    WindowsRegistry.Messages.load_account_question.exec()

    if WindowsRegistry.Messages.load_account_question.clickedButton() == WindowsRegistry.Messages.load_account_question.ok_button:
        for widget in WindowsRegistry.SwitchAccountWindow.account_switch_widgets:
            if widget.account_name_label.text() == name:
                widget.switch_button.setDisabled(True)
            else:
                widget.switch_button.setDisabled(False)
        load_account_data(name)
        logger.info(f"Account switched to {name}")
    


def remove_account() -> None:
    """Remove account. Show warning message and remove account from database. If last account is removed, close app."""

    app_core = AppCore.instance()
    WindowsRegistry.Messages.delete_account_warning.setText(
        LanguageStructure.Messages.get_translation(11).replace("%account%", app_core.config.account_name))
    WindowsRegistry.Messages.delete_account_warning.exec()

    if WindowsRegistry.Messages.delete_account_warning.clickedButton() == WindowsRegistry.Messages.delete_account_warning.ok_button:
        app_core.db.account_query.delete_account()
        clear_accounts_layout()
        load_accounts()

        if len(app_core.accounts_list) != 0:
            next_name = app_core.accounts_list[0].name
            for widget in WindowsRegistry.SwitchAccountWindow.account_switch_widgets:
                if widget.account_name_label.text() == next_name:
                    widget.switch_button.setDisabled(True)

            load_account_data(next_name)
            logger.info(f"Account {app_core.config.account_name} removed")
        else:#Close app if db is empty
            app_core.config.update_user_config()
            logger.info("Last account removed. Closing app")
            exit()


def show_rename_account_window() -> None:
    """Show rename account window. Set current account name to line edit."""

    WindowsRegistry.RenameAccountWindow.new_account_name.setText(AppCore.instance().config.account_name)
    WindowsRegistry.RenameAccountWindow.exec()


def rename_account() -> int:
    """Rename account. Show warning message and rename account in database. If account already exists, show warning message."""
    
    app_core = AppCore.instance()
    new_account_name = WindowsRegistry.RenameAccountWindow.new_account_name.text().strip()

    if new_account_name == "":
        return WindowsRegistry.Messages.empty_fields.exec()

    if app_core.db.account_query.account_exists(new_account_name):
        return WindowsRegistry.Messages.account_already_exists.exec()

    app_core.db.account_query.rename_account(new_account_name)

    app_core.config.account_name = new_account_name
    app_core.config.update_user_config()
    clear_accounts_layout()
    load_accounts()

    WindowsRegistry.RenameAccountWindow.done(1)
    logger.info(f"Account renamed to {new_account_name}")
    return 1