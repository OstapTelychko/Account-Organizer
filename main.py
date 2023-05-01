from GUI import *
from Languages import LANGUAGES
from Accont_mangment import Account
from datetime import datetime
import toml


Current_balance = 0
Current_month = datetime.now().month
Current_year = datetime.now().year

Accounts_list = []
Categories = {}
CATEGORY_TYPE = {0:"Incomes",1:"Expenses"}

def update_config():
    with open("./configuration.toml","w",encoding="utf-8") as file:
        toml.dump(Configuration,file)


def swith_theme():
    global Configuration
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(light_theme)
        Settings_window.switch_themes_button.setIcon(light_theme_icon)

        if len(Categories) != 0:
            for category in Categories:
                Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(205,205,205)}")

        Configuration.update({"Theme" : "Light"})
    elif Configuration["Theme"] == "Light":
        app.setStyleSheet(dark_theme)
        Settings_window.switch_themes_button.setIcon(dark_theme_icon)

        if len(Categories) != 0:
            for category in Categories:
                Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(45,45,45)}")

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
    Main_window.Incomes_and_expenses.setTabText(0,LANGUAGES[Language]["Account"]["Info"][4])
    Main_window.Incomes_and_expenses.setTabText(1,LANGUAGES[Language]["Account"]["Info"][5])
    Main_window.add_incomes_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])
    Main_window.add_expenses_category.setText(LANGUAGES[Language]["Account"]["Category management"][0])

    Settings_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][0])
    Settings_window.delete_account.setText(LANGUAGES[Language]["Account"]["Account management"][0])
    Settings_window.add_account.setText(LANGUAGES[Language]["Account"]["Account management"][1])
    Settings_window.rename_account.setText(LANGUAGES[Language]["Account"]["Account management"][2])

    Add_accoount_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][1])
    Add_accoount_window.name.setPlaceholderText(LANGUAGES[Language]["Account"][0])
    Add_accoount_window.surname.setPlaceholderText(LANGUAGES[Language]["Account"][1])

    Add_category_window.category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Info"][0])
    Add_category_window.button.setText(LANGUAGES[Language]["General management"][1])
    Add_category_window.window.setWindowTitle(LANGUAGES[Language]["Account"]["Category management"][0])

    Category_settings_window.delete_category.setText(LANGUAGES[Language]["Account"]["Category management"][1])
    Category_settings_window.rename_category.setText(LANGUAGES[Language]["Account"]["Category management"][2])
    Category_settings_window.show_statistics.setText(LANGUAGES[Language]["Account"]["Category management"][3])

    Rename_category_window.new_category_name.setPlaceholderText(LANGUAGES[Language]["Account"]["Category management"][4])
    Rename_category_window.button.setText(LANGUAGES[Language]["General management"][2])

    for index,error in enumerate(errors_list):
        error.setText(LANGUAGES[Language]["Errors"][index])
        error.button(QMessageBox.StandardButton.Ok).setText(LANGUAGES[Language]["General management"][3])
        if error.button(QMessageBox.StandardButton.Cancel) != None:
            error.button(QMessageBox.StandardButton.Cancel).setText(LANGUAGES[Language]["General management"][4])
    
    if len(Categories) > 0:
        for category in Categories:
            Categories[category]["Add transaction"].setText(LANGUAGES[Language]["Account"]["Transactions management"][0])
            Categories[category]["Delete transaction"].setText(LANGUAGES[Language]["Account"]["Transactions management"][1])
            Categories[category]["Rename transaction"].setText(LANGUAGES[Language]["Account"]["Transactions management"][2])
            Categories[category]["Columns"]["Name"].setText(LANGUAGES[Language]["Account"]["Info"][0])
            Categories[category]["Columns"]["Date"].setText(LANGUAGES[Language]["Account"]["Info"][1])
            Categories[category]["Columns"]["Value"].setText(LANGUAGES[Language]["Account"]["Info"][2])
            total_value = Categories[category]["Total value"].text().split(" ")[1]
            Categories[category]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+total_value)
    
    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Incomes = Settings_window.total_income.text().split(" ")[2]
    Settings_window.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(Incomes))
    Expenses = Settings_window.total_expense.text().split(" ")[2]
    Settings_window.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(Expenses))
    Settings_window.account_created_date.setText(LANGUAGES[Language]["Account"]["Info"][9]+account.get_account_date())    


def calculate_current_balance():
    global Current_balance

    Incomes = 0
    Expenses = 0

    for category in account.get_all_categories():
        if category[1] == "Incomes":
            for transaction in account.get_all_transactions(category[0]):
                Incomes += transaction[5]
        elif category[1] == "Expenses":
            for transaction in account.get_all_transactions(category[0]):
                Expenses += transaction[5]
    
    Current_balance = Incomes - Expenses
    Main_window.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(Current_balance))
    Settings_window.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(Incomes))
    Settings_window.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(Expenses))


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
    global Account_name,Configuration

    name = Add_accoount_window.name.text().strip()
    surname = Add_accoount_window.surname.text().strip()

    if name.isalpha() and surname.isalpha():
        full_name = name+" "+surname
        account  = Account("./Accounts.sqlite",full_name)
        if not account.account_exists():
            balance = Add_accoount_window.current_balance.text()
            if balance != "":
                if balance.isdigit():
                    account.create_account(int(balance))
                    Add_accoount_window.window.hide()
                    Account_name = full_name
                    Configuration.update({"Account_name":Account_name})
                    update_config()
                    Settings_window.accounts.addItem(full_name)
                    Accounts_list.append(Account_name)
                    Settings_window.accounts.setCurrentText(Account_name)
            else:
                if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
                    account.create_account(0)
                    Add_accoount_window.window.hide()
                    Account_name = full_name
                    Configuration.update({"Account_name":Account_name})
                    update_config()
                    Settings_window.accounts.addItem(full_name)
                    Accounts_list.append(Account_name)
                    Settings_window.accounts.setCurrentText(Account_name)
        else:
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.incorrect_data_type_error.exec()


