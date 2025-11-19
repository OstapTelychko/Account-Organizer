from PySide6.QtWidgets import QMessageBox

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.shortcuts_manager import ShortcutsManager

from project_configuration import AVAILABLE_LANGUAGES
from languages import LanguageStructure



logger = get_logger(__name__)

def change_language_for_startup() -> None:
    """Change language during application startup. Until app fully loads these windows and widgets have to be translated."""

    app_core = AppCore.instance()
    WindowsRegistry.SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(app_core.config.language))

    WindowsRegistry.MainWindow.account_current_balance.setText(
        f"{LanguageStructure.MainWindow.get_translation(0)}{round(app_core.current_balance, 2)}"
    )

    WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(app_core.current_month))
    WindowsRegistry.MainWindow.Incomes_and_expenses.setTabText(0, LanguageStructure.MainWindow.get_translation(1))
    WindowsRegistry.MainWindow.Incomes_and_expenses.setTabText(1, LanguageStructure.MainWindow.get_translation(2))
    WindowsRegistry.MainWindow.add_incomes_category.setText(LanguageStructure.Categories.get_translation(0))
    WindowsRegistry.MainWindow.add_expenses_category.setText(LanguageStructure.Categories.get_translation(0))
    WindowsRegistry.MainWindow.statistics.setText(LanguageStructure.Statistics.get_translation(0))
    WindowsRegistry.MainWindow.search.setText(LanguageStructure.Search.get_translation(0))
    WindowsRegistry.MainWindow.mini_calculator_label.setText(LanguageStructure.MiniCalculator.get_translation(0))


