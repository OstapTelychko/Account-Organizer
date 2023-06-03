#!/usr/bin/env python3
from GUI import *
from Languages import LANGUAGES,change_language
from Accont_mangment import Account
from Statistics import show_monthly_statistics,show_quarterly_statistics,show_yearly_statistics
from datetime import datetime
import toml
from sys import exit


Current_balance = 0
Current_month = datetime.now().month
Current_year = datetime.now().year

Accounts_list = []
Categories = {}
CATEGORY_TYPE = {0:"Incomes",1:"Expenses"}
FORBIDDEN_CALCULATOR_WORDS = ["import","def","for","while","open","del","__","with","exit","raise","print","range","quit","class","try","if","input","object","global","lambda","match"]

Switch_account = True
MONTHS_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def update_config():
    with open(f"{ROOT_DIRECTORY}/configuration.toml","w",encoding="utf-8") as file:
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


def load_language(language):
    global Language

    if type(language) is int:
        language = [*LANGUAGES.keys()][language]
        Configuration["Language"] = language
        Language = language
    else:
        Configuration["Language"] = language
        Language = language
    update_config()
    change_language(Language,Categories,Current_balance,Current_month,account)


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


def load_categories_data():
    for category in Categories:
        category_data = Categories[category]["Category data"]
        if category_data.rowCount() != 0:#Remove current category transactions if it exist
            for row in range(1,category_data.rowCount()+1):
                category_data.removeRow(row)
        category_data.setRowCount(0)

        transactions = account.get_transactions_by_month(category,Current_year,Current_month)
        total_value = 0
        if len(transactions) != 0:
            category_data.setRowCount(len(transactions))
            for row,transaction in enumerate(transactions):
                day = QTableWidgetItem()
                day.setData(Qt.ItemDataRole.EditRole,transaction[4])
                value = QTableWidgetItem()
                value.setData(Qt.ItemDataRole.EditRole,transaction[5])
                transaction_id = QTableWidgetItem()
                transaction_id.setData(Qt.ItemDataRole.EditRole,transaction[0])

                category_data.setItem(row,0,QTableWidgetItem(transaction[6]))
                category_data.setItem(row,1,day)
                category_data.setItem(row,2,value)
                category_data.setItem(row,3,transaction_id)
                total_value += transaction[5]
        Categories[category]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+str(total_value))


def next_month():
    global Current_month

    if Current_month != 12:
        Current_month +=1
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    else:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][1])
        Current_month = 1
    load_categories_data()


def previous_month():
    global Current_month

    Current_month -= 1
    if Current_month != 0:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    else:
        Main_window.current_month.setText(LANGUAGES[Language]["Months"][12])
        Current_month = 12
    load_categories_data()


def next_year():
    global Current_year

    Current_year += 1
    Main_window.current_year.setText(str(Current_year))
    load_categories_data()


def previous_year():
    global Current_year

    Current_year -= 1
    Main_window.current_year.setText(str(Current_year))
    load_categories_data()


def show_add_user_window():
    Add_account_window.message.setText(LANGUAGES[Language]["Account"]["Account management"]["Messages"][0])
    Add_account_window.button.setText(LANGUAGES[Language]["General management"][1])
    Add_account_window.window.setWindowTitle(LANGUAGES[Language]["Windows"][1])
    Add_account_window.name.setPlaceholderText(LANGUAGES[Language]["Account"][0])
    Add_account_window.surname.setPlaceholderText(LANGUAGES[Language]["Account"][1])
    Add_account_window.current_balance.setPlaceholderText(LANGUAGES[Language]["Account"][2])
    Add_account_window.window.exec()


def add_user():
    global Account_name,Configuration

    name = Add_account_window.name.text().strip()
    surname = Add_account_window.surname.text().strip()

    if name.isalpha() and surname.isalpha():
        full_name = name+" "+surname
        account  = Account(full_name)
        if not account.account_exists(full_name):
            balance = Add_account_window.current_balance.text()
            if balance != "":

                def complete_adding_account():
                    global Switch_account

                    Add_account_window.window.hide()
                    Account_name = full_name
                    Configuration.update({"Account_name":Account_name})
                    update_config()
                    Settings_window.accounts.addItem(full_name)
                    Accounts_list.append(Account_name)
                    Switch_account = False
                    load_account_data(Account_name)
                    Settings_window.accounts.setCurrentText(Account_name)

                if balance.isdigit():
                    account.create_account(int(balance))
                    complete_adding_account()    
            else:
                if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
                    account.create_account(0)
                    complete_adding_account()
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
        activate_categories()
        Add_category_window.category_name.setText("")
        Add_category_window.window.hide()
    else:
        Errors.category_exists_error.exec()


