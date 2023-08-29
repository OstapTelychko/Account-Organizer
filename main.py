#!/usr/bin/env python3

from GUI import *
from Languages import LANGUAGES,change_language
from Account_management import Account
from Statistics import show_monthly_statistics,show_quarterly_statistics,show_yearly_statistics
from Project_configuration import ROOT_DIRECTORY, MONTHS_DAYS, FORBIDDEN_CALCULATOR_WORDS, CATEGORY_TYPE
from Copy_statistics import show_information_message, copy_monthly_transactions, copy_monthly_statistics, copy_quarterly_statistics, copy_yearly_statistics

from functools import partial
from datetime import datetime
import toml
from sys import exit


Current_month = datetime.now().month
Current_year = datetime.now().year
Current_balance = 0
Current_total_income = 0
Current_total_expenses = 0
Accounts_list = []
Categories = {}

Switch_account = True


def update_user_config():
    with open(f"{ROOT_DIRECTORY}/User_configuration.toml","w",encoding="utf-8") as file:
        toml.dump(Configuration,file)


def swith_theme():
    global Configuration
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(light_theme)
        SettingsWindow.switch_themes_button.setIcon(light_theme_icon)

        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(200,200,200);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")
        if len(Categories) != 0:
            for category in Categories:
                Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(205,205,205)}")

        Configuration.update({"Theme" : "Light"})
    elif Configuration["Theme"] == "Light":
        app.setStyleSheet(dark_theme)
        SettingsWindow.switch_themes_button.setIcon(dark_theme_icon)

        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(40,40,40);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")
        if len(Categories) != 0:
            for category in Categories:
                Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(45,45,45)}")

        Configuration.update({"Theme" : "Dark"})
    update_user_config()


def load_language(language):
    global Language

    if type(language) is int:
        language = [*LANGUAGES.keys()][language]
        Configuration["Language"] = language
        Language = language
    else:
        Configuration["Language"] = language
        Language = language
    update_user_config()
    change_language(Language,Categories,Current_balance,Current_month,account)


def calculate_current_balance():
    global Current_balance, Current_total_income, Current_total_expenses

    Current_total_income = 0
    Current_total_expenses = 0

    for category in account.get_all_categories():
        if category[1] == "Incomes":
            for transaction in account.get_all_transactions(category[0]):
                Current_total_income += transaction[5]
        elif category[1] == "Expenses":
            for transaction in account.get_all_transactions(category[0]):
                Current_total_expenses += transaction[5]
    
    # If user created account recently with balance not 0 and he don't have transactions yet
    if Current_total_income == 0 and Current_total_expenses == 0 and account.get_account_balance()[0] != 0:
        Current_balance = account.get_account_balance()[0]
    else:
        Current_balance = Current_total_income - Current_total_expenses

    account.update_account_balance(Current_balance,Current_total_income,Current_total_expenses)
    MainWindow.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(round(Current_balance,2)))
    SettingsWindow.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(round(Current_total_income,2)))
    SettingsWindow.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(round(Current_total_expenses,2)))


def load_account_balance():
    global Current_balance, Current_total_income, Current_total_expenses

    Current_balance, Current_total_income, Current_total_expenses = account.get_account_balance()

    if Current_total_income == 0 and Current_total_expenses == 0:
        calculate_current_balance()
    
    
    MainWindow.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(round(Current_balance,2)))
    SettingsWindow.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(round(Current_total_income,2)))
    SettingsWindow.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(round(Current_total_expenses,2)))


def update_account_balance():
    account.update_account_balance(Current_balance,Current_total_income,Current_total_expenses)

    MainWindow.account_current_balance.setText(LANGUAGES[Language]["Account"]["Info"][3]+str(round(Current_balance,2)))
    SettingsWindow.total_income.setText(LANGUAGES[Language]["Account"]["Info"][7]+str(round(Current_total_income,2)))
    SettingsWindow.total_expense.setText(LANGUAGES[Language]["Account"]["Info"][8]+str(round(Current_total_expenses,2)))


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
                name = QTableWidgetItem(transaction[6])
                name.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                day = QTableWidgetItem()
                day.setData(Qt.ItemDataRole.EditRole,transaction[4])
                day.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                value = QTableWidgetItem()
                value.setData(Qt.ItemDataRole.EditRole,transaction[5])
                value.setFlags(~ Qt.ItemFlag.ItemIsEditable)

                transaction_id = QTableWidgetItem()
                transaction_id.setData(Qt.ItemDataRole.EditRole,transaction[0])

                category_data.setItem(row,0,name)
                category_data.setItem(row,1,day)
                category_data.setItem(row,2,value)
                category_data.setItem(row,3,transaction_id)
                total_value += transaction[5]
        Categories[category]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+str(total_value))