def change_language() -> None:
    """Change language of the application. It changes the text of all widgets in the application."""

    app_core = AppCore.instance()

    WindowsRegistry.SettingsWindow.setWindowTitle(LanguageStructure.Settings.get_translation(0))
    WindowsRegistry.SettingsWindow.delete_account.setText(LanguageStructure.Account.get_translation(0))
    WindowsRegistry.SettingsWindow.add_account.setText(LanguageStructure.Account.get_translation(1))
    WindowsRegistry.SettingsWindow.rename_account.setText(LanguageStructure.Account.get_translation(2))
    WindowsRegistry.SettingsWindow.switch_account.setText(LanguageStructure.Account.get_translation(6))
    WindowsRegistry.SettingsWindow.total_income.setText(LanguageStructure.Statistics.get_translation(4)+str(app_core.current_total_income))
    WindowsRegistry.SettingsWindow.total_expense.setText(LanguageStructure.Statistics.get_translation(6)+str(app_core.current_total_expenses))
    WindowsRegistry.SettingsWindow.account_created_date.setText(
        LanguageStructure.Settings.get_translation(1)
        + str(app_core.db.account_query.get_account().created_date.strftime("%Y-%m-%d %H:%M:%S"))
    )
    WindowsRegistry.SettingsWindow.backup_management.setText(LanguageStructure.BackupManagement.get_translation(0))
    WindowsRegistry.SettingsWindow.general_section.section_name.setText(LanguageStructure.Settings.get_translation(3))
    WindowsRegistry.SettingsWindow.account_section.section_name.setText(LanguageStructure.Settings.get_translation(4))
    WindowsRegistry.SettingsWindow.account_info_section.section_name.setText(LanguageStructure.Settings.get_translation(5))
    WindowsRegistry.SettingsWindow.backup_section.section_name.setText(LanguageStructure.Settings.get_translation(6))
    WindowsRegistry.SettingsWindow.shortcuts_management.setText(LanguageStructure.ShortcutsManagement.get_translation(0))
    
    WindowsRegistry.SettingsWindow.app_version.setText(LanguageStructure.Settings.get_translation(2) + app_core.app_version)
                                       
    WindowsRegistry.RenameAccountWindow.message.setText(LanguageStructure.AccountMessages.get_translation(1))
    WindowsRegistry.RenameAccountWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(5))
    WindowsRegistry.RenameAccountWindow.new_account_name.setPlaceholderText(LanguageStructure.Account.get_translation(3))
    WindowsRegistry.RenameAccountWindow.setWindowTitle(LanguageStructure.Account.get_translation(2))

    WindowsRegistry.SwitchAccountWindow.setWindowTitle(LanguageStructure.Account.get_translation(6))
    for account, account_switch_widget in zip(app_core.accounts_list, WindowsRegistry.SwitchAccountWindow.account_switch_widgets):
        account_switch_widget.account_balance_label.setText(
            f"{LanguageStructure.MainWindow.get_translation(0)}{round(account.current_balance, 2)}"
)
        account_switch_widget.account_creation_date_label.setText(
            f"{LanguageStructure.Settings.get_translation(1)}{account.created_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        account_switch_widget.switch_button.setText(LanguageStructure.GeneralManagement.get_translation(8))

    WindowsRegistry.AddCategoryWindow.category_name.setPlaceholderText(LanguageStructure.Transactions.get_translation(0))
    WindowsRegistry.AddCategoryWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(1))
    WindowsRegistry.AddCategoryWindow.setWindowTitle(LanguageStructure.Categories.get_translation(0))

    WindowsRegistry.CategorySettingsWindow.delete_category.setText(LanguageStructure.Categories.get_translation(1))
    WindowsRegistry.CategorySettingsWindow.rename_category.setText(LanguageStructure.Categories.get_translation(2))
    WindowsRegistry.CategorySettingsWindow.copy_transactions.setText(LanguageStructure.Categories.get_translation(4))
    WindowsRegistry.CategorySettingsWindow.change_category_position.setText(
        LanguageStructure.Categories.get_translation(9)
    )

    WindowsRegistry.ChangeCategoryPositionWindow.enter_new_position.setText(
        LanguageStructure.GeneralManagement.get_translation(6)
    )

    WindowsRegistry.RenameCategoryWindow.new_category_name.setPlaceholderText(
        LanguageStructure.Categories.get_translation(3)
    )
    WindowsRegistry.RenameCategoryWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(2))

    WindowsRegistry.TransactionManagementWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(5))
    WindowsRegistry.TransactionManagementWindow.transaction_name.setPlaceholderText(
        LanguageStructure.Transactions.get_translation(0)
    )
    WindowsRegistry.TransactionManagementWindow.transaction_day.setPlaceholderText(
        LanguageStructure.Transactions.get_translation(1)
    )
    WindowsRegistry.TransactionManagementWindow.transaction_value.setPlaceholderText(
        LanguageStructure.Transactions.get_translation(2)
    )

    WindowsRegistry.StatisticsWindow.setWindowTitle(LanguageStructure.Statistics.get_translation(0))
    WindowsRegistry.StatisticsWindow.monthly_statistics.setText(LanguageStructure.Statistics.get_translation(1))
    WindowsRegistry.StatisticsWindow.quarterly_statistics.setText(LanguageStructure.Statistics.get_translation(2))
    WindowsRegistry.StatisticsWindow.yearly_statistics.setText(LanguageStructure.Statistics.get_translation(3))
    WindowsRegistry.StatisticsWindow.custom_range_statistics.setText(LanguageStructure.Statistics.get_translation(34))

    WindowsRegistry.MonthlyStatistics.copy_statistics.setText(LanguageStructure.Statistics.get_translation(28))

    WindowsRegistry.QuarterlyStatistics.setWindowTitle(LanguageStructure.Statistics.get_translation(2))
    WindowsRegistry.QuarterlyStatistics.copy_statistics.setText(LanguageStructure.Statistics.get_translation(30))
    quarters_numbers = ["I","II","III","IV"]
    for quarter in WindowsRegistry.QuarterlyStatistics.statistics.quarters:
        quarter.label.setText(quarters_numbers[quarter.quarter_number-1]+LanguageStructure.Statistics.get_translation(23))
        quarter.total_quarter_statistics.label.setText(LanguageStructure.Categories.get_translation(10))

        for qmonth in quarter.months:
            qmonth.label.setText(LanguageStructure.Months.get_translation(qmonth.month_number))
    
    WindowsRegistry.YearlyStatistics.setWindowTitle(LanguageStructure.Statistics.get_translation(3))
    WindowsRegistry.YearlyStatistics.copy_statistics.setText(LanguageStructure.Statistics.get_translation(32))
    WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.label.setText(
        LanguageStructure.Categories.get_translation(10)
    )
    for ymonth in WindowsRegistry.YearlyStatistics.statistics.months:
        ymonth.label.setText(LanguageStructure.Months.get_translation(ymonth.month_number))
    
    WindowsRegistry.CustomRangeStatistics.setWindowTitle(LanguageStructure.Statistics.get_translation(34))
    WindowsRegistry.CustomRangeStatistics.show_statistics.setText(LanguageStructure.Statistics.get_translation(0))
    WindowsRegistry.CustomRangeStatistics.add_all_incomes_categories.setText(
        LanguageStructure.GeneralManagement.get_translation(9)
    )
    WindowsRegistry.CustomRangeStatistics.add_all_expenses_categories.setText(
        LanguageStructure.GeneralManagement.get_translation(9)
    )
    WindowsRegistry.CustomRangeStatistics.remove_all_incomes_categories.setText(
        LanguageStructure.GeneralManagement.get_translation(10)
    )
    WindowsRegistry.CustomRangeStatistics.remove_all_expenses_categories.setText(
        LanguageStructure.GeneralManagement.get_translation(10)
    )
    WindowsRegistry.CustomRangeStatisticsView.setWindowTitle(
        LanguageStructure.Statistics.get_translation(34)
    )
    WindowsRegistry.CustomRangeStatisticsView.copy_statistics.setText(
        LanguageStructure.Statistics.get_translation(35)
    )
    WindowsRegistry.CustomRangeStatisticsView.copy_transactions.setText(LanguageStructure.Statistics.get_translation(37))


    for account_layout_item, message in enumerate(WindowsRegistry.MainWindow.message_windows.values()):
        message.setText(LanguageStructure.Messages.get_translation(account_layout_item))
        message.button(QMessageBox.StandardButton.Ok).setText(LanguageStructure.GeneralManagement.get_translation(3))
        if message.button(QMessageBox.StandardButton.Cancel) != None:
            message.button(QMessageBox.StandardButton.Cancel).setText(
                LanguageStructure.GeneralManagement.get_translation(4)
            )

    for category in app_core.categories:
        app_core.categories[category].delete_transaction.setText(LanguageStructure.GeneralManagement.get_translation(0))
        app_core.categories[category].add_transaction.setText(LanguageStructure.GeneralManagement.get_translation(1))
        app_core.categories[category].edit_transaction.setText(LanguageStructure.GeneralManagement.get_translation(7))
        app_core.categories[category].table_data.setHorizontalHeaderLabels(
            (LanguageStructure.Transactions.get_translation(0),
            LanguageStructure.Transactions.get_translation(1),
            LanguageStructure.Transactions.get_translation(2))
        )
        total_value = app_core.categories[category].total_value_label.text().split(" ")[1]
        app_core.categories[category].total_value_label.setText(
            LanguageStructure.Categories.get_translation(10) + total_value
        )

    WindowsRegistry.BackupManagementWindow.setWindowTitle(LanguageStructure.BackupManagement.get_translation(0))
    WindowsRegistry.BackupManagementWindow.backups_table.setHorizontalHeaderLabels(
        (
            LanguageStructure.Transactions.get_translation(1),
            LanguageStructure.Settings.get_translation(2).replace(":", "")
        )
    )
    WindowsRegistry.BackupManagementWindow.create_backup.setText(LanguageStructure.BackupManagement.get_translation(1))
    WindowsRegistry.BackupManagementWindow.delete_backup.setText(LanguageStructure.BackupManagement.get_translation(2))
    WindowsRegistry.BackupManagementWindow.load_backup.setText(LanguageStructure.BackupManagement.get_translation(3))
    WindowsRegistry.SettingsWindow.auto_backup.setText(LanguageStructure.BackupManagement.get_translation(4))
    WindowsRegistry.SettingsWindow.auto_backup_status.setText(
        f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(5)}"
    )

    WindowsRegistry.AutoBackupWindow.setWindowTitle(LanguageStructure.BackupManagement.get_translation(4))
    if app_core.config.auto_backup_status == app_core.config.AutoBackupStatus.MONTHLY.value:
        WindowsRegistry.AutoBackupWindow.current_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(5)}"
        )
        WindowsRegistry.SettingsWindow.auto_backup_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(5)}"
        )

    elif app_core.config.auto_backup_status == app_core.config.AutoBackupStatus.WEEKLY.value:
        WindowsRegistry.AutoBackupWindow.current_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(6)}"
        )
        WindowsRegistry.SettingsWindow.auto_backup_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(6)}"
        )

    elif app_core.config.auto_backup_status == app_core.config.AutoBackupStatus.DAILY.value:
        WindowsRegistry.AutoBackupWindow.current_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(7)}"
        )
        WindowsRegistry.SettingsWindow.auto_backup_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(7)}"
        )

    elif app_core.config.auto_backup_status == app_core.config.AutoBackupStatus.NO_AUTO_BACKUP.value:
        WindowsRegistry.AutoBackupWindow.current_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(20)}"
        )
        WindowsRegistry.SettingsWindow.auto_backup_status.setText(
            f"{LanguageStructure.BackupManagement.get_translation(8)} {LanguageStructure.BackupManagement.get_translation(20)}"
        )
    WindowsRegistry.AutoBackupWindow.monthly.setText(LanguageStructure.BackupManagement.get_translation(9))
    WindowsRegistry.AutoBackupWindow.weekly.setText(LanguageStructure.BackupManagement.get_translation(10))
    WindowsRegistry.AutoBackupWindow.daily.setText(LanguageStructure.BackupManagement.get_translation(11))
    WindowsRegistry.AutoBackupWindow.no_auto_backup.setText(LanguageStructure.BackupManagement.get_translation(15))
    WindowsRegistry.AutoBackupWindow.max_backups_label.setText(
        f"{LanguageStructure.BackupManagement.get_translation(12).replace('%max_backups%', str(app_core.config.max_backups))}\
        \n{LanguageStructure.BackupManagement.get_translation(13)}"
    )
    WindowsRegistry.AutoBackupWindow.max_backups.setPlaceholderText(LanguageStructure.BackupManagement.get_translation(14))
    WindowsRegistry.AutoBackupWindow.max_legacy_backups_label.setText(
        f"{LanguageStructure.BackupManagement.get_translation(17).replace('%max_legacy_backups%', str(app_core.config.max_legacy_backups))}\
        \n{LanguageStructure.BackupManagement.get_translation(18)}"
    
    )
    WindowsRegistry.AutoBackupWindow.max_legacy_backups.setPlaceholderText(LanguageStructure.BackupManagement.get_translation(19))
    WindowsRegistry.AutoBackupWindow.no_auto_removal.setText(LanguageStructure.BackupManagement.get_translation(16))
    WindowsRegistry.AutoBackupWindow.save.setText(LanguageStructure.GeneralManagement.get_translation(6))

    WindowsRegistry.UpdateProgressWindow.setWindowTitle(LanguageStructure.Update.get_translation(0))
    WindowsRegistry.UpdateProgressWindow.update_progress_title.setText(LanguageStructure.Update.get_translation(1))
    WindowsRegistry.UpdateProgressWindow.backups_upgrade_label.setText(LanguageStructure.Update.get_translation(3))

    WindowsRegistry.ShortcutsWindow.setWindowTitle(LanguageStructure.ShortcutsManagement.get_translation(0))

    for shortcut, index in ShortcutsManager.instance().shortcut_widget_to_translations.items():
        shortcut.shortcut_name.setText(LanguageStructure.ShortcutsNames.get_translation(index))
        shortcut.shortcut_description.setText(LanguageStructure.ShortcutsDescriptions.get_translation(index))
        shortcut.reset_shortcut.setText(LanguageStructure.GeneralManagement.get_translation(11))
    WindowsRegistry.ShortcutsWindow.save_shortcuts.setText(LanguageStructure.GeneralManagement.get_translation(6))

    WindowsRegistry.SearchWindow.setWindowTitle(LanguageStructure.Search.get_translation(1))
    WindowsRegistry.SearchWindow.search.setText(LanguageStructure.Search.get_translation(0))
    WindowsRegistry.SearchWindow.search_name.setPlaceholderText(LanguageStructure.Search.get_translation(2))
    WindowsRegistry.SearchWindow.search_value.setPlaceholderText(LanguageStructure.Search.get_translation(3))
    WindowsRegistry.SearchWindow.select_month_range_button.setText(LanguageStructure.Search.get_translation(4))
    WindowsRegistry.SearchWindow.select_year_range_button.setText(LanguageStructure.Search.get_translation(5))


 
