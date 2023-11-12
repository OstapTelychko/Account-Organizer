#!/usr/bin/env python3
from sys import exit

from GUI import *
from Session import Session
from languages import LANGUAGES
from project_configuration import FORBIDDEN_CALCULATOR_WORDS, AVAILABLE_LANGUAGES
from Statistics import show_monthly_statistics,show_quarterly_statistics,show_yearly_statistics
from copy_statistics import  copy_monthly_transactions, copy_monthly_statistics, copy_quarterly_statistics, copy_yearly_statistics

from AppManagement.language import load_language, change_language_add_account
from AppManagement.balance import load_account_balance
from AppManagement.category import create_category, load_categories, remove_category, rename_category,  activate_categories
from AppManagement.transaction import transaction_data_handler
from AppManagement.date import next_month, previous_month, next_year, previous_year
from AppManagement.account import show_add_user_window, add_user, switch_account, remove_account, show_rename_account_window, rename_account 



def swith_theme():
    if Session.Theme == "Dark":
        app.setStyleSheet(LIGHT_THEME)
        SettingsWindow.switch_themes_button.setIcon(LIGHT_THEME_ICON)

        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(200,200,200);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")
        if len(Session.Categories) != 0:
            for category in Session.Categories:
                Session.Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(205,205,205)}")
        Session.Theme = "Light"

    elif Session.Theme == "Light":
        app.setStyleSheet(DARK_THEME)
        SettingsWindow.switch_themes_button.setIcon(DARK_THEME_ICON)

        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(40,40,40);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")
        if len(Session.Categories) != 0:
            for category in Session.Categories:
                Session.Categories[category]["Category data"].setStyleSheet("QTableWidget{background-color:rgb(45,45,45)}")
        Session.Theme = "Dark"

    Session.update_user_config()


def calculate_expression():
    expression = MainWindow.mini_calculator_text.text()

    if expression != "":
        if not any([word in expression for word in FORBIDDEN_CALCULATOR_WORDS]):
            try:
                result = str(eval(expression))
            except ZeroDivisionError:
                result = LANGUAGES[Session.Language]["Mini calculator"][1]
            except SyntaxError:
                result = LANGUAGES[Session.Language]["Mini calculator"][2]
            except Exception as ex:
                result = str(ex)
            MainWindow.mini_calculator_text.setText(result)
        else:
            Errors.forbidden_calculator_word_error.exec()
    else:
        Errors.empty_expression_error.exec()



if __name__ == "__main__":
    Session.start_session()

    #Set selected theme
    if Session.Theme == "Dark":
        app.setStyleSheet(DARK_THEME)
        SettingsWindow.switch_themes_button.setIcon(DARK_THEME_ICON)
        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(40,40,40);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")
    if Session.Theme == "Light":
        app.setStyleSheet(LIGHT_THEME)
        SettingsWindow.switch_themes_button.setIcon(LIGHT_THEME_ICON)
        InformationMessage.message.setStyleSheet("QWidget{background-color:rgb(200, 200, 200);border-top-left-radius:15px;border-bottom-left-radius:15px;border-top-right-radius:15px;border-bottom-right-radius:15px;}")


    #Set current month and year
    MainWindow.current_year.setText(str(Session.Current_year))
    MainWindow.current_month.setText(LANGUAGES[Session.Language]["Months"][Session.Current_month])

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
    MainWindow.statistics.clicked.connect(StatisticsWindow.window.exec)
    StatisticsWindow.monthly_statistics.clicked.connect(show_monthly_statistics)
    StatisticsWindow.quarterly_statistics.clicked.connect(show_quarterly_statistics)
    StatisticsWindow.yearly_statistics.clicked.connect(show_yearly_statistics)
    MonthlyStatistics.copy_statistics.clicked.connect(copy_monthly_statistics)
    QuarterlyStatistics.copy_statistics.clicked.connect(copy_quarterly_statistics)
    YearlyStatistics.copy_statistics.clicked.connect(copy_yearly_statistics)
    
    #Category settings
    CategorySettingsWindow.delete_category.clicked.connect(remove_category)
    CategorySettingsWindow.rename_category.clicked.connect(lambda: (RenameCategoryWindow.window.setWindowTitle(CategorySettingsWindow.window.windowTitle()), RenameCategoryWindow.window.exec()))
    CategorySettingsWindow.copy_transactions.clicked.connect(copy_monthly_transactions)
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


    #Create new account if it doesn't exist
    AddAccountWindow.button.clicked.connect(add_user)
    AddAccountWindow.languages.currentIndexChanged.connect(change_language_add_account)
    #Connect to db
    if not Account(Session.Account_name).account_exists(Session.Account_name):
        show_add_user_window()
        if not Session.account:
            exit() 
    Session.account = Account(Session.Account_name)
    Session.account.set_account_id()
    

    #Load categories if they exists
    if len(Session.account.get_all_categories()) > 0:
        load_categories()
    activate_categories()

    #Add accounts to list
    [Session.Accounts_list.append(item[0]) for item in Session.account.get_all_accounts() if item[0] not in Session.Accounts_list]

    SettingsWindow.accounts.clear()
    SettingsWindow.accounts.addItems(Session.Accounts_list)
    SettingsWindow.accounts.setCurrentText(Session.Account_name)


    #Account management
    SettingsWindow.accounts.currentTextChanged.connect(switch_account)
    SettingsWindow.delete_account.clicked.connect(remove_account)
    RenameAccountWindow.button.clicked.connect(rename_account)

    load_account_balance()
    load_language(Session.Language)

    MainWindow.window.show()
    app.exec()