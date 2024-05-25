from threading import Thread

from AppObjects.session import Session
from project_configuration import CATEGORY_TYPE
from languages import LANGUAGES

from GUI.windows.main import MainWindow, app
from GUI.windows.information_message import InformationMessage
from GUI.windows.category import CategorySettingsWindow 
from GUI.windows.statistics import MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatisticsView



def show_information_message(text:str):
    InformationMessage.message_text.setText(text)
    screen_center = MainWindow.window.frameGeometry().center()
    InformationMessage.window.move(screen_center)

    message_worker = Thread(target=InformationMessage.run)
    message_worker.run()


def copy_monthly_transactions():
    if CategorySettingsWindow.copy_transactions.isEnabled():
        CategorySettingsWindow.copy_transactions.setEnabled(False)
        category_name = CategorySettingsWindow.window.windowTitle()
        category_id = Session.db.get_category(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()]).id
        
        transactions = Session.db.get_transactions_by_month(category_id, Session.current_year, Session.current_month)
        if len(transactions):
            result = ""
            column_names = LANGUAGES[Session.language]["Account"]["Info"]
            result += f"\t{column_names[2]}\t{column_names[1]}\t{column_names[0]}\t\t{LANGUAGES[Session.language]['Months'][Session.current_month]}\t{Session.current_year}\n"
            for index,transaction in enumerate(transactions):
                result += f"{index}\t{transaction.value}\t\t{transaction.day}\t{transaction.name}\n"
            

            app.clipboard().setText(result)
        else:
            app.clipboard().setText("")
            
        show_information_message(LANGUAGES[Session.language]["Account"]["Category management"][5])


def copy_monthly_statistics():
    if MonthlyStatistics.copy_statistics.isEnabled():
        MonthlyStatistics.copy_statistics.setEnabled(False)
        statistics = MonthlyStatistics.statistics
        result = ""

        for row in range(statistics.count()):
            result += f"{statistics.item(row).text()}\n"
        
        app.clipboard().setText(result)
        show_information_message(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][29])


def copy_quarterly_statistics():
    if QuarterlyStatistics.copy_statistics.isEnabled():
        QuarterlyStatistics.copy_statistics.setEnabled(False)
        statistics = QuarterlyStatistics.statistics
        result = ""

        for quarter in statistics:
            result += f"{statistics[quarter]['Label'].text()}\n\n"
            for statistic_list in statistics[quarter]:
                if statistic_list != "Label":
                    result += f"{statistics[quarter][statistic_list]['Label'].text()}\n\n"
                    for row in range(statistics[quarter][statistic_list]["Statistic Data"].count()):
                        result += f"{statistics[quarter][statistic_list]['Statistic Data'].item(row).text()}\n"
                    result += "\n"
            result+= "\n"
        
        app.clipboard().setText(result)
        show_information_message(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][31])


def copy_yearly_statistics():
    if YearlyStatistics.copy_statistics.isEnabled():
        YearlyStatistics.copy_statistics.setEnabled(False)
        statistics = YearlyStatistics.statistics
        result = ""

        for statistic_list in statistics:
            result += f"{statistics[statistic_list]['Label'].text()}\n"
            for row in range(statistics[statistic_list]["Statistic Data"].count()):
                result += f"{statistics[statistic_list]['Statistic Data'].item(row).text()}\n"
            result += "\n\n\n"

        app.clipboard().setText(result)
        show_information_message(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][33])


def copy_custom_range_statistics():
    if CustomRangeStatisticsView.copy_statistics.isEnabled():
        CustomRangeStatisticsView.copy_statistics.setEnabled(False)
        statistics = CustomRangeStatisticsView.statistics_list
        result = ""

        for row in range(statistics.count()):
            result += f"{statistics.item(row).text()}\n"
        
        app.clipboard().setText(result)
        show_information_message(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][36])


def copy_custom_range_transactions():
    if CustomRangeStatisticsView.copy_transactions.isEnabled():
        CustomRangeStatisticsView.copy_transactions.setEnabled(False)
        transactions = CustomRangeStatisticsView.transactions_list

        result = ""

        for row in range(transactions.count()):
            result += f"{transactions.item(row).text()}\n"
        
        app.clipboard().setText(result)
        show_information_message(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][38])