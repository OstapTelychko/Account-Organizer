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

from PySide6.QtCore import QTimer

from project_configuration import FORBIDDEN_CALCULATOR_WORDS
from languages import LanguageStructure
from backend.db_controller import DBController
from AppObjects.session import Session
from AppObjects.logger import get_logger

from GUI.gui_constants import app
from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow, SwitchAccountWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, RenameCategoryWindow, ChangeCategoryPositionWindow
from GUI.windows.messages import Messages
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatistics, CustomRangeStatisticsView
from GUI.windows.transaction import TransactionManagementWindow
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.theme import swith_theme, load_theme

from Statistics.statistics import show_monthly_statistics, show_quarterly_statistics, show_yearly_statistics, show_custom_range_statistics_window, show_custom_range_statistics_view, add_all_categories_to_statistics_list, remove_all_categories_from_statistics_list
from Statistics.copy_statistics import  copy_monthly_transactions, copy_monthly_statistics, copy_quarterly_statistics, copy_yearly_statistics, copy_custom_range_statistics, copy_custom_range_transactions

from AppManagement.language import load_language, change_language_during_add_account
from AppManagement.balance import load_account_balance
from AppManagement.category import create_category, load_categories, remove_category, rename_category,  activate_categories, show_change_category_position, change_category_position
from AppManagement.transaction import transaction_data_handler
from AppManagement.date import next_month, previous_month, next_year, previous_year
from AppManagement.account import show_add_user_window, add_acccount, remove_account, show_rename_account_window, rename_account, load_accounts, clear_accounts_layout 
from AppManagement.backup_management import load_backups, create_backup, remove_backup, load_backup, open_auto_backup_window, auto_backup, prevent_same_auto_backup_status, save_auto_backup_settings, auto_remove_backups
from AppManagement.shortcuts import assign_shortcuts
from AppManagement.update_app import check_for_updates

from tests.init_tests import test_main



logger = get_logger(__name__)


def calculate_expression():
    """Calculate the expression from the mini calculator input field"""

    expression = MainWindow.mini_calculator_text.text()

    if expression != "":
        if not any([word in expression for word in FORBIDDEN_CALCULATOR_WORDS]):
            try:
                result = str(eval(expression))
            except ZeroDivisionError:
                result = LanguageStructure.MiniCalculator.get_translation(1)
                logger.debug(f"Zero division error (mini calculator) expression: {expression}")

            except SyntaxError:
                result = LanguageStructure.MiniCalculator.get_translation(2)
                logger.debug(f"Syntax error (mini calculator) expression: {expression}")
                
            except Exception as ex:
                result = str(ex)
                logger.debug(f"Error (mini calculator) expression: {expression}")
            MainWindow.mini_calculator_text.setText(result)

        else:
            Messages.forbidden_calculator_word.exec()
    else:
        Messages.empty_expression.exec()


def main():
    """Main function to start the application"""

    Session.start_session()

    #Set main window for instance guard
    Session.instance_guard.main_window = MainWindow.window
    # Ensure the safe exit when the application exits
    app.aboutToQuit.connect(Session.end_session)

    load_theme()

    #Set current month and year
    MainWindow.current_year.setText(str(Session.current_year))
    MainWindow.current_month.setText(LanguageStructure.Months.get_translation(Session.current_month))

    #Connect buttons to functions
    #Settings
    MainWindow.settings.clicked.connect(SettingsWindow.window.exec)
    SettingsWindow.switch_themes_button.clicked.connect(swith_theme)
    SettingsWindow.languages.currentIndexChanged.connect(load_language)
    SettingsWindow.add_account.clicked.connect(show_add_user_window)
    SettingsWindow.rename_account.clicked.connect(show_rename_account_window)
    SettingsWindow.switch_account.clicked.connect(SwitchAccountWindow.window.exec)
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
    CustomRangeStatistics.add_all_incomes_categories.clicked.connect(partial(add_all_categories_to_statistics_list, CustomRangeStatistics.add_all_incomes_categories))
    CustomRangeStatistics.add_all_expenses_categories.clicked.connect(partial(add_all_categories_to_statistics_list, CustomRangeStatistics.add_all_expenses_categories))
    CustomRangeStatistics.remove_all_incomes_categories.clicked.connect(partial(remove_all_categories_from_statistics_list, CustomRangeStatistics.remove_all_incomes_categories))
    CustomRangeStatistics.remove_all_expenses_categories.clicked.connect(partial(remove_all_categories_from_statistics_list, CustomRangeStatistics.remove_all_expenses_categories))
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
    AddAccountWindow.button.clicked.connect(add_acccount)
    AddAccountWindow.languages.currentIndexChanged.connect(change_language_during_add_account)
    #Connect to db
    logger.info("__BREAK_LINE__")
    logger.info("Connecting to database")
    if not Session.test_mode:
        Session.db = DBController()
        
    if not Session.db.account_query.account_exists(Session.account_name):
        logger.info("Account doesn't exist. Showing add account window")
        show_add_user_window()
        if not Session.db.account_id:
            logger.info("Account wasn't created. Exiting")
            exit() 
    Session.db.set_account_id(Session.account_name)
    logger.info("accont_id set")
    logger.info("Connected to database")
    logger.info("__BREAK_LINE__")
    
    #Load backups if they exists
    logger.info("Loading backups")
    load_backups()

    if not Session.test_mode and not Session.auto_backup_status == Session.AutoBackupStatus.NO_AUTO_BACKUP.value:
        logger.info("Auto backup enabled")
        auto_backup()
    
    if Session.auto_backup_removal_enabled:
        logger.info("Auto backup removal enabled")
        auto_remove_backups()
    logger.info("__BREAK_LINE__")

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
    logger.info("Loading categories")
    if len(Session.db.category_query.get_all_categories()) > 0:
        load_categories()
    activate_categories()
    logger.info(f"{len(Session.categories)} categories loaded")
    logger.info("__BREAK_LINE__")

    #Add accounts to list
    logger.info("Loading accounts")
    clear_accounts_layout()
    load_accounts()
    logger.info(f"{len(Session.accounts_list)} accounts loaded")
    logger.info("__BREAK_LINE__")

    #Shortcuts
    assign_shortcuts()
    logger.info("Shortcuts assigned")
    logger.info("__BREAK_LINE__")

    #Account management
    SettingsWindow.delete_account.clicked.connect(remove_account)
    RenameAccountWindow.button.clicked.connect(rename_account)

    load_account_balance()
    load_language(Session.language)

    MainWindow.window.show()

    if not Session.test_mode:
        QTimer.singleShot(200, check_for_updates)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--test", action="store_true")

    if parser.parse_args().test:
        test_main(main)
    else:
        main()
        app.exec()