def next_month():
    global Current_month

    if Current_month != 12:
        Current_month +=1
        MainWindow.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    else:
        MainWindow.current_month.setText(LANGUAGES[Language]["Months"][1])
        Current_month = 1
    load_categories_data()


def previous_month():
    global Current_month

    Current_month -= 1
    if Current_month != 0:
        MainWindow.current_month.setText(LANGUAGES[Language]["Months"][Current_month])
    else:
        MainWindow.current_month.setText(LANGUAGES[Language]["Months"][12])
        Current_month = 12
    load_categories_data()


def next_year():
    global Current_year

    Current_year += 1
    MainWindow.current_year.setText(str(Current_year))
    load_categories_data()


def previous_year():
    global Current_year

    Current_year -= 1
    MainWindow.current_year.setText(str(Current_year))
    load_categories_data()


def show_add_user_window():
    AddAccountWindow.message.setText(LANGUAGES[Language]["Account"]["Account management"]["Messages"][0])
    AddAccountWindow.button.setText(LANGUAGES[Language]["General management"][1])
    AddAccountWindow.window.setWindowTitle(LANGUAGES[Language]["Windows"][1])
    AddAccountWindow.name.setPlaceholderText(LANGUAGES[Language]["Account"][0])
    AddAccountWindow.surname.setPlaceholderText(LANGUAGES[Language]["Account"][1])
    AddAccountWindow.current_balance.setPlaceholderText(LANGUAGES[Language]["Account"][2])
    AddAccountWindow.window.exec()


def add_user():
    global Account_name,Configuration

    name = AddAccountWindow.name.text().strip()
    surname = AddAccountWindow.surname.text().strip()

    #For expample: Ostap  Telychko (Treatment) is allowed now
    prepared_name = name.replace(" ","").replace("(","").replace(")","")
    prepared_surname = surname.replace(" ","").replace("(","").replace(")","")

    if prepared_name.isalpha() and prepared_surname.isalpha():
        full_name = name+" "+surname
        account  = Account(full_name)
        if not account.account_exists(full_name):
            balance = AddAccountWindow.current_balance.text()

            def complete_adding_account():
                global Switch_account

                AddAccountWindow.window.hide()
                Account_name = full_name
                Configuration.update({"Account_name":Account_name})
                update_user_config()
                SettingsWindow.accounts.addItem(full_name)
                Accounts_list.append(Account_name)
                Switch_account = False
                load_account_data(Account_name)
                SettingsWindow.accounts.setCurrentText(Account_name)

            if balance != "":
                if balance.isdigit():
                    account.create_account(int(balance))
                    complete_adding_account()    
            else:
                Errors.zero_current_balance_error.setText(LANGUAGES[Language]["Errors"][2])
                if Errors.zero_current_balance_error.exec() == QMessageBox.StandardButton.Ok:
                    account.create_account(0)
                    complete_adding_account()
        else:
            Errors.account_alredy_exists_error.setText(LANGUAGES[Language]["Errors"][1])
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.incorrect_data_type_error.setText(LANGUAGES[Language]["Errors"][0])
        Errors.incorrect_data_type_error.exec()


def create_category():
    global Categories

    category_type = "Incomes" if MainWindow.Incomes_and_expenses.currentIndex() == 0 else "Expenses"
    category_name = AddCategoryWindow.category_name.text().strip()

    if category_name != "":
        if not account.category_exists(category_name,category_type):
            account.create_category(category_name,category_type)
            category_id = account.get_category_id(category_name,category_type) 
            Categories[category_id]=load_category(category_type,category_name,account,category_id,Current_year,Current_month,Language,Configuration["Theme"])

            #Activate Category
            Categories[category_id]["Settings"].clicked.connect(partial(show_category_settings,Categories[category_id]["Name"]))
            Categories[category_id]["Add transaction"].clicked.connect(partial(show_add_transaction_window,Categories[category_id]["Name"]))
            Categories[category_id]["Edit transaction"].clicked.connect(partial(show_edit_transaction_window,Categories[category_id]["Name"],Categories[category_id]["Category data"]))
            Categories[category_id]["Delete transaction"].clicked.connect(partial(remove_transaction,Categories[category_id]["Category data"],category_id))

            AddCategoryWindow.category_name.setText("")
            AddCategoryWindow.window.hide()
            show_information_message(LANGUAGES[Language]["Account"]["Category management"][8])
        else:
            Errors.category_exists_error.exec()
    else:
        Errors.no_category_name_error.exec()


