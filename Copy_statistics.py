from GUI import InformationMessage, MainWindow, CategorySettingsWindow, QApplication, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics
from Project_configuration import CATEGORY_TYPE
from Account_management import Account
from Languages import LANGUAGES

from threading import Thread


def show_information_message(text:str):
    InformationMessage.message_text.setText(text)
    screen_center = MainWindow.window.frameGeometry().center()
    InformationMessage.window.move(screen_center)

    message_worker = Thread(target=InformationMessage.run)
    message_worker.run()
    


def copy_monthly_transactions(account: Account, Current_month:int, Current_year:int, Language:str, app:QApplication):
    if CategorySettingsWindow.copy_transactions.isEnabled():
        CategorySettingsWindow.copy_transactions.setEnabled(False)
        category_name = CategorySettingsWindow.window.windowTitle()
        category_id = account.get_category_id(category_name, CATEGORY_TYPE[MainWindow.Incomes_and_expenses.currentIndex()])
        
        transactions = account.get_transactions_by_month(category_id, Current_year, Current_month)
        if len(transactions):
            result = ""
            column_names = LANGUAGES[Language]["Account"]["Info"]
            result += f"\t{column_names[2]}\t{column_names[1]}\t{column_names[0]}\t\t{LANGUAGES[Language]['Months'][Current_month]}\t{Current_year}\n"
            for index,transaction in enumerate(transactions):
                result += f"{index}\t{transaction[5]}\t\t{transaction[4]}\t{transaction[6]}\n"
            

            app.clipboard().setText(result)
            show_information_message(LANGUAGES[Language]["Account"]["Category management"][5])


def copy_monthly_statistics(app:QApplication, Language:str):
    if MonthlyStatistics.copy_statistics.isEnabled():
        MonthlyStatistics.copy_statistics.setEnabled(False)
        statistics = MonthlyStatistics.statistics
        result = ""

        for row in range(statistics.count()):
            result += f"{statistics.item(row).text()}\n"
        
        app.clipboard().setText(result)
        show_information_message(LANGUAGES[Language]["Account"]["Info"]["Statistics"][29])


def copy_quarterly_statistics(app:QApplication, Language:str):
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
        show_information_message(LANGUAGES[Language]["Account"]["Info"]["Statistics"][31])


def copy_yearly_statistics(app:QApplication, Language:str):
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
        show_information_message(LANGUAGES[Language]["Account"]["Info"]["Statistics"][33])

