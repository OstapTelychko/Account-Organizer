#!/usr/bin/env python3
from sys import exit

from project_configuration import FORBIDDEN_CALCULATOR_WORDS
from languages import LANGUAGES
from backend.db_controller import DBController
from AppObjects.session import Session


from GUI.windows.main import app, MainWindow, SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, RenameCategoryWindow, ChangeCategoryPositionWindow
from GUI.windows.errors import Errors
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatistics, CustomRangeStatisticsView
from GUI.windows.transaction import TransactionManagementWindow
from GUI.theme import swith_theme, load_theme

from Statistics.statistics import show_monthly_statistics, show_quarterly_statistics, show_yearly_statistics, show_custom_range_statistics_window, show_custom_range_statistics_view
from Statistics.copy_statistics import  copy_monthly_transactions, copy_monthly_statistics, copy_quarterly_statistics, copy_yearly_statistics, copy_custom_range_statistics, copy_custom_range_transactions

from AppManagement.language import load_language, change_language_add_account
from AppManagement.balance import load_account_balance
from AppManagement.category import create_category, load_categories, remove_category, rename_category,  activate_categories, show_change_category_position, change_category_position
from AppManagement.transaction import transaction_data_handler
from AppManagement.date import next_month, previous_month, next_year, previous_year
from AppManagement.account import show_add_user_window, add_user, switch_account, remove_account, show_rename_account_window, rename_account 






def calculate_expression():
    expression = MainWindow.mini_calculator_text.text()

    if expression != "":
        if not any([word in expression for word in FORBIDDEN_CALCULATOR_WORDS]):
            try:
                result = str(eval(expression))
            except ZeroDivisionError:
                result = LANGUAGES[Session.language]["Mini calculator"][1]
            except SyntaxError:
                result = LANGUAGES[Session.language]["Mini calculator"][2]
            except Exception as ex:
                result = str(ex)
            MainWindow.mini_calculator_text.setText(result)
        else:
            Errors.forbidden_calculator_word.exec()
    else:
        Errors.empty_expression.exec()


def main():
    Session.start_session()

    load_theme()

    #Set current month and year
    MainWindow.current_year.setText(str(Session.current_year))
    MainWindow.current_month.setText(LANGUAGES[Session.language]["Months"][Session.current_month])

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
    StatisticsWindow.custom_range_statistics.clicked.connect(show_custom_range_statistics_window)
    MonthlyStatistics.copy_statistics.clicked.connect(copy_monthly_statistics)
    QuarterlyStatistics.copy_statistics.clicked.connect(copy_quarterly_statistics)
    YearlyStatistics.copy_statistics.clicked.connect(copy_yearly_statistics)
    CustomRangeStatistics.show_statistics.clicked.connect(show_custom_range_statistics_view)
    CustomRangeStatisticsView.copy_statistics.clicked.connect(copy_custom_range_statistics)
    CustomRangeStatisticsView.copy_transactions.clicked.connect(copy_custom_range_transactions)
    
    #Category settings
    CategorySettingsWindow.delete_category.clicked.connect(remove_category)
    CategorySettingsWindow.rename_category.clicked.connect(lambda: (RenameCategoryWindow.window.setWindowTitle(CategorySettingsWindow.window.windowTitle()), RenameCategoryWindow.window.exec()))
    CategorySettingsWindow.change_category_position.clicked.connect(lambda: show_change_category_position(CategorySettingsWindow.window.windowTitle()))
    CategorySettingsWindow.copy_transactions.clicked.connect(copy_monthly_transactions)
    RenameCategoryWindow.button.clicked.connect(rename_category)
    ChangeCategoryPositionWindow.enter_new_position.clicked.connect(change_category_position)
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
    if not DBController(Session.account_name).account_exists(Session.account_name):
        show_add_user_window()
        if not Session.db:
            exit() 
    Session.db = DBController(Session.account_name)
    Session.db.set_account_id()
    

    #Load categories if they exists
    if len(Session.db.get_all_categories()) > 0:
        load_categories()
    activate_categories()

    #Add accounts to list
    [Session.accounts_list.append(account.name) for account in Session.db.get_all_accounts() if account.name not in Session.accounts_list]

    SettingsWindow.accounts.clear()
    SettingsWindow.accounts.addItems(Session.accounts_list)
    SettingsWindow.accounts.setCurrentText(Session.account_name)


    #Account management
    SettingsWindow.accounts.currentTextChanged.connect(switch_account)
    SettingsWindow.delete_account.clicked.connect(remove_account)
    RenameAccountWindow.button.clicked.connect(rename_account)

    load_account_balance()
    load_language(Session.language)

    MainWindow.window.show()
    app.exec()


if __name__ == "__main__":
    main()    