def load_categories():
    global Categories

    for category in account.get_all_categories():
        Categories[category[0]]=load_category(category[1],category[2],account,category[0],Current_year,Current_month,Language,Configuration["Theme"])


def show_category_settings(category_name:str):
    if account.category_exists(category_name,CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]):
        CategorySettingsWindow.window.setWindowTitle(category_name)
        CategorySettingsWindow.window.exec()


def remove_category():
    global Categories

    category_name = CategorySettingsWindow.window.windowTitle()

    if Errors.delete_category_question.exec() == QMessageBox.StandardButton.Ok:
        category_id = account.get_category_id(category_name,CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
        account.delete_category(category_id)
        CategorySettingsWindow.window.setWindowTitle(" ")
        CategorySettingsWindow.window.hide()

        Categories[category_id]["Category window"].deleteLater()
        Categories[category_id]["Settings"].deleteLater()
        Categories[category_id]["Add transaction"].deleteLater()
        Categories[category_id]["Edit transaction"].deleteLater()
        Categories[category_id]["Delete transaction"].deleteLater()
        del Categories[category_id]

        calculate_current_balance()
        show_information_message(LANGUAGES[Language]["Account"]["Category management"][7])


def rename_category():
    global Categories

    new_category_name = RenameCategoryWindow.new_category_name.text().strip()
    current_name = RenameCategoryWindow.window.windowTitle()
    category_type = CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]

    if not account.category_exists(new_category_name,category_type):
        for category in Categories:
            if Categories[category]["Name"] == current_name and Categories[category]["Type"] == category_type:
                Categories[category].update({"Name":new_category_name})

                #Update connections
                Categories[category]["Settings"].clicked.disconnect()
                Categories[category]["Add transaction"].clicked.disconnect()
                Categories[category]["Edit transaction"].clicked.disconnect()
                Categories[category]["Settings"].clicked.connect(partial(show_category_settings,new_category_name ))
                Categories[category]["Add transaction"].clicked.connect(partial(show_add_transaction_window,new_category_name))
                Categories[category]["Edit transaction"].clicked.connect(partial(show_edit_transaction_window,new_category_name,Categories[category]["Category data"]))
                Categories[category]["Name label"].setText(new_category_name)

                account.rename_category(category,new_category_name)
                RenameCategoryWindow.window.hide()
                CategorySettingsWindow.window.hide()
                RenameCategoryWindow.new_category_name.setText("")
                show_information_message(LANGUAGES[Language]["Account"]["Category management"][6])
    else:
        Errors.category_exists_error.exec()


def update_category_total_value(category_id:int):
    transactions = account.get_transactions_by_month(category_id,Current_year,Current_month)
    total_value = 0

    if len(transactions) != 0:
        for transaction in transactions:
            total_value += transaction[5]
    Categories[category_id]["Total value"].setText(LANGUAGES[Language]["Account"]["Info"][6]+str(round(total_value, 2)))
    

def show_edit_transaction_window(category_name:str,category_data:QTableWidget):
    selected_row = category_data.selectedItems()
    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[1].row() and selected_row[0].row() == selected_row[2].row():
            TransactionManagementWindow.button.setText(LANGUAGES[Language]["General management"][5])
            TransactionManagementWindow.message.setText(LANGUAGES[Language]["Account"]["Transactions management"]["Messages"][0])
            TransactionManagementWindow.window.setWindowTitle(category_name)
            TransactionManagementWindow.transaction_name.setText(selected_row[0].text())
            TransactionManagementWindow.transaction_day.setText(selected_row[1].text())
            TransactionManagementWindow.transaction_value.setText(selected_row[2].text())
            TransactionManagementWindow.transaction_id = int(category_data.item(selected_row[0].row(),3).text())
            TransactionManagementWindow.window.exec()
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def update_transaction(transaction_id:int,transaction_name:str,transaction_day:int,transaction_value:int|float,category_data:QTableWidget):
    global Current_balance, Current_total_income, Current_total_expenses

    account.update_transaction(transaction_id,transaction_name,transaction_day,transaction_value)
                
    for row in range(category_data.rowCount()):
        if int(category_data.item(row,3).text()) == transaction_id:
            category_data.item(row,0).setText(transaction_name)
            category_data.item(row,1).setData(Qt.ItemDataRole.EditRole,transaction_day)

            old_value = category_data.item(row,2).data(Qt.ItemDataRole.EditRole)
            values_difference = transaction_value - old_value

            if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
                Current_total_income += values_difference
                Current_balance += values_difference
            else:
                Current_total_expenses += values_difference
                Current_balance -=  values_difference
            category_data.item(row,2).setData(Qt.ItemDataRole.EditRole,transaction_value)


