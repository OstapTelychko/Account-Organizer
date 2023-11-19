from Session import Session
from Account import Account
from languages import LANGUAGES
from GUI import QMessageBox, AddAccountWindow, RenameAccountWindow, SettingsWindow, Errors

from AppManagement.balance import load_account_balance
from AppManagement.category import load_categories, activate_categories
from AppManagement.language import change_language_add_account, change_language

from sys import exit


def show_add_user_window():
    change_language_add_account(Session.language)
    AddAccountWindow.window.exec()


def add_user():
    account_name = AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return Errors.empty_fields_error.exec()
    
    account = Account(account_name)
    
    if account.account_exists(account_name):
        Errors.account_alredy_exists_error.setText(LANGUAGES[Session.language]["Errors"][1])
        return Errors.account_alredy_exists_error.exec()

    balance = AddAccountWindow.current_balance.text()

    def complete_adding_account():
        AddAccountWindow.window.hide()

        Session.account_name = account_name
        Session.account = account
        Session.update_user_config()

        SettingsWindow.accounts.addItem(account_name)
        Session.accounts_list.append(Session.account_name)
        Session.switch_account = False
        load_account_data(Session.account_name)
        SettingsWindow.accounts.setCurrentText(Session.account_name)
        change_language()     

    if balance != "":
        if balance.replace(",","").replace(".","").isdigit():

            if balance.find("."):
                balance = float(balance)
            elif balance.find(","):#if balance contains "," for example: 4,5 will be 4.5 
                balance = float(".".join(balance.split(",")))
            else:
                balance = int(balance)

            account.create_account(balance)
            complete_adding_account()    
    else:
        Errors.zero_current_balance_error.setText(LANGUAGES[Session.language]["Errors"][2])
        if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
            account.create_account(0)
            complete_adding_account()


def load_account_data(name:str):
    #Remove loaded categories
    for category in Session.categories.copy():
        Session.categories[category]["Category window"].deleteLater()
        Session.categories[category]["Settings"].deleteLater()
        Session.categories[category]["Add transaction"].deleteLater()
        Session.categories[category]["Edit transaction"].deleteLater()
        Session.categories[category]["Delete transaction"].deleteLater()
        del Session.categories[category]

    Session.account_name = name
    Session.account = Account(Session.account_name)
    Session.account.set_account_id()
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.language]["Account"]["Info"][9] + Session.account.get_account_date())    

    Session.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()


def switch_account(name:str):
    if Session.switch_account:
        Errors.load_account_question.setText(LANGUAGES[Session.language]["Errors"][10].replace("account", name))

        if Errors.load_account_question.exec() == QMessageBox.StandardButton.Ok:
            load_account_data(name)
        else:
            Session.switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.account_name)
    else:
        Session.switch_account = True


def remove_account():
    Errors.delete_account_warning.setText(LANGUAGES[Session.language]["Errors"][11].replace("account", Session.account_name))

    if Errors.delete_account_warning.exec() == QMessageBox.StandardButton.Ok:
        Session.account.delete_account()
        Session.switch_account = False
        SettingsWindow.accounts.removeItem(Session.accounts_list.index(Session.account_name))
        Session.accounts_list.remove(Session.account_name)

        if len(Session.accounts_list) != 0:
            load_account_data(Session.accounts_list[0])
            Session.switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.accounts_list[0])
        else:#Close app if db is empty
            Session.update_user_config()
            exit()


def show_rename_account_window():
    account_name = SettingsWindow.accounts.currentText().split(" ")
    RenameAccountWindow.new_name.setText(account_name[0])
    RenameAccountWindow.new_surname.setText(account_name[1])
    RenameAccountWindow.window.exec()


def rename_account():
    new_account_name = RenameAccountWindow.new_account_name.text().strip()

    if new_account_name == "":
        return Errors.empty_fields_error.exec()

    if Session.account.account_exists(new_account_name):
        return Errors.account_alredy_exists_error.exec()

    Session.account.rename_account(new_account_name)

    Session.accounts_list[Session.accounts_list.index(Account_name)] = new_account_name
    Account_name = new_account_name
    Session.update_user_config()

    Session.switch_account = False
    SettingsWindow.accounts.clear()

    Session.switch_account = False
    SettingsWindow.accounts.addItems(Session.accounts_list)

    Session.switch_account = False
    SettingsWindow.accounts.setCurrentText(Session.account_name)

    RenameAccountWindow.window.hide()