def load_categories():
    global Categories

    for category in account.get_all_categories():
        Categories[category[0]]=load_category(category[1],category[2],account,category[0],Current_year,Current_month,Language,Configuration["Theme"])


def show_category_settings(category_name:str):
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
        Categories[category_id]["Edit transaction"].deleteLater()
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


def update_category_total_value(category_id:int):
    transactions = account.get_transactions_by_month(category_id,Current_year,Current_month)
    total_value = 0

    if len(transactions) != 0:
        for transaction in transactions:
            total_value += transaction[5]
    Categories[category_id]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+str(total_value))
    

def show_edit_transaction_window(category_name:str,category_data:QTableWidget):
    selected_row = category_data.selectedItems()
    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
            Transaction_management_window.button.setText(LANGUAGES[Language]["General management"][5])
            Transaction_management_window.message.setText(LANGUAGES[Language]["Account"]["Transactions management"]["Messages"][0])
            Transaction_management_window.window.setWindowTitle(category_name)
            Transaction_management_window.transaction_name.setText(selected_row[0].text())
            Transaction_management_window.transaction_day.setText(selected_row[1].text())
            Transaction_management_window.transaction_value.setText(selected_row[2].text())
            Transaction_management_window.transaction_id = int(category_data.item(selected_row[0].row(),3).text())
            Transaction_management_window.window.exec()
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def update_transaction(transaction_id:int,transaction_name:str,transaction_day:int,transaction_value:int|float,category_data:QTableWidget):
    account.update_transaction(transaction_id,transaction_name,transaction_day,transaction_value)
                
    for row in range(category_data.rowCount()):
        if int(category_data.item(row,3).text()) == transaction_id:
            category_data.item(row,0).setText(transaction_name)
            category_data.item(row,1).setData(Qt.ItemDataRole.EditRole,transaction_day)
            category_data.item(row,2).setData(Qt.ItemDataRole.EditRole,transaction_value)


def show_add_transaction_window(category_name:str):
    Transaction_management_window.button.setText(LANGUAGES[Language]["General management"][1])
    Transaction_management_window.message.setText(LANGUAGES[Language]["Account"]["Transactions management"]["Messages"][1])
    Transaction_management_window.transaction_name.setText("")
    Transaction_management_window.transaction_day.setText("")
    Transaction_management_window.transaction_value.setText("")

    Transaction_management_window.window.setWindowTitle(category_name)
    Transaction_management_window.window.exec()


def add_transaction(transaction_name:str,transaction_day:int,transaction_value:int|float,category_data:QTableWidget,category_id:int):
    account.add_transaction(category_id,Current_year,Current_month,transaction_day,transaction_value,transaction_name)

    row = category_data.rowCount()
    category_data.setRowCount(row+1)

    day = QTableWidgetItem()
    day.setData(Qt.ItemDataRole.EditRole,transaction_day)
    day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes so items can't be edited

    value = QTableWidgetItem()
    value.setData(Qt.ItemDataRole.EditRole,transaction_value)
    value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    transaction_id = QTableWidgetItem()
    transaction_id.setData(Qt.ItemDataRole.EditRole,account.get_last_transaction_id())
    transaction_id.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    name = QTableWidgetItem(transaction_name)
    name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

    category_data.setItem(row,0,name)
    category_data.setItem(row,1,day)
    category_data.setItem(row,2,value)
    category_data.setItem(row,3,transaction_id)
    Transaction_management_window.window.hide()


