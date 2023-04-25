from GUI import *
from Languages import LANGUAGES
from Accont_mangment import Account
from datetime import datetime
import toml


Current_balance = 0
Current_month = datetime.now().month
Current_year = datetime.now().year
Accounts_list = []

def update_config():
    with open("./configuration.toml","w",encoding="utf-8") as file:
        toml.dump(Configuration,file)


def swith_theme():
    global Configuration
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(light_theme)
        Settings_window.switch_themes_button.setIcon(light_theme_icon)
        Configuration.update({"Theme" : "Light"})
    elif Configuration["Theme"] == "Light":
        app.setStyleSheet(dark_theme)
        Settings_window.switch_themes_button.setIcon(dark_theme_icon)
        Configuration.update({"Theme" : "Dark"})
    update_config()

def change_language(language):
    global Configuration,Language

    if type(language) is int:
        language = [*LANGUAGES.keys()][language]
        Configuration["Language"] = language
        Language = language
    else:
        Configuration["Language"] = language
        Language = language
    update_config()

    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    Main_window.Income_and_expenses.setTabText(0,LANGUAGES[Language]["Account"]["Info"][4])

    Settings_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][0])
    Settings_window.delete_account.setText(LANGUAGES[Language]["Account"]["Account management"][0])
    Settings_window.add_account.setText(LANGUAGES[Language]["Account"]["Account management"][1])
    Settings_window.rename_account.setText(LANGUAGES[Language]["Account"]["Account management"][2])

    Add_accoount_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][1])
    Add_accoount_window.name.setPlaceholderText(LANGUAGES[Language]["Account"][0])
    Add_accoount_window.surname.setPlaceholderText(LANGUAGES[Language]["Account"][1])

    Errors.incorrect_data_type_error.setText(LANGUAGES[Language]["Errors"][0])
    Errors.account_alredy_exists_error.setText(LANGUAGES[Language]["Errors"][1])
    Errors.zero_current_balance_error.setText(LANGUAGES[Language]["Errors"][2])

def next_month():
    global Current_month

    if Current_month != 12:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month+1])
        Current_month +=1
    else:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][1])
        Current_month = 1


def previous_month():
    global Current_month

    Current_month -= 1
    if Current_month != 0:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    else:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][12])
        Current_month = 12


def next_year():
    global Current_year

    Current_year += 1
    Main_window.current_year.setText(str(Current_year))


def previous_year():
    global Current_year

    Current_year -= 1
    Main_window.current_year.setText(str(Current_year))


def show_add_user_window():
    Add_accoount_window.message.setText(LANGUAGES[Language]["Account"]["Account management"]["Messages"][0])
    Add_accoount_window.button.setText(LANGUAGES[Language]["General management"][1])
    Add_accoount_window.window.exec()


def add_user():
    global Current_balance

    name = Add_accoount_window.name.text()
    surname = Add_accoount_window.surname.text()

    if name.isalpha() and surname.isalpha():
        account  = Account("./Accounts.sqlite",name+" "+surname)
        if not account.account_exists():
            balance = Add_accoount_window.current_balance.text()
            if balance != "":
                if balance.isdigit():
                    account.create_account(int(balance))
                    Current_balance = int(balance)
                    Add_accoount_window.window.hide()
            else:
                if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
                    account.create_account(0)
                    Current_balance = 0
                    Add_accoount_window.window.hide()
        else:
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.incorrect_data_type_error.exec()


if __name__ == "__main__":
    with open("./configuration.toml") as file:
        Configuration = toml.load("./configuration.toml")
    #Load selected language 
    Language = Configuration["Language"]
    change_language(Language)
    Settings_window.languages.setCurrentIndex([*LANGUAGES.keys()].index(Language))

    #Set selected theme
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(dark_theme)
        Settings_window.switch_themes_button.setIcon(dark_theme_icon)
    if Configuration["Theme"] == "Light":
        app.setStyleSheet(light_theme)
        Settings_window.switch_themes_button.setIcon(light_theme_icon)

    #Set current month and year
    Main_window.current_year.setText(str(Current_year))
    Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])

    #Connect buttons to functions
    Main_window.settings.clicked.connect(Settings_window.window.exec)
    Settings_window.switch_themes_button.clicked.connect(swith_theme)
    Settings_window.languages.currentIndexChanged.connect(change_language)
    Settings_window.add_account.clicked.connect(show_add_user_window)

    Add_accoount_window.button.clicked.connect(add_user)
    

    Main_window.next_month_button.clicked.connect(next_month)
    Main_window.previous_month_button.clicked.connect(previous_month)
    Main_window.next_year_button.clicked.connect(next_year)
    Main_window.previous_year_button.clicked.connect(previous_year)
    Main_window.window.show()
    app.exec()