def show_add_transaction_window(category_name:str):
    TransactionManagementWindow.button.setText(LANGUAGES[Language]["General management"][1])
    TransactionManagementWindow.message.setText(LANGUAGES[Language]["Account"]["Transactions management"]["Messages"][1])
    TransactionManagementWindow.transaction_name.setText("")
    TransactionManagementWindow.transaction_day.setText("")
    TransactionManagementWindow.transaction_value.setText("")

    TransactionManagementWindow.window.setWindowTitle(category_name)
    TransactionManagementWindow.window.exec()


def add_transaction(transaction_name:str, transaction_day:int, transaction_value:int|float, category_data:QTableWidget, category_id:int):
    global Current_balance, Current_total_income, Current_total_expenses

    account.add_transaction(category_id,Current_year,Current_month,transaction_day,transaction_value,transaction_name)

    if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
        Current_total_income += transaction_value
        Current_balance += transaction_value
    else:
        Current_total_expenses += transaction_value
        Current_balance -= transaction_value

    row = category_data.rowCount()
    category_data.setRowCount(row+1)

    day = QTableWidgetItem()
    day.setData(Qt.ItemDataRole.EditRole,transaction_day)
    day.setFlags(~ Qt.ItemFlag.ItemIsEditable)# symbol ~ mean invert bytes in this case cells in table can't be edited

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
    TransactionManagementWindow.window.hide()


def transaction_data_handler():
    transaction_name = TransactionManagementWindow.transaction_name.text().strip()
    transaction_day = TransactionManagementWindow.transaction_day.text()
    transaction_value = TransactionManagementWindow.transaction_value.text()
    transaction_id = TransactionManagementWindow.transaction_id
    category_id = account.get_category_id(TransactionManagementWindow.window.windowTitle(),CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
    category_data = Categories[category_id]["Category data"]

    if  transaction_day != "" or transaction_value != "":
        if transaction_value.replace(".","").isdigit() and  transaction_day.isdigit():
            transaction_day = int(transaction_day)

            max_month_day = MONTHS_DAYS[Current_month-1] + (Current_month == 2 and Current_year % 4 == 0)#Add one day to February (29) if year is leap
            if 0 < transaction_day <= max_month_day:
                if transaction_value.find("."):
                    transaction_value = float(transaction_value)
                else:
                    transaction_value = int(transaction_value)

                if TransactionManagementWindow.button.text() == LANGUAGES[Language]["General management"][5]: #Update 
                    update_transaction(transaction_id,transaction_name,transaction_day,transaction_value,category_data)
                else: #Add
                    add_transaction(transaction_name,transaction_day,transaction_value,category_data,category_id)

                update_category_total_value(category_id)
                update_account_balance()
                TransactionManagementWindow.window.hide()
            else:
                Errors.day_out_range_error.setText(LANGUAGES[Language]["Errors"][8]+f"1-{max_month_day}")
                Errors.day_out_range_error.exec()
        else:
            Errors.incorrect_data_type_error.exec()
    else:
        Errors.empty_fields_error.exec()


def remove_transaction(category_data:QTableWidget,category_id:int):
    global Current_balance, Current_total_expenses, Current_total_income

    selected_row = category_data.selectedItems()
    if len(selected_row) != 0 and  not len(selected_row) < 3:
        if len(selected_row) == 3 and selected_row[0].row() == selected_row[1].row()  and selected_row[0].row() == selected_row[2].row():
            transaction_id = category_data.item(selected_row[0].row(),3).data(Qt.ItemDataRole.EditRole)
            if Errors.delete_transaction_question.exec() == QMessageBox.StandardButton.Ok:

                transaction_value = selected_row[2].data(Qt.ItemDataRole.EditRole)
                account.delete_transaction(transaction_id)

                for row in range(category_data.rowCount()):
                    if category_data.item(row,3).data(Qt.ItemDataRole.EditRole) == transaction_id:
                        category_data.removeRow(row)
                        break

                update_category_total_value(category_id)
                if CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()] == "Incomes":
                    Current_total_income -= transaction_value
                    Current_balance -= transaction_value
                else:
                    Current_total_expenses -= transaction_value
                    Current_balance += transaction_value
                update_account_balance()

                row = category_data.verticalHeader()
                row.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        else:
            Errors.only_one_row_error.exec()
    else:
        Errors.unselected_row_error.exec()


