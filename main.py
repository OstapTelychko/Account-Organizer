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

import setproctitle
from sys import exit
from argparse import ArgumentParser
from functools import partial

from PySide6.QtCore import QTimer

from project_configuration import FORBIDDEN_CALCULATOR_WORDS, APP_NAME
from languages import LanguageStructure
from backend.db_controller import DBController

from AppObjects.app_core import AppCore
from AppObjects.single_instance_guard import SingleInstanceGuard
from AppObjects.user_config import UserConfig
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from GUI.gui_constants import app
from GUI.theme import switch_theme, load_theme

from Statistics.statistics import show_monthly_statistics, show_quarterly_statistics, show_yearly_statistics,\
    show_custom_range_statistics_window, show_custom_range_statistics_view, add_all_categories_to_statistics_list,\
    remove_all_categories_from_statistics_list
from Statistics.copy_statistics import  copy_monthly_transactions, copy_monthly_statistics, copy_quarterly_statistics,\
    copy_yearly_statistics, copy_custom_range_statistics, copy_custom_range_transactions

from AppManagement.language import load_language, change_language_during_add_account
from AppManagement.balance import load_account_balance
from AppManagement.category import create_category, load_categories, remove_category, show_rename_category_window,\
    rename_category,  activate_categories, show_change_category_position, change_category_position
from AppManagement.transaction import transaction_data_handler
from AppManagement.date import next_month, previous_month, next_year, previous_year
from AppManagement.account import show_add_user_window, add_account, remove_account,\
    show_rename_account_window, rename_account, load_accounts, clear_accounts_layout 
from AppManagement.backup_management import load_backups, create_backup, remove_backup, load_backup,\
    open_auto_backup_window, auto_backup, prevent_same_auto_backup_status, save_auto_backup_settings, auto_remove_backups
from AppManagement.shortcuts.shortcuts_management import load_shortcuts, save_shortcuts
from AppManagement.AppUpdate.check_for_update import check_for_updates

from tests.init_tests import test_main

max_possible_length = len(setproctitle.getproctitle())
setproctitle.setproctitle(APP_NAME[:max_possible_length])
logger = get_logger(__name__)


def calculate_expression() -> None:
    """Calculate the expression from the mini calculator input field"""

    expression = WindowsRegistry.MainWindow.mini_calculator_text.text()

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
            WindowsRegistry.MainWindow.mini_calculator_text.setText(result)

        else:
            WindowsRegistry.Messages.forbidden_calculator_word.exec()
    else:
        WindowsRegistry.Messages.empty_expression.exec()