def transaction_data_handler():
    transaction_name = Transaction_management_window.transaction_name.text().strip()
    transaction_day = Transaction_management_window.transaction_day.text()
    transaction_value = Transaction_management_window.transaction_value.text()
    transaction_id = Transaction_management_window.transaction_id
    category_id = account.get_category_id(Transaction_management_window.window.windowTitle(),CATEGORY_TYPE[Main_window.Incomes_and_expenses.currentIndex()])
    category_data = Categories[category_id]["Category data"]

    if  transaction_day != "" or transaction_value != "":
        if transaction_value.replace(".","").isdigit() and  transaction_day.isdigit() :
            transaction_day = int(transaction_day)

            max_month_day = MONTHS_DAYS[Current_month-1] + (Current_month == 2 and Current_year % 4 == 0)#Add one day to February (29) if year is leap
            if 0 < transaction_day <= max_month_day:
                if transaction_value.find("."):
                    transaction_value = float(transaction_value)
                else:
                    transaction_value = int(transaction_value)

                if Transaction_management_window.button.text() == LANGUAGES[Language]["General management"][5]: #Update 
                    update_transaction(transaction_id,transaction_name,transaction_day,transaction_value,category_data)
                else: #Add
                    add_transaction(transaction_name,transaction_day,transaction_value,category_data,category_id)

                update_category_total_value(category_id)
                calculate_current_balance()
                Transaction_management_window.window.hide()
            else:
                Errors.day_out_range_error.setText(LANGUAGES[Language]["Errors"][8]+f"1-{max_month_day}")
                Errors.day_out_range_error.exec()
        else:
            Errors.incorrect_data_type_error.exec()
    else:
        Errors.empty_fields_error.exec()


def remove_transaction(category_data:QTableWidget,category_id:int):
    selected_row = category_data.selectedItems()
    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row()  and selected_row[0].row() == selected_row[2].row():
            transaction_id = category_data.item(selected_row[0].row(),3).data(Qt.ItemDataRole.EditRole)
            if Errors.delete_transaction_question.exec() == QMessageBox.StandardButton.Ok:
                account.delete_transaction(transaction_id)

                for row in range(category_data.rowCount()):
                    if category_data.item(row,3).data(Qt.ItemDataRole.EditRole) == transaction_id:
                        category_data.removeRow(row)
                        break

                update_category_total_value(category_id)
                calculate_current_balance()
                row = category_data.verticalHeader()
                row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

                #Without this transactions management buttons work twice (double delete double add double edit)
                Categories[category_id]["Delete transaction"].setDisabled(True)
                Categories[category_id]["Add transaction"].setDisabled(True)
                Categories[category_id]["Edit transaction"].setDisabled(True)
                Categories[category_id]["Delete transaction"].setDisabled(False)
                Categories[category_id]["Add transaction"].setDisabled(False)
                Categories[category_id]["Edit transaction"].setDisabled(False)
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def activate_categories():
    for category in Categories:
        Categories[category]["Settings"].clicked.connect(lambda category_name = Categories[category]["Name"],_=False: show_category_settings(category_name=category_name))
        Categories[category]["Add transaction"].clicked.connect(lambda category_name = Categories[category]["Name"],_=False: show_add_transaction_window(category_name))
        Categories[category]["Edit transaction"].clicked.connect(lambda category_name= Categories[category]["Name"],category_data = Categories[category]["Category data"]:show_edit_transaction_window(category_name=category_name,category_data=category_data))
        Categories[category]["Delete transaction"].clicked.connect(lambda category_data = Categories[category]["Category data"],category_id=category:remove_transaction(category_data,category_id))


def load_account_data(name:str):
    global account, Account_name, Configuration

    #Remove loaded categories
    for category in Categories.copy():
        Categories[category]["Category window"].deleteLater()
        Categories[category]["Settings"].deleteLater()
        Categories[category]["Add transaction"].deleteLater()
        Categories[category]["Edit transaction"].deleteLater()
        Categories[category]["Delete transaction"].deleteLater()
        del Categories[category]

    Account_name = name
    account = Account(Account_name)
    account.set_account_id()
    Settings_window.account_created_date.setText(LANGUAGES[Language]["Account"]["Info"][9]+account.get_account_date())    

    Configuration.update({"Account_name":Account_name})
    update_config()
    load_categories()
    activate_categories()
    calculate_current_balance()


def switch_account(name:str):
    global Switch_account
    if Switch_account:
        Errors.load_account_question.setText(LANGUAGES[Language]["Errors"][10].replace("account",name))
        if Errors.load_account_question.exec() == QMessageBox.StandardButton.Ok:
            load_account_data(name)
        else:
            Switch_account = False
            Settings_window.accounts.setCurrentText(Account_name)
    else:
        Switch_account = True