def activate_categories():
    for category in Categories:
        Categories[category]["Settings"].clicked.connect(partial(show_category_settings,Categories[category]["Name"]))
        Categories[category]["Add transaction"].clicked.connect(partial(show_add_transaction_window,Categories[category]["Name"]))
        Categories[category]["Edit transaction"].clicked.connect(partial(show_edit_transaction_window,Categories[category]["Name"],Categories[category]["Category data"]))
        Categories[category]["Delete transaction"].clicked.connect(partial(remove_transaction,Categories[category]["Category data"],category))


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
    SettingsWindow.account_created_date.setText(LANGUAGES[Language]["Account"]["Info"][9]+account.get_account_date())    

    Configuration.update({"Account_name":Account_name})
    update_user_config()
    load_categories()
    activate_categories()
    load_account_balance()


def switch_account(name:str):
    global Switch_account
    if Switch_account:
        Errors.load_account_question.setText(LANGUAGES[Language]["Errors"][10].replace("account",name))
        if Errors.load_account_question.exec() == QMessageBox.StandardButton.Ok:
            load_account_data(name)
        else:
            Switch_account = False
            SettingsWindow.accounts.setCurrentText(Account_name)
    else:
        Switch_account = True


def remove_account():
    global Accounts_list,Switch_account,Configuration

    Errors.delete_account_warning.setText(LANGUAGES[Language]["Errors"][11].replace("account",Account_name))
    if Errors.delete_account_warning.exec() == QMessageBox.StandardButton.Ok:
        account.delete_account()
        Switch_account = False
        SettingsWindow.accounts.removeItem(Accounts_list.index(Account_name))
        Accounts_list.remove(Account_name)

        if len(Accounts_list) != 0:
            load_account_data(Accounts_list[0])
            Switch_account = False
            SettingsWindow.accounts.setCurrentText(Accounts_list[0])
        else:#Close app if db is empty
            Configuration.update({"Account_name":""})
            update_user_config()
            exit()


def show_rename_account_window():
    full_name = SettingsWindow.accounts.currentText().split(" ")
    RenameAccountWindow.new_name.setText(full_name[0])
    RenameAccountWindow.new_surname.setText(full_name[1])
    RenameAccountWindow.window.exec()


def rename_account():
    global Account_name,Switch_account,Configuration

    name = RenameAccountWindow.new_name.text().strip()
    surname = RenameAccountWindow.new_surname.text().strip()
    if name != " " or surname != "":
        new_name = name+" "+surname
        if not account.account_exists(new_name):
            account.rename_account(new_name)

            Accounts_list[Accounts_list.index(Account_name)] = new_name
            Account_name = new_name
            Configuration.update({"Account_name":new_name})
            update_user_config()

            Switch_account = False
            SettingsWindow.accounts.clear()
            Switch_account = False
            SettingsWindow.accounts.addItems(Accounts_list)
            Switch_account = False
            SettingsWindow.accounts.setCurrentText(Account_name)
            RenameAccountWindow.window.hide()
        else:
            Errors.account_alredy_exists_error.exec()
    else:
        Errors.empty_fields_error.exec()


def calculate_expression():
    expression = MainWindow.mini_calculator_text.text()
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
            MainWindow.mini_calculator_text.setText(result)
        else:
            Errors.forbidden_calculator_word_error.exec()
    else:
        Errors.empty_expression_error.exec()




