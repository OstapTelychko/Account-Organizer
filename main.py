""""
MIT License with Non-Monetization Clause

Copyright (c) 2024 - present Ostap Telychko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

2. The Software and any modifications thereof shall not be sold, licensed for a fee,
or monetized in any way. Commercial use is permitted only if the Software remains
freely available to end users.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

from sys import exit
from argparse import ArgumentParser
from functools import partial

from project_configuration import FORBIDDEN_CALCULATOR_WORDS
from languages import LANGUAGES
from backend.db_controller import DBController
from AppObjects.session import Session

from GUI.gui_constants import app
from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, RenameCategoryWindow, ChangeCategoryPositionWindow
from GUI.windows.messages import Messages
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatistics, CustomRangeStatisticsView
from GUI.windows.transaction import TransactionManagementWindow
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.theme import swith_theme, load_theme

from Statistics.statistics import show_monthly_statistics, show_quarterly_statistics, show_yearly_statistics, show_custom_range_statistics_window, show_custom_range_statistics_view
from Statistics.copy_statistics import  copy_monthly_transactions, copy_monthly_statistics, copy_quarterly_statistics, copy_yearly_statistics, copy_custom_range_statistics, copy_custom_range_transactions

from AppManagement.language import load_language, change_language_during_add_account
from AppManagement.balance import load_account_balance
from AppManagement.category import create_category, load_categories, remove_category, rename_category,  activate_categories, show_change_category_position, change_category_position
from AppManagement.transaction import transaction_data_handler
from AppManagement.date import next_month, previous_month, next_year, previous_year
from AppManagement.account import show_add_user_window, add_user, switch_account, remove_account, show_rename_account_window, rename_account 
from AppManagement.backup_management import load_backups, create_backup, remove_backup, load_backup, open_auto_backup_window, auto_backup, prevent_same_auto_backup_status, save_auto_backup_settings, auto_remove_backups
from AppManagement.update_app import check_for_updates

from tests.init_tests import test_main






def calculate_expression():
    expression = MainWindow.mini_calculator_text.text()

    if expression != "":
        if not any([word in expression for word in FORBIDDEN_CALCULATOR_WORDS]):
            try:
                result = str(eval(expression))
            except ZeroDivisionError:
                result = LANGUAGES[Session.language]["Windows"]["Main"]["Mini calculator"][1]
            except SyntaxError:
                result = LANGUAGES[Session.language]["Windows"]["Main"]["Mini calculator"][2]
            except Exception as ex:
                result = str(ex)
            MainWindow.mini_calculator_text.setText(result)
        else:
            Messages.forbidden_calculator_word.exec()
    else:
        Messages.empty_expression.exec()


def main():
    Session.start_session()

    #Set main window for instance guard
    Session.instance_guard.main_window = MainWindow.window
    # Ensure the server socket is closed when the application exits
    app.aboutToQuit.connect(Session.instance_guard.close_sockets)

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
    SettingsWindow.backup_management.clicked.connect(BackupManagementWindow.window.exec)

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
    AddAccountWindow.languages.currentIndexChanged.connect(change_language_during_add_account)
    #Connect to db
    if not Session.test_mode:
        Session.db = DBController()
        
    if not Session.db.account_exists(Session.account_name):
        show_add_user_window()
        if not Session.db.account_id:
            exit() 
    Session.db.set_account_id(Session.account_name)
    
    #Load backups if they exists
    load_backups()

    if not Session.test_mode or not Session.auto_backup_status == Session.AutoBackupStatus.NO_AUTO_BACKUP:
        auto_backup()
    
    if Session.auto_backup_removal_enabled:
        auto_remove_backups()

    #Backup management
    BackupManagementWindow.create_backup.clicked.connect(create_backup)
    BackupManagementWindow.delete_backup.clicked.connect(remove_backup)
    BackupManagementWindow.load_backup.clicked.connect(load_backup)
    BackupManagementWindow.auto_backup.clicked.connect(open_auto_backup_window)

    AutoBackupWindow.monthly.stateChanged.connect(partial(prevent_same_auto_backup_status, AutoBackupWindow.monthly))
    AutoBackupWindow.weekly.stateChanged.connect(partial(prevent_same_auto_backup_status, AutoBackupWindow.weekly))
    AutoBackupWindow.daily.stateChanged.connect(partial(prevent_same_auto_backup_status, AutoBackupWindow.daily))
    AutoBackupWindow.no_auto_backup.stateChanged.connect(partial(prevent_same_auto_backup_status, AutoBackupWindow.no_auto_backup))
    AutoBackupWindow.save.clicked.connect(save_auto_backup_settings)

    #Load categories if they exists
    if len(Session.db.get_all_categories()) > 0:
        load_categories()
    activate_categories()

    #Add accounts to list
    Session.accounts_list = [account.name for account in Session.db.get_all_accounts()]

    SettingsWindow.accounts.clear()
    SettingsWindow.accounts.addItems(Session.accounts_list)
    SettingsWindow.accounts.setCurrentText(Session.account_name)


    #Account management
    SettingsWindow.accounts.currentTextChanged.connect(switch_account)
    SettingsWindow.delete_account.clicked.connect(remove_account)
    RenameAccountWindow.button.clicked.connect(rename_account)

    load_account_balance()
    load_language(Session.language)
    print(check_for_updates())

    MainWindow.window.show()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--test", action="store_true")

    if parser.parse_args().test:
        test_main(main)
    else:
        main()
        app.exec()