def remove_account():
    global Accounts_list,Switch_account,Configuration

    Errors.delete_account_warning.setText(LANGUAGES[Language]["Errors"][11].replace("account",Account_name))
    if Errors.delete_account_warning.exec() == QMessageBox.StandardButton.Ok:
        account.delete_account()
        Switch_account = False
        Settings_window.accounts.removeItem(Accounts_list.index(Account_name))
        Accounts_list.remove(Account_name)

        if len(Accounts_list) != 0:
            load_account_data(Accounts_list[0])
            Switch_account = False
            Settings_window.accounts.setCurrentText(Accounts_list[0])
        else:#Close app if db is empty
            Configuration.update({"Account_name":""})
            update_config()
            exit()


def show_rename_account_window():
    full_name = Settings_window.accounts.currentText().split(" ")
    Rename_account_window.new_name.setText(full_name[0])
    Rename_account_window.new_surname.setText(full_name[1])
    Rename_account_window.window.exec()


def rename_account():
    global Account_name,Switch_account,Configuration

    name = Rename_account_window.new_name.text().strip()
    surname = Rename_account_window.new_surname.text().strip()
    if name != " " or surname != "":
        new_name = name+" "+surname
        if not account.account_exists(new_name):
            account.rename_account(Account_name,new_name)

            Accounts_list[Accounts_list.index(Account_name)] = new_name
            Account_name = new_name
            Configuration.update({"Account_name":new_name})
            update_config()

            Switch_account = False
            Settings_window.accounts.clear()
            Switch_account = False
            Settings_window.accounts.addItems(Accounts_list)
            Switch_account = False
            Settings_window.accounts.setCurrentText(Account_name)
            Rename_account_window.window.hide()
        else:
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.empty_fields_error.exec()


def calulate_expression():
    expression = Main_window.mini_calculator_text.text()
    if expression != "":
        if not any([word in expression for word in FORBIDDEN_CALCULATOR_WORDS]):
            try:
                result = str(eval(expression))
            except ZeroDivisionError:
                result = LANGUAGES[Language]["Mini calculator"][1]
            except SyntaxError:
                result = LANGUAGES[Language]["Mini calculator"][2]
            except Exception as ex:
                result = str(ex)
            Main_window.mini_calculator_text.setText(result)
        else:
            Errors.forbidden_calculator_word_error.exec()
    else:
        Errors.empty_expression_error.exec()


if __name__ == "__main__":
    with open(f"{ROOT_DIRECTORY}/configuration.toml") as file:
        Configuration = toml.load(f"{ROOT_DIRECTORY}/configuration.toml")


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
    Settings_window.languages.currentIndexChanged.connect(load_language)
    Settings_window.add_account.clicked.connect(show_add_user_window)
    Settings_window.rename_account.clicked.connect(show_rename_account_window)

    #Activate mini calculator
    Main_window.calculate.clicked.connect(calulate_expression)

    #Statistics
    Main_window.statistics.clicked.connect(Statistcs_window.window.exec)
    Statistcs_window.monthly_statistics.clicked.connect(lambda:show_monthly_statistics(Categories,Language,Current_year,Current_month,account,MONTHS_DAYS))
    Statistcs_window.quarterly_statistics.clicked.connect(lambda:show_quarterly_statistics(Categories,Language,Current_year,account,MONTHS_DAYS))
    Statistcs_window.yearly_statistics.clicked.connect(lambda:show_yearly_statistics(Categories,Language,Current_year,account,MONTHS_DAYS))
    
    #Category settings
    Category_settings_window.delete_category.clicked.connect(remove_category)
    Category_settings_window.rename_category.clicked.connect(lambda: (Rename_category_window.window.setWindowTitle(Category_settings_window.window.windowTitle()),Rename_category_window.window.exec()))
    Rename_category_window.button.clicked.connect(rename_category)
    Transaction_management_window.button.clicked.connect(transaction_data_handler)
    
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
    Add_account_window.button.clicked.connect(add_user)
    if Account_name == "":
        show_add_user_window()
    
    #Connect to db
    account = Account(Account_name)
    account.set_account_id()

    #Load categories if they exists
    if len(account.get_all_categories()) > 0:
        load_categories()
    activate_categories()

    [Accounts_list.append(item[0]) for item in account.get_all_accounts()]
    Settings_window.accounts.addItems(Accounts_list)
    Settings_window.accounts.setCurrentText(Account_name)


    #Account management
    Settings_window.accounts.currentTextChanged.connect(switch_account)
    Settings_window.delete_account.clicked.connect(remove_account)
    Rename_account_window.button.clicked.connect(rename_account)


    calculate_current_balance()
    load_language(Language)

    Main_window.window.show()
    app.exec()