def main(test_mode:bool=False) -> None:
    """Main function to start the application"""

    def post_show_setup() -> None:
        """Setup that needs to be done after the main window is shown"""

        from AppObjects.shortcuts_manager import ShortcutsManager
        
        ShortcutsManager(app_core.config)

        #Load backups if they exists
        logger.info("Loading backups")
        load_backups()

        if not test_mode and not app_core.config.auto_backup_status == app_core.config.AutoBackupStatus.NO_AUTO_BACKUP.value:
            logger.info("Auto backup enabled")
            auto_backup()
        
        if app_core.config.auto_backup_removal_enabled:
            logger.info("Auto backup removal enabled")
            auto_remove_backups()
        logger.info("__BREAK_LINE__")

        #Load categories if they exists
        logger.info("Loading categories")
        if len(app_core.db.category_query.get_all_categories()) > 0:
            load_categories()
        activate_categories()
        logger.info(f"{len(app_core.categories)} categories loaded")
        logger.info("__BREAK_LINE__")

        #Add accounts to list
        logger.info("Loading accounts")
        clear_accounts_layout()
        load_accounts()
        logger.info(f"{len(app_core.accounts_list)} accounts loaded")
        logger.info("__BREAK_LINE__")

        #Shortcuts
        WindowsRegistry.ShortcutsWindow.save_shortcuts.clicked.connect(save_shortcuts)
        load_shortcuts()
        logger.info("Shortcuts loaded")
        logger.info("__BREAK_LINE__")

        #Account management
        WindowsRegistry.SettingsWindow.delete_account.clicked.connect(remove_account)
        WindowsRegistry.RenameAccountWindow.button.clicked.connect(rename_account)

        load_account_balance()
        load_language(app_core.config.language)

        
        if not test_mode:
            QTimer.singleShot(200, check_for_updates)

    
    if test_mode:
        app_core = AppCore.instance()
    else:
        Single_instance_guard = SingleInstanceGuard()
        db_controller = DBController(False)
        user_config = UserConfig(False)
        app_core = AppCore(
            single_instance_guard=Single_instance_guard,
            db_controller=db_controller,
            user_config=user_config,
            test_mode=False
        )


    app_core.start_session()

    #Set main window for instance guard
    app_core.instance_guard.main_window = WindowsRegistry.MainWindow
    # Ensure the safe exit when the application exits
    app.aboutToQuit.connect(AppCore.instance().end_session)

    load_theme()

    #Set current month and year
    WindowsRegistry.MainWindow.current_year.setText(str(app_core.current_year))
    WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(app_core.current_month))

    #Connect buttons to functions
    #Settings
    WindowsRegistry.MainWindow.settings.clicked.connect(WindowsRegistry.SettingsWindow.exec)
    WindowsRegistry.SettingsWindow.switch_themes_button.clicked.connect(switch_theme)
    WindowsRegistry.SettingsWindow.languages.currentIndexChanged.connect(load_language)
    WindowsRegistry.SettingsWindow.add_account.clicked.connect(show_add_user_window)
    WindowsRegistry.SettingsWindow.rename_account.clicked.connect(show_rename_account_window)
    WindowsRegistry.SettingsWindow.switch_account.clicked.connect(WindowsRegistry.SwitchAccountWindow.exec)
    WindowsRegistry.SettingsWindow.backup_management.clicked.connect(WindowsRegistry.BackupManagementWindow.exec)
    WindowsRegistry.SettingsWindow.shortcuts_management.clicked.connect(WindowsRegistry.ShortcutsWindow.exec)

    #Activate mini calculator
    WindowsRegistry.MainWindow.calculate.clicked.connect(calculate_expression)

    #Statistics
    WindowsRegistry.MainWindow.statistics.clicked.connect(WindowsRegistry.StatisticsWindow.exec)
    WindowsRegistry.StatisticsWindow.monthly_statistics.clicked.connect(show_monthly_statistics)
    WindowsRegistry.StatisticsWindow.quarterly_statistics.clicked.connect(show_quarterly_statistics)
    WindowsRegistry.StatisticsWindow.yearly_statistics.clicked.connect(show_yearly_statistics)
    WindowsRegistry.StatisticsWindow.custom_range_statistics.clicked.connect(show_custom_range_statistics_window)
    WindowsRegistry.MonthlyStatistics.copy_statistics.clicked.connect(copy_monthly_statistics)
    WindowsRegistry.QuarterlyStatistics.copy_statistics.clicked.connect(copy_quarterly_statistics)
    WindowsRegistry.YearlyStatistics.copy_statistics.clicked.connect(copy_yearly_statistics)
    WindowsRegistry.CustomRangeStatistics.show_statistics.clicked.connect(show_custom_range_statistics_view)
    WindowsRegistry.CustomRangeStatistics.add_all_incomes_categories.clicked.connect(
        partial(add_all_categories_to_statistics_list, WindowsRegistry.CustomRangeStatistics.add_all_incomes_categories)
    )
    WindowsRegistry.CustomRangeStatistics.add_all_expenses_categories.clicked.connect(
        partial(add_all_categories_to_statistics_list, WindowsRegistry.CustomRangeStatistics.add_all_expenses_categories)
    )
    WindowsRegistry.CustomRangeStatistics.remove_all_incomes_categories.clicked.connect(
        partial(
            remove_all_categories_from_statistics_list,
            WindowsRegistry.CustomRangeStatistics.remove_all_incomes_categories
        )
    )
    WindowsRegistry.CustomRangeStatistics.remove_all_expenses_categories.clicked.connect(
        partial(
            remove_all_categories_from_statistics_list,
            WindowsRegistry.CustomRangeStatistics.remove_all_expenses_categories
        )
    )
    WindowsRegistry.CustomRangeStatisticsView.copy_statistics.clicked.connect(copy_custom_range_statistics)
    WindowsRegistry.CustomRangeStatisticsView.copy_transactions.clicked.connect(copy_custom_range_transactions)
    
    #Category settings
    WindowsRegistry.CategorySettingsWindow.delete_category.clicked.connect(remove_category)
    WindowsRegistry.CategorySettingsWindow.rename_category.clicked.connect(show_rename_category_window)
    WindowsRegistry.CategorySettingsWindow.change_category_position.clicked.connect(
        lambda: show_change_category_position(WindowsRegistry.CategorySettingsWindow.windowTitle())
    )
    WindowsRegistry.CategorySettingsWindow.copy_transactions.clicked.connect(copy_monthly_transactions)
    WindowsRegistry.RenameCategoryWindow.button.clicked.connect(rename_category)
    WindowsRegistry.ChangeCategoryPositionWindow.enter_new_position.clicked.connect(change_category_position)
    WindowsRegistry.TransactionManagementWindow.button.clicked.connect(transaction_data_handler)
    
    #Date management
    WindowsRegistry.MainWindow.next_month_button.clicked.connect(next_month)
    WindowsRegistry.MainWindow.previous_month_button.clicked.connect(previous_month)
    WindowsRegistry.MainWindow.next_year_button.clicked.connect(next_year)
    WindowsRegistry.MainWindow.previous_year_button.clicked.connect(previous_year)

    #Add category
    WindowsRegistry.MainWindow.add_incomes_category.clicked.connect(WindowsRegistry.AddCategoryWindow.exec)
    WindowsRegistry.MainWindow.add_expenses_category.clicked.connect(WindowsRegistry.AddCategoryWindow.exec)
    WindowsRegistry.AddCategoryWindow.button.clicked.connect(create_category)


    #Create new account if it doesn't exist
    WindowsRegistry.AddAccountWindow.button.clicked.connect(add_account)
    WindowsRegistry.AddAccountWindow.languages.currentIndexChanged.connect(change_language_during_add_account)
    #Connect to db
    logger.info("__BREAK_LINE__")
    logger.info("Connecting to database")
        
    if not app_core.db.account_query.account_exists(app_core.config.account_name):
        logger.info("Account doesn't exist. Showing add account window")
        show_add_user_window()
        if not app_core.db.account_id:
            logger.info("Account wasn't created. Exiting")
            exit() 

    app_core.db.set_account_id(app_core.config.account_name)
    logger.info("account_id set")
    logger.info("Connected to database")
    logger.info("__BREAK_LINE__")
    
    WindowsRegistry.MainWindow.show()

    #Backup management
    WindowsRegistry.BackupManagementWindow.create_backup.clicked.connect(create_backup)
    WindowsRegistry.BackupManagementWindow.delete_backup.clicked.connect(remove_backup)
    WindowsRegistry.BackupManagementWindow.load_backup.clicked.connect(load_backup)
    WindowsRegistry.SettingsWindow.auto_backup.clicked.connect(open_auto_backup_window)

    WindowsRegistry.AutoBackupWindow.monthly.stateChanged.connect(
        partial(prevent_same_auto_backup_status, WindowsRegistry.AutoBackupWindow.monthly)
    )
    WindowsRegistry.AutoBackupWindow.weekly.stateChanged.connect(
        partial(prevent_same_auto_backup_status, WindowsRegistry.AutoBackupWindow.weekly)
    )
    WindowsRegistry.AutoBackupWindow.daily.stateChanged.connect(
        partial(prevent_same_auto_backup_status, WindowsRegistry.AutoBackupWindow.daily)
    )
    WindowsRegistry.AutoBackupWindow.no_auto_backup.stateChanged.connect(
        partial(prevent_same_auto_backup_status, WindowsRegistry.AutoBackupWindow.no_auto_backup)
    )
    WindowsRegistry.AutoBackupWindow.save.clicked.connect(save_auto_backup_settings)

    QTimer.singleShot(50, post_show_setup)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--test", action="store_true")

    if parser.parse_args().test:
        test_main(main)
    else:
        main()
        app.exec()