def create_category():
    global Categories

    category_type = "Incomes" if Main_window.Incomes_and_expenses.currentIndex() == 0 else "Expenses"
    category_name = Add_category_window.category_name.text().strip()

    if not account.category_exists(category_name,category_type):
        account.create_category(category_name,category_type)
        category_id = account.get_category_id(category_name,category_type) 
        Categories[category_id]=load_category(category_type,category_name,account,category_id,Current_year,Current_month,Language,Configuration["Theme"])
        connect_categories_to_settings()
        Add_category_window.window.hide()
    else:
        Errors.category_exists_error.exec()


def load_categories():
    global Categories

    for category in account.get_all_categories():
        Categories[category[0]]=load_category(category[1],category[2],account,category[0],Current_year,Current_month,Language,Configuration["Theme"])


def show_category_settings(category_name:str,useless_variable:bool=False): # I added useless variable to avoid error with Pyside6 which sends False after click on the button
    if account.category_exists(category_name,CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()]):
        Category_settings_window.window.setWindowTitle(category_name)
        Category_settings_window.window.exec()


def remove_category():
    global Categories

    category_name = Category_settings_window.window.windowTitle()

    if Errors.delete_category_question.exec() == QMessageBox.StandardButton.Ok:
        category_id = account.get_category_id(category_name,CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()])
        account.delete_category(category_id)
        Category_settings_window.window.setWindowTitle(" ")
        Category_settings_window.window.hide()

        Categories[category_id]["Category window"].deleteLater()
        Categories[category_id]["Settings"].deleteLater()
        Categories[category_id]["Add transaction"].deleteLater()
        Categories[category_id]["Rename transaction"].deleteLater()
        Categories[category_id]["Delete transaction"].deleteLater()
        del Categories[category_id]

        calculate_current_balance()


def rename_category():
    global Categories

    new_category_name = Rename_category_window.new_category_name.text().strip()
    current_name = Rename_category_window.window.windowTitle()
    category_type = CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()]

    if not account.category_exists(new_category_name,category_type):
        for category in Categories:
            if Categories[category]["Name"] == current_name:
                Categories[category].update({"Name":new_category_name})
                Categories[category]["Settings"].clicked.connect(lambda category_name= new_category_name,useless_variable=False: show_category_settings(category_name=category_name,useless_variable=useless_variable))
                Categories[category]["Name label"].setText(new_category_name)
                account.rename_category(account.get_category_id(current_name,category_type),new_category_name)
                Rename_category_window.window.hide()
                Category_settings_window.window.hide()
    else:
        Errors.category_exists_error.exec()


def add_transaction():
    ...


def connect_categories_to_settings():
    for category in Categories:
        Categories[category]["Settings"].clicked.connect(lambda category_name= Categories[category]["Name"],useless_variable=False: show_category_settings(category_name=category_name,useless_variable=useless_variable))


if __name__ == "__main__":
    with open("./configuration.toml") as file:
        Configuration = toml.load("./configuration.toml")

    #Load selected language 
    Language = Configuration["Language"]
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
    #Settings
    Main_window.settings.clicked.connect(Settings_window.window.exec)
    Settings_window.switch_themes_button.clicked.connect(swith_theme)
    Settings_window.languages.currentIndexChanged.connect(change_language)
    Settings_window.add_account.clicked.connect(show_add_user_window)

    Add_accoount_window.button.clicked.connect(add_user)

    #Category settings
    Category_settings_window.delete_category.clicked.connect(remove_category)
    Category_settings_window.rename_category.clicked.connect(lambda: (Rename_category_window.window.setWindowTitle(Category_settings_window.window.windowTitle()),Rename_category_window.window.exec()))
    Rename_category_window.button.clicked.connect(rename_category)
    
    #Date management
    Main_window.next_month_button.clicked.connect(next_month)
    Main_window.previous_month_button.clicked.connect(previous_month)
    Main_window.next_year_button.clicked.connect(next_year)
    Main_window.previous_year_button.clicked.connect(previous_year)

    #Add category
    Main_window.add_incomes_category.clicked.connect(Add_category_window.window.exec)
    Main_window.add_expenses_category.clicked.connect(Add_category_window.window.exec)
    Add_category_window.button.clicked.connect(create_category)

    #Load last used account name 
    Account_name = Configuration["Account_name"]

    #Create new account if it doesn't exist
    if Account_name == "":
        show_add_user_window()
    
    #Connect to db
    account = Account("./Accounts.sqlite",Account_name)
    account.get_account_id()

    #Load categories if they exists
    if len(account.get_all_categories()) > 0:
        load_categories()
    connect_categories_to_settings()

    [Accounts_list.append(item[0]) for item in account.get_all_accounts()]
    Settings_window.accounts.addItems(Accounts_list)
    Settings_window.accounts.setCurrentText(Account_name)

    calculate_current_balance()
    change_language(Language)

    Main_window.window.show()
    app.exec()