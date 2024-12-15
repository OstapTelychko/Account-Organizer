from sys import exit
from PySide6.QtWidgets import QMessageBox

from AppObjects.session import Session
from backend.db_controller import DBController
from languages import LANGUAGES

from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.messages import Messages

from AppManagement.balance import load_account_balance
from AppManagement.category import remove_categories_from_list, load_categories, activate_categories
from AppManagement.language import change_language_add_account, change_language



def show_add_user_window():
    change_language_add_account(Session.language)
    AddAccountWindow.window.exec()


def add_user():
    account_name = AddAccountWindow.account_name.text().strip()

    if account_name == "":
        return Messages.empty_fields.exec()
    
    db = DBController(account_name)
    
    if db.account_exists(account_name):
        Messages.account_alredy_exists.setText(LANGUAGES[Session.language]["Errors"][1])
        return Messages.account_alredy_exists.exec()

    balance = AddAccountWindow.current_balance.text()

    def complete_adding_account():
        AddAccountWindow.window.hide()

        Session.account_name = account_name
        Session.db = db
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

            db.create_account(balance)
            complete_adding_account()    
    else:
        Messages.zero_current_balance.setText(LANGUAGES[Session.language]["Errors"][2])

        Messages.zero_current_balance.exec()
        if Messages.zero_current_balance.clickedButton() == Messages.zero_current_balance.ok_button:
            db.create_account(0)
            complete_adding_account()


def load_account_data(name:str):
    #Remove loaded categories
    remove_categories_from_list()

    Session.account_name = name
    Session.db = DBController(Session.account_name)
    Session.db.set_account_id()
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.language]["Account"]["Info"][9] + str(Session.db.get_account().created_date))    
    
    Session.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()


def switch_account(name:str):
    if Session.switch_account:
        Messages.load_account_question.setText(LANGUAGES[Session.language]["Errors"][10].replace("account", name))

        Messages.load_account_question.exec()
        if Messages.load_account_question.clickedButton() == Messages.load_account_question.ok_button:
            load_account_data(name)
        else:
            Session.switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.account_name)
    else:
        Session.switch_account = True


def remove_account():
    Messages.delete_account_warning.setText(LANGUAGES[Session.language]["Errors"][11].replace("account", Session.account_name))

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
        else:#Close app if db is empty
            Session.update_user_config()
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