def change_language_during_add_account(language:int | str) -> None:
    """Change language during adding account. In case db have no account, not all windows are loaded."""

    app_core = AppCore.instance()
    if isinstance(language, int):# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        app_core.config.language = language
    else:
        app_core.config.language = language
    logger.info(f"Language {app_core.config.language} loaded during adding account")
    app_core.config.update_user_config()

    WindowsRegistry.AddAccountWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(app_core.config.language))
    
    WindowsRegistry.AddAccountWindow.message.setText(LanguageStructure.AccountMessages.get_translation(0))
    WindowsRegistry.AddAccountWindow.button.setText(LanguageStructure.GeneralManagement.get_translation(1))
    WindowsRegistry.AddAccountWindow.setWindowTitle(LanguageStructure.Account.get_translation(1))
    WindowsRegistry.AddAccountWindow.current_balance.setPlaceholderText(LanguageStructure.Account.get_translation(4))
    WindowsRegistry.AddAccountWindow.account_name.setPlaceholderText(LanguageStructure.Account.get_translation(5))


def load_language(language:str|int) -> None:
    """Load language. It loads language from user config or by user choice.

        Arguments
        ---------
        `language` : str | int - Language to load. It can be a string or an index of the language in AVAILABLE_LANGUAGES.
            If the language is a string, it will be converted to an index.
    """

    logger.info("Loading language")
    app_core = AppCore.instance()
    if isinstance(language, int):# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        app_core.config.language = language
    else:
        app_core.config.language = language
    app_core.config.update_user_config()
    change_language_for_startup()
    change_language()
    logger.info(f"Language {app_core.config.language} loaded")