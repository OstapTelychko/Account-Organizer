from Session import Session
from project_configuration import AVAILABLE_LANGUAGES
from languages import LANGUAGES
from GUI import *


def change_language():
    SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.Language))

    MainWindow.account_current_balance.setText(LANGUAGES[Session.Language]["Account"]["Info"][3]+str(round(Session.Current_balance, 2)))
    MainWindow.current_month.setText(LANGUAGES[Session.Language]["Months"][Session.Current_month])
    MainWindow.Incomes_and_expenses.setTabText(0,LANGUAGES[Session.Language]["Account"]["Info"][4])
    MainWindow.Incomes_and_expenses.setTabText(1,LANGUAGES[Session.Language]["Account"]["Info"][5])
    MainWindow.add_incomes_category.setText(LANGUAGES[Session.Language]["Account"]["Category management"][0])
    MainWindow.add_expenses_category.setText(LANGUAGES[Session.Language]["Account"]["Category management"][0])
    MainWindow.statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][0])
    MainWindow.mini_calculator_label.setText(LANGUAGES[Session.Language]["Mini calculator"][0])

    SettingsWindow.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][0])
    SettingsWindow.delete_account.setText(LANGUAGES[Session.Language]["Account"]["Account management"][0])
    SettingsWindow.add_account.setText(LANGUAGES[Session.Language]["Account"]["Account management"][1])
    SettingsWindow.rename_account.setText(LANGUAGES[Session.Language]["Account"]["Account management"][2])

    RenameAccountWindow.message.setText(LANGUAGES[Session.Language]["Account"]["Account management"]["Messages"][1])
    RenameAccountWindow.button.setText(LANGUAGES[Session.Language]["General management"][5])
    RenameAccountWindow.new_name.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Account management"][3])
    RenameAccountWindow.new_surname.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Account management"][4])
    RenameAccountWindow.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][2])

    AddCategoryWindow.category_name.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Info"][0])
    AddCategoryWindow.button.setText(LANGUAGES[Session.Language]["General management"][1])
    AddCategoryWindow.window.setWindowTitle(LANGUAGES[Session.Language]["Account"]["Category management"][0])

    CategorySettingsWindow.delete_category.setText(LANGUAGES[Session.Language]["Account"]["Category management"][1])
    CategorySettingsWindow.rename_category.setText(LANGUAGES[Session.Language]["Account"]["Category management"][2])
    CategorySettingsWindow.copy_transactions.setText(LANGUAGES[Session.Language]["Account"]["Category management"][4])

    RenameCategoryWindow.new_category_name.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Category management"][3])
    RenameCategoryWindow.button.setText(LANGUAGES[Session.Language]["General management"][2])

    TransactionManagementWindow.button.setText(LANGUAGES[Session.Language]["General management"][5])
    TransactionManagementWindow.transaction_name.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Info"][0])
    TransactionManagementWindow.transaction_day.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Info"][1])
    TransactionManagementWindow.transaction_value.setPlaceholderText(LANGUAGES[Session.Language]["Account"]["Info"][2])

    StatisticsWindow.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][4])
    StatisticsWindow.monthly_statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][1])
    StatisticsWindow.quarterly_statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][2])
    StatisticsWindow.yearly_statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][3])

    MonthlyStatistics.copy_statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][28])

    QuarterlyStatistics.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][5])
    QuarterlyStatistics.copy_statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][30])
    quarters_numbers = ["I","II","III","IV"]
    month_number = 1
    for quarter in QuarterlyStatistics.statistics:
        QuarterlyStatistics.statistics[quarter]["Label"].setText(quarters_numbers[quarter-1]+LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][23])
        for month_list in QuarterlyStatistics.statistics[quarter]:
            if month_list != 0 and month_list != "Label":
                QuarterlyStatistics.statistics[quarter][month_list]["Label"].setText(LANGUAGES[Session.Language]["Months"][month_number])
                month_number+=1
            elif month_list == 0:
                QuarterlyStatistics.statistics[quarter][0]["Label"].setText(LANGUAGES[Session.Language]["Account"]["Info"][6])
    
    YearlyStatistics.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][6])
    YearlyStatistics.copy_statistics.setText(LANGUAGES[Session.Language]["Account"]["Info"]["Statistics"][32])
    for month_list in YearlyStatistics.statistics:
        if month_list != 0:
            YearlyStatistics.statistics[month_list]["Label"].setText(LANGUAGES[Session.Language]["Months"][month_list])
        else:
            YearlyStatistics.statistics[0]["Label"].setText(LANGUAGES[Session.Language]["Account"]["Info"][6])


    for index,error in enumerate(errors_list):
        error.setText(LANGUAGES[Session.Language]["Errors"][index])
        error.button(QMessageBox.StandardButton.Ok).setText(LANGUAGES[Session.Language]["General management"][3])
        if error.button(QMessageBox.StandardButton.Cancel) != None:
            error.button(QMessageBox.StandardButton.Cancel).setText(LANGUAGES[Session.Language]["General management"][4])
    
    for category in Session.Categories:
        Session.Categories[category]["Add transaction"].setText(LANGUAGES[Session.Language]["Account"]["Transactions management"][0])
        Session.Categories[category]["Delete transaction"].setText(LANGUAGES[Session.Language]["Account"]["Transactions management"][1])
        Session.Categories[category]["Edit transaction"].setText(LANGUAGES[Session.Language]["Account"]["Transactions management"][2])
        Session.Categories[category]["Category data"].setHorizontalHeaderLabels((LANGUAGES[Session.Language]["Account"]["Info"][0],LANGUAGES[Session.Language]["Account"]["Info"][1],LANGUAGES[Session.Language]["Account"]["Info"][2]))
        total_value = Session.Categories[category]["Total value"].text().split(" ")[1]
        Session.Categories[category]["Total value"].setText(LANGUAGES[Session.Language]["Account"]["Info"][6]+total_value)
    
    MainWindow.account_current_balance.setText(LANGUAGES[Session.Language]["Account"]["Info"][3]+str(round(Session.Current_balance, 2)))
    Incomes = SettingsWindow.total_income.text().split(" ")[2]
    SettingsWindow.total_income.setText(LANGUAGES[Session.Language]["Account"]["Info"][7]+str(Incomes))
    Expenses = SettingsWindow.total_expense.text().split(" ")[2]
    SettingsWindow.total_expense.setText(LANGUAGES[Session.Language]["Account"]["Info"][8]+str(Expenses))
    SettingsWindow.account_created_date.setText(LANGUAGES[Session.Language]["Account"]["Info"][9]+Session.account.get_account_date())  


def change_language_add_account(language: int | str):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.Language = language
    else:
        Session.Language = language
    Session.update_user_config()

    AddAccountWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.Language))
    
    AddAccountWindow.message.setText(LANGUAGES[Session.Language]["Account"]["Account management"]["Messages"][0])
    AddAccountWindow.button.setText(LANGUAGES[Session.Language]["General management"][1])
    AddAccountWindow.window.setWindowTitle(LANGUAGES[Session.Language]["Windows"][1])
    AddAccountWindow.name.setPlaceholderText(LANGUAGES[Session.Language]["Account"][0])
    AddAccountWindow.surname.setPlaceholderText(LANGUAGES[Session.Language]["Account"][1])
    AddAccountWindow.current_balance.setPlaceholderText(LANGUAGES[Session.Language]["Account"][2])


def load_language(language):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.Language = language
    else:
        Session.Language = language
    Session.update_user_config()
    change_language()