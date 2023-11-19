from Session import Session
from project_configuration import AVAILABLE_LANGUAGES
from languages import LANGUAGES
from GUI import *


def change_language():
    SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.language))

    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(round(Session.current_balance, 2)))
    MainWindow.current_month.setText(LANGUAGES[Session.language]["Months"][Session.current_month])
    MainWindow.Incomes_and_expenses.setTabText(0,LANGUAGES[Session.language]["Account"]["Info"][4])
    MainWindow.Incomes_and_expenses.setTabText(1,LANGUAGES[Session.language]["Account"]["Info"][5])
    MainWindow.add_incomes_category.setText(LANGUAGES[Session.language]["Account"]["Category management"][0])
    MainWindow.add_expenses_category.setText(LANGUAGES[Session.language]["Account"]["Category management"][0])
    MainWindow.statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][0])
    MainWindow.mini_calculator_label.setText(LANGUAGES[Session.language]["Mini calculator"][0])

    SettingsWindow.window.setWindowTitle(LANGUAGES[Session.language]["Windows"][0])
    SettingsWindow.delete_account.setText(LANGUAGES[Session.language]["Account"]["Account management"][0])
    SettingsWindow.add_account.setText(LANGUAGES[Session.language]["Account"]["Account management"][1])
    SettingsWindow.rename_account.setText(LANGUAGES[Session.language]["Account"]["Account management"][2])

    RenameAccountWindow.message.setText(LANGUAGES[Session.language]["Account"]["Account management"]["Messages"][1])
    RenameAccountWindow.button.setText(LANGUAGES[Session.language]["General management"][5])
    RenameAccountWindow.new_account_name.setPlaceholderText(LANGUAGES[Session.language]["Account"]["Account management"][3])
    RenameAccountWindow.window.setWindowTitle(LANGUAGES[Session.language]["Windows"][2])

    AddCategoryWindow.category_name.setPlaceholderText(LANGUAGES[Session.language]["Account"]["Info"][0])
    AddCategoryWindow.button.setText(LANGUAGES[Session.language]["General management"][1])
    AddCategoryWindow.window.setWindowTitle(LANGUAGES[Session.language]["Account"]["Category management"][0])

    CategorySettingsWindow.delete_category.setText(LANGUAGES[Session.language]["Account"]["Category management"][1])
    CategorySettingsWindow.rename_category.setText(LANGUAGES[Session.language]["Account"]["Category management"][2])
    CategorySettingsWindow.copy_transactions.setText(LANGUAGES[Session.language]["Account"]["Category management"][4])

    RenameCategoryWindow.new_category_name.setPlaceholderText(LANGUAGES[Session.language]["Account"]["Category management"][3])
    RenameCategoryWindow.button.setText(LANGUAGES[Session.language]["General management"][2])

    TransactionManagementWindow.button.setText(LANGUAGES[Session.language]["General management"][5])
    TransactionManagementWindow.transaction_name.setPlaceholderText(LANGUAGES[Session.language]["Account"]["Info"][0])
    TransactionManagementWindow.transaction_day.setPlaceholderText(LANGUAGES[Session.language]["Account"]["Info"][1])
    TransactionManagementWindow.transaction_value.setPlaceholderText(LANGUAGES[Session.language]["Account"]["Info"][2])

    StatisticsWindow.window.setWindowTitle(LANGUAGES[Session.language]["Windows"][4])
    StatisticsWindow.monthly_statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][1])
    StatisticsWindow.quarterly_statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][2])
    StatisticsWindow.yearly_statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][3])

    MonthlyStatistics.copy_statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][28])

    QuarterlyStatistics.window.setWindowTitle(LANGUAGES[Session.language]["Windows"][5])
    QuarterlyStatistics.copy_statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][30])
    quarters_numbers = ["I","II","III","IV"]
    month_number = 1
    for quarter in QuarterlyStatistics.statistics:
        QuarterlyStatistics.statistics[quarter]["Label"].setText(quarters_numbers[quarter-1]+LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][23])
        for month_list in QuarterlyStatistics.statistics[quarter]:
            if month_list != 0 and month_list != "Label":
                QuarterlyStatistics.statistics[quarter][month_list]["Label"].setText(LANGUAGES[Session.language]["Months"][month_number])
                month_number+=1
            elif month_list == 0:
                QuarterlyStatistics.statistics[quarter][0]["Label"].setText(LANGUAGES[Session.language]["Account"]["Info"][6])
    
    YearlyStatistics.window.setWindowTitle(LANGUAGES[Session.language]["Windows"][6])
    YearlyStatistics.copy_statistics.setText(LANGUAGES[Session.language]["Account"]["Info"]["Statistics"][32])
    for month_list in YearlyStatistics.statistics:
        if month_list != 0:
            YearlyStatistics.statistics[month_list]["Label"].setText(LANGUAGES[Session.language]["Months"][month_list])
        else:
            YearlyStatistics.statistics[0]["Label"].setText(LANGUAGES[Session.language]["Account"]["Info"][6])


    for index,error in enumerate(errors_list):
        error.setText(LANGUAGES[Session.language]["Errors"][index])
        error.button(QMessageBox.StandardButton.Ok).setText(LANGUAGES[Session.language]["General management"][3])
        if error.button(QMessageBox.StandardButton.Cancel) != None:
            error.button(QMessageBox.StandardButton.Cancel).setText(LANGUAGES[Session.language]["General management"][4])
    
    for category in Session.categories:
        Session.categories[category]["Add transaction"].setText(LANGUAGES[Session.language]["Account"]["Transactions management"][0])
        Session.categories[category]["Delete transaction"].setText(LANGUAGES[Session.language]["Account"]["Transactions management"][1])
        Session.categories[category]["Edit transaction"].setText(LANGUAGES[Session.language]["Account"]["Transactions management"][2])
        Session.categories[category]["Category data"].setHorizontalHeaderLabels((LANGUAGES[Session.language]["Account"]["Info"][0], LANGUAGES[Session.language]["Account"]["Info"][1], LANGUAGES[Session.language]["Account"]["Info"][2]))
        total_value = Session.categories[category]["Total value"].text().split(" ")[1]
        Session.categories[category]["Total value"].setText(LANGUAGES[Session.language]["Account"]["Info"][6] + total_value)
    
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Account"]["Info"][3]+str(round(Session.current_balance, 2)))
    Incomes = SettingsWindow.total_income.text().split(" ")[2]
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Account"]["Info"][7]+str(Incomes))
    Expenses = SettingsWindow.total_expense.text().split(" ")[2]
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Account"]["Info"][8]+str(Expenses))
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.language]["Account"]["Info"][9]+Session.account.get_account_date())  


def change_language_add_account(language: int | str):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.language = language
    else:
        Session.language = language
    Session.update_user_config()

    AddAccountWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.language))
    
    AddAccountWindow.message.setText(LANGUAGES[Session.language]["Account"]["Account management"]["Messages"][0])
    AddAccountWindow.button.setText(LANGUAGES[Session.language]["General management"][1])
    AddAccountWindow.window.setWindowTitle(LANGUAGES[Session.language]["Windows"][1])
    AddAccountWindow.current_balance.setPlaceholderText(LANGUAGES[Session.language]["Account"][0])
    AddAccountWindow.account_name.setPlaceholderText(LANGUAGES[Session.language]["Account"][1])


def load_language(language):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.language = language
    else:
        Session.language = language
    Session.update_user_config()
    change_language()