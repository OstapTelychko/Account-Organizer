from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import CATEGORY_TYPE
from AppManagement.information_message import show_information_message
from languages import LanguageStructure
from GUI.gui_constants import app
from GeneralTools.html_to_text import html_to_text




logger = get_logger(__name__)


def copy_monthly_transactions() -> None:
    """This method is used to copy the transactions of the selected category to the clipboard."""

    app_core = AppCore.instance()
    if WindowsRegistry.CategorySettingsWindow.copy_transactions.isEnabled():
        WindowsRegistry.CategorySettingsWindow.copy_transactions.setEnabled(False)
        category_name = WindowsRegistry.CategorySettingsWindow.windowTitle()
        category = app_core.db.category_query.get_category(
            category_name, CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]
        )
        if category is None:
            logger.error(f"Category {category_name} not found monthly transactions haven't been copied")
            return
        category_id = category.id
        
        transactions = app_core.db.transaction_query.get_transactions_by_month(
            category_id, app_core.current_year, app_core.current_month
        )
        if len(transactions):
            result = ""
            result += f"\t{LanguageStructure.Transactions.get_translation(2)}\t{LanguageStructure.Transactions.get_translation(1)}\t{LanguageStructure.Transactions.get_translation(0)}\t\t{LanguageStructure.Months.get_translation(app_core.current_month)}\t{app_core.current_year}\n"
            
            for index,transaction in enumerate(transactions):
                result += f"{index}\t{transaction.value}\t\t{transaction.date.day}\t{transaction.name}\n"
            

            app.clipboard().setText(result)
        else:
            app.clipboard().setText("")
        
        logger.info(f"Transactions for {category_name} copied | {app_core.current_year}-{app_core.current_month}")
        show_information_message(LanguageStructure.Categories.get_translation(5))


def copy_monthly_statistics() -> None:
    """This method is used to copy the monthly statistics to the clipboard."""

    app_core = AppCore.instance()
    if WindowsRegistry.MonthlyStatistics.copy_statistics.isEnabled():
        WindowsRegistry.MonthlyStatistics.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.MonthlyStatistics.statistics
        result = ""

        for row in range(statistics.count()):
            result += f"{statistics.item(row).text()}\n"
        
        app.clipboard().setText(html_to_text(result))
        logger.info(f"Monthly statistics copied | {app_core.current_year}-{app_core.current_month}")
        show_information_message(LanguageStructure.Statistics.get_translation(29))


def copy_quarterly_statistics() -> None:
    """This method is used to copy the quarterly statistics to the clipboard."""

    if WindowsRegistry.QuarterlyStatistics.copy_statistics.isEnabled():
        WindowsRegistry.QuarterlyStatistics.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.QuarterlyStatistics.statistics
        result = ""

        for quarter in statistics.quarters:
            result += f"\n{quarter.label.text():=^50}\n"

            total_quarter_statistics = quarter.total_quarter_statistics
            result += f"{total_quarter_statistics.label.text()}\n\n"
            for row in range(total_quarter_statistics.data.count()):
                result += f"{total_quarter_statistics.data.item(row).text()}\n"
            result += "\n\n"

            for month in quarter.months:
                result += f"{month.label.text():-^50}\n"
                for row in range(month.data.count()):
                    result += f"{month.data.item(row).text()}\n"
                result += "\n\n"
        
        app.clipboard().setText(html_to_text(result))
        logger.info(f"Quarterly statistics copied | {AppCore.instance().current_year}")
        show_information_message(LanguageStructure.Statistics.get_translation(31))


def copy_yearly_statistics() -> None:
    """This method is used to copy the yearly statistics to the clipboard."""

    if WindowsRegistry.YearlyStatistics.copy_statistics.isEnabled():
        WindowsRegistry.YearlyStatistics.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.YearlyStatistics.statistics
        result = ""

        total_yearly_statistics = statistics.total_year_statistics
        result += f"{total_yearly_statistics.label.text():=^50}\n"
        for row in range(total_yearly_statistics.data.count()):
            result += f"{total_yearly_statistics.data.item(row).text()}\n"

        for month in statistics.months:
            result += f"\n{month.label.text():-^50}\n"
            for row in range(month.data.count()):
                result += f"{month.data.item(row).text()}\n"

        app.clipboard().setText(html_to_text(result))
        logger.info(f"Yearly statistics copied | {AppCore.instance().current_year}")
        show_information_message(LanguageStructure.Statistics.get_translation(33))


def copy_custom_range_statistics() -> None:
    """This method is used to copy the custom range statistics to the clipboard."""

    if WindowsRegistry.CustomRangeStatisticsView.copy_statistics.isEnabled():
        WindowsRegistry.CustomRangeStatisticsView.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.CustomRangeStatisticsView.statistics_list
        result = ""

        for row in range(statistics.count()):
            result += statistics.item(row).text()

        app.clipboard().setText(html_to_text(result))
        show_information_message(LanguageStructure.Statistics.get_translation(36))


def copy_custom_range_transactions() -> None:
    """This method is used to copy the custom range transactions to the clipboard."""

    if WindowsRegistry.CustomRangeStatisticsView.copy_transactions.isEnabled():
        WindowsRegistry.CustomRangeStatisticsView.copy_transactions.setEnabled(False)
        transactions = WindowsRegistry.CustomRangeStatisticsView.transactions_list

        result = ""

        for row in range(transactions.count()):
            result += transactions.item(row).text()
        
        app.clipboard().setText(html_to_text(result))
        logger.info(f"Transactions for custom range copied")
        show_information_message(LanguageStructure.Statistics.get_translation(38))