from threading import Thread

from AppObjects.session import Session
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from project_configuration import CATEGORY_TYPE
from languages import LanguageStructure

from GUI.gui_constants import app



logger = get_logger(__name__)

def show_information_message(text:str):
    """This method is used to show the information message window and center it on the main window.

        Arguments
        -------
            `text` (str): message to show
    """

    WindowsRegistry.InformationMessage.message_text.setText(text)
    screen_center = WindowsRegistry.MainWindow.frameGeometry().center()
    WindowsRegistry.InformationMessage.move(screen_center)

    try:
        message_worker = Thread(target=WindowsRegistry.InformationMessage.run)
        message_worker.start()
    except RuntimeError:
        pass # When the program exits, this prevents a widget deletion error



def copy_monthly_transactions():
    """This method is used to copy the transactions of the selected category to the clipboard."""

    if WindowsRegistry.CategorySettingsWindow.copy_transactions.isEnabled():
        WindowsRegistry.CategorySettingsWindow.copy_transactions.setEnabled(False)
        category_name = WindowsRegistry.CategorySettingsWindow.windowTitle()
        category_id = Session.db.category_query.get_category(category_name, CATEGORY_TYPE[WindowsRegistry.MainWindow.Incomes_and_expenses.currentIndex()]).id
        
        transactions = Session.db.transaction_query.get_transactions_by_month(category_id, Session.current_year, Session.current_month)
        if len(transactions):
            result = ""
            result += f"\t{LanguageStructure.Transactions.get_translation(2)}\t{LanguageStructure.Transactions.get_translation(1)}\t{LanguageStructure.Transactions.get_translation(0)}\t\t{LanguageStructure.Months.get_translation(Session.current_month)}\t{Session.current_year}\n"
            
            for index,transaction in enumerate(transactions):
                result += f"{index}\t{transaction.value}\t\t{transaction.day}\t{transaction.name}\n"
            

            app.clipboard().setText(result)
        else:
            app.clipboard().setText("")
        
        logger.info(f"Transactions for {category_name} copied | {Session.current_year}-{Session.current_month}")
        show_information_message(LanguageStructure.Categories.get_translation(5))


def copy_monthly_statistics():
    """This method is used to copy the monthly statistics to the clipboard."""

    if WindowsRegistry.MonthlyStatistics.copy_statistics.isEnabled():
        WindowsRegistry.MonthlyStatistics.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.MonthlyStatistics.statistics
        result = ""

        for row in range(statistics.count()):
            result += f"{statistics.item(row).text()}\n"
        
        app.clipboard().setText(result)
        logger.info(f"Monthly statistics copied | {Session.current_year}-{Session.current_month}")
        show_information_message(LanguageStructure.Statistics.get_translation(29))


def copy_quarterly_statistics():
    """This method is used to copy the quarterly statistics to the clipboard."""

    if WindowsRegistry.QuarterlyStatistics.copy_statistics.isEnabled():
        WindowsRegistry.QuarterlyStatistics.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.QuarterlyStatistics.statistics
        result = ""

        for quarter in statistics.quarters:
            result += f"{quarter.label.text()}\n\n"

            total_quarter_statistics = quarter.total_quarter_statistics
            result += f"{total_quarter_statistics.label.text()}\n\n"
            for row in range(total_quarter_statistics.data.count()):
                result += f"{total_quarter_statistics.data.item(row).text()}\n"
            result += "\n\n"

            for month in quarter.months:
                result += f"{month.label.text()}\n"
                for row in range(month.data.count()):
                    result += f"{month.data.item(row).text()}\n"
                result += "\n\n"
            result+= "\n\n\n"
        
        app.clipboard().setText(result)
        logger.info(f"Quarterly statistics copied | {Session.current_year}")
        show_information_message(LanguageStructure.Statistics.get_translation(31))


def copy_yearly_statistics():
    """This method is used to copy the yearly statistics to the clipboard."""

    if WindowsRegistry.YearlyStatistics.copy_statistics.isEnabled():
        WindowsRegistry.YearlyStatistics.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.YearlyStatistics.statistics
        result = ""

        total_yearly_statistics = statistics.total_year_statistics
        result += f"{total_yearly_statistics.label.text()}\n"
        for row in range(total_yearly_statistics.data.count()):
            result += f"{total_yearly_statistics.data.item(row).text()}\n"
        result += "\n\n\n"

        for month in statistics.months:
            result += f"{month.label.text()}\n"
            for row in range(month.data.count()):
                result += f"{month.data.item(row).text()}\n"
            result += "\n\n\n"

        app.clipboard().setText(result)
        logger.info(f"Yearly statistics copied | {Session.current_year}")
        show_information_message(LanguageStructure.Statistics.get_translation(33))


def copy_custom_range_statistics():
    """This method is used to copy the custom range statistics to the clipboard."""

    if WindowsRegistry.CustomRangeStatisticsView.copy_statistics.isEnabled():
        WindowsRegistry.CustomRangeStatisticsView.copy_statistics.setEnabled(False)
        statistics = WindowsRegistry.CustomRangeStatisticsView.statistics_list
        result = ""

        for row in range(statistics.count()):
            result += f"{statistics.item(row).text()}\n"
        
        app.clipboard().setText(result)
        show_information_message(LanguageStructure.Statistics.get_translation(36))


def copy_custom_range_transactions():
    """This method is used to copy the custom range transactions to the clipboard."""

    if WindowsRegistry.CustomRangeStatisticsView.copy_transactions.isEnabled():
        WindowsRegistry.CustomRangeStatisticsView.copy_transactions.setEnabled(False)
        transactions = WindowsRegistry.CustomRangeStatisticsView.transactions_list

        result = ""

        for row in range(transactions.count()):
            result += f"{transactions.item(row).text()}\n"
        
        app.clipboard().setText(result)
        logger.info(f"Transactions for custom range copied")
        show_information_message(LanguageStructure.Statistics.get_translation(38))