if __name__ == "__main__":
    with open(f"{ROOT_DIRECTORY}/User_configuration.toml") as file:
        Configuration = toml.load(f"{ROOT_DIRECTORY}/User_configuration.toml")

    #Load selected language 
    Language = Configuration["Language"]
    SettingsWindow.languages.setCurrentIndex([*LANGUAGES.keys()].index(Language))

    #Set selected theme
    if Configuration["Theme"] == "Dark":
        app.setStyleSheet(dark_theme)
        SettingsWindow.switch_themes_button.setIcon(dark_theme_icon)
        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(40,40,40);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")
    if Configuration["Theme"] == "Light":
        app.setStyleSheet(light_theme)
        SettingsWindow.switch_themes_button.setIcon(light_theme_icon)
        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(200, 200, 200);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")


    #Set current month and year
    MainWindow.current_year.setText(str(Current_year))
    MainWindow.current_month.setText(LANGUAGES[Language]["Months"][Current_month])

    #Connect buttons to functions
    #Settings
    MainWindow.settings.clicked.connect(SettingsWindow.window.exec)
    SettingsWindow.switch_themes_button.clicked.connect(swith_theme)
    SettingsWindow.languages.currentIndexChanged.connect(load_language)
    SettingsWindow.add_account.clicked.connect(show_add_user_window)
    SettingsWindow.rename_account.clicked.connect(show_rename_account_window)

    #Activate mini calculator
    MainWindow.calculate.clicked.connect(calculate_expression)

    #Statistics
    MainWindow.statistics.clicked.connect(StatistcsWindow.window.exec)
    StatistcsWindow.monthly_statistics.clicked.connect(lambda:show_monthly_statistics(Categories,Language,Current_year,Current_month,account,MONTHS_DAYS))
    StatistcsWindow.quarterly_statistics.clicked.connect(lambda:show_quarterly_statistics(Categories,Language,Current_year,account,MONTHS_DAYS))
    StatistcsWindow.yearly_statistics.clicked.connect(lambda:show_yearly_statistics(Categories,Language,Current_year,account,MONTHS_DAYS))
    MonthlyStatistics.copy_statistics.clicked.connect(lambda: copy_monthly_statistics(app,Language))
    QuarterlyStatistics.copy_statistics.clicked.connect(lambda: copy_quarterly_statistics(app,Language))
    YearlyStatistics.copy_statistics.clicked.connect(lambda: copy_yearly_statistics(app,Language))
    
    #Category settings
    CategorySettingsWindow.delete_category.clicked.connect(remove_category)
    CategorySettingsWindow.rename_category.clicked.connect(lambda: (RenameCategoryWindow.window.setWindowTitle(CategorySettingsWindow.window.windowTitle()),RenameCategoryWindow.window.exec()))
    CategorySettingsWindow.copy_transactions.clicked.connect(lambda: copy_monthly_transactions(account,Current_month,Current_year,Language,app))
    RenameCategoryWindow.button.clicked.connect(rename_category)
    TransactionManagementWindow.button.clicked.connect(transaction_data_handler)
    
    #Date management
    MainWindow.next_month_button.clicked.connect(next_month)
    MainWindow.previous_month_button.clicked.connect(previous_month)
    MainWindow.next_year_button.clicked.connect(next_year)
    MainWindow.previous_year_button.clicked.connect(previous_year)

    #Add category
    MainWindow.add_incomes_category.clicked.connect(AddCategoryWindow.window.exec)
    MainWindow.add_expenses_category.clicked.connect(AddCategoryWindow.window.exec)
    AddCategoryWindow.button.clicked.connect(create_category)

    #Load last used account name 
    Account_name = Configuration["Account_name"]

    #Create new account if it doesn't exist
    AddAccountWindow.button.clicked.connect(add_user)
    if Account_name == "":
        show_add_user_window()
    if Account_name == "":
        exit()
    
    #Connect to db
    account = Account(Account_name)
    account.set_account_id()

    #Load categories if they exists
    if len(account.get_all_categories()) > 0:
        load_categories()
    activate_categories()

    #Add accounts to list
    [Accounts_list.append(item[0]) for item in account.get_all_accounts() if item[0] not in Accounts_list]

    SettingsWindow.accounts.clear()
    SettingsWindow.accounts.addItems(Accounts_list)
    SettingsWindow.accounts.setCurrentText(Account_name)


    #Account management
    SettingsWindow.accounts.currentTextChanged.connect(switch_account)
    SettingsWindow.delete_account.clicked.connect(remove_account)
    RenameAccountWindow.button.clicked.connect(rename_account)

    load_account_balance()
    load_language(Language)

    MainWindow.window.show()
    app.exec()