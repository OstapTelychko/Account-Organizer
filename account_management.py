from Session import Session
from Account import Account
from languages import LANGUAGES
from GUI import QMessageBox, AddAccountWindow, RenameAccountWindow, SettingsWindow, Errors

from balance_management import load_account_balance
from category_management import load_categories, activate_categories

from sys import exit


def show_add_user_window():
    AddAccountWindow.message.setText(LANGUAGES[Session.Language]["Account"]["Account management"]["Messages"][0])
    AddAccountWindow.button.setText(LANGUAGES[Session.Language]["General management"][1])
    AddAccountWindow.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][1])
    AddAccountWindow.name.setPlaceholderText(LANGUAGES[Session.Language]["Account"][0])
    AddAccountWindow.surname.setPlaceholderText(LANGUAGES[Session.Language]["Account"][1])
    AddAccountWindow.current_balance.setPlaceholderText(LANGUAGES[Session.Language]["Account"][2])
    AddAccountWindow.window.exec()


def add_user():
    name = AddAccountWindow.name.text().strip()
    surname = AddAccountWindow.surname.text().strip()

    #For expample: Ostap  Telychko (Treatment) is allowed now
    prepared_name = name.replace(" ","").replace("(","").replace(")","")
    prepared_surname = surname.replace(" ","").replace("(","").replace(")","")

    if prepared_name.isalpha() and prepared_surname.isalpha():
        full_name = name+" "+surname
        Session.account = Account(full_name)

        if not Session.account.account_exists(full_name):
            balance = AddAccountWindow.current_balance.text()

            def complete_adding_account():
                AddAccountWindow.window.hide()
                Session.Account_name = full_name
                Session.update_user_config()
                SettingsWindow.accounts.addItem(full_name)
                Session.Accounts_list.append(Session.Account_name)
                Session.Switch_account = False
                load_account_data(Session.Account_name)
                SettingsWindow.accounts.setCurrentText(Session.Account_name)

            if balance != "":
                if balance.isdigit():
                    Session.account.create_account(int(balance))
                    complete_adding_account()    
            else:
                Errors.zero_current_balance_error.setText(LANGUAGES[Session.Language]["Errors"][2])
                if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
                    Session.account.create_account(0)
                    complete_adding_account()
        else:
            Errors.account_alredy_exists_error.setText(LANGUAGES[Session.Language]["Errors"][1])
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.incorrect_data_type_error.setText(LANGUAGES[Session.Language]["Errors"][0])
        Errors.incorrect_data_type_error.exec()


def load_account_data(name:str):
    #Remove loaded categories
    for category in Session.Categories.copy():
        Session.Categories[category]["Category window"].deleteLater()
        Session.Categories[category]["Settings"].deleteLater()
        Session.Categories[category]["Add transaction"].deleteLater()
        Session.Categories[category]["Edit transaction"].deleteLater()
        Session.Categories[category]["Delete transaction"].deleteLater()
        del Session.Categories[category]

    Session.Account_name = name
    Session.account = Account(Session.Account_name)
    Session.account.set_account_id()
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.Language]["Account"]["Info"][9] + Session.account.get_account_date())    

    Session.update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()


def switch_account(name:str):
    if Session.Switch_account:
        Errors.load_account_question.setText(LANGUAGES[Session.Language]["Errors"][10].replace("account", name))

        if Errors.load_account_question.exec() == QMessageBox.StandardButton.Ok:
            load_account_data(name)
        else:
            Session.Switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.Account_name)
    else:
        Session.Switch_account = True


def remove_account():
    Errors.delete_account_warning.setText(LANGUAGES[Session.Language]["Errors"][11].replace("account", Session.Account_name))

    if Errors.delete_account_warning.exec() == QMessageBox.StandardButton.Ok:
        Session.account.delete_account()
        Session.Switch_account = False
        SettingsWindow.accounts.removeItem(Session.Accounts_list.index(Session.Account_name))
        Session.Accounts_list.remove(Session.Account_name)

        if len(Session.Accounts_list) != 0:
            load_account_data(Session.Accounts_list[0])
            Session.Switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.Accounts_list[0])
        else:#Close app if db is empty
            Session.update_user_config()
            exit()


def show_rename_account_window():
    full_name = SettingsWindow.accounts.currentText().split(" ")
    RenameAccountWindow.new_name.setText(full_name[0])
    RenameAccountWindow.new_surname.setText(full_name[1])
    RenameAccountWindow.window.exec()


def rename_account():
    name = RenameAccountWindow.new_name.text().strip()
    surname = RenameAccountWindow.new_surname.text().strip()

    if name != " " or surname != "":
        new_name = name+" "+surname
        if not Session.account.account_exists(new_name):
            Session.account.rename_account(new_name)

            Session.Accounts_list[Session.Accounts_list.index(Account_name)] = new_name
            Account_name = new_name
            Session.update_user_config()

            Session.Switch_account = False
            SettingsWindow.accounts.clear()

            Session.Switch_account = False
            SettingsWindow.accounts.addItems(Session.Accounts_list)

            Session.Switch_account = False
            SettingsWindow.accounts.setCurrentText(Session.Account_name)

            RenameAccountWindow.window.hide()
        else:
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.empty_fields_error.exec()