from AppObjects.session import Session
from project_configuration import AVAILABLE_LANGUAGES
from languages import LANGUAGES
from GUI import *


def change_language():
    Language = LANGUAGES[Session.language]

    SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.language))

    MainWindow.account_current_balance.setText(Language["Account"]["Info"][3]+str(round(Session.current_balance, 2)))
    MainWindow.current_month.setText(Language["Months"][Session.current_month])
    MainWindow.Incomes_and_expenses.setTabText(0,Language["Account"]["Info"][4])
    MainWindow.Incomes_and_expenses.setTabText(1,Language["Account"]["Info"][5])
    MainWindow.add_incomes_category.setText(Language["Account"]["Category management"][0])
    MainWindow.add_expenses_category.setText(Language["Account"]["Category management"][0])
    MainWindow.statistics.setText(Language["Account"]["Info"]["Statistics"][0])
    MainWindow.mini_calculator_label.setText(Language["Mini calculator"][0])

    SettingsWindow.window.setWindowTitle(Language["Windows"][0])
    SettingsWindow.delete_account.setText(Language["Account"]["Account management"][0])
    SettingsWindow.add_account.setText(Language["Account"]["Account management"][1])
    SettingsWindow.rename_account.setText(Language["Account"]["Account management"][2])

    RenameAccountWindow.message.setText(Language["Account"]["Account management"]["Messages"][1])
    RenameAccountWindow.button.setText(Language["General management"][5])
    RenameAccountWindow.new_account_name.setPlaceholderText(Language["Account"]["Account management"][3])
    RenameAccountWindow.window.setWindowTitle(Language["Windows"][2])

    AddCategoryWindow.category_name.setPlaceholderText(Language["Account"]["Info"][0])
    AddCategoryWindow.button.setText(Language["General management"][1])
    AddCategoryWindow.window.setWindowTitle(Language["Account"]["Category management"][0])

    CategorySettingsWindow.delete_category.setText(Language["Account"]["Category management"][1])
    CategorySettingsWindow.rename_category.setText(Language["Account"]["Category management"][2])
    CategorySettingsWindow.copy_transactions.setText(Language["Account"]["Category management"][4])

    RenameCategoryWindow.new_category_name.setPlaceholderText(Language["Account"]["Category management"][3])
    RenameCategoryWindow.button.setText(Language["General management"][2])

    TransactionManagementWindow.button.setText(Language["General management"][5])
    TransactionManagementWindow.transaction_name.setPlaceholderText(Language["Account"]["Info"][0])
    TransactionManagementWindow.transaction_day.setPlaceholderText(Language["Account"]["Info"][1])
    TransactionManagementWindow.transaction_value.setPlaceholderText(Language["Account"]["Info"][2])

    StatisticsWindow.window.setWindowTitle(Language["Windows"][4])
    StatisticsWindow.monthly_statistics.setText(Language["Account"]["Info"]["Statistics"][1])
    StatisticsWindow.quarterly_statistics.setText(Language["Account"]["Info"]["Statistics"][2])
    StatisticsWindow.yearly_statistics.setText(Language["Account"]["Info"]["Statistics"][3])

    MonthlyStatistics.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][28])

    QuarterlyStatistics.window.setWindowTitle(Language["Windows"][5])
    QuarterlyStatistics.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][30])
    quarters_numbers = ["I","II","III","IV"]
    month_number = 1
    for quarter in QuarterlyStatistics.statistics:
        QuarterlyStatistics.statistics[quarter]["Label"].setText(quarters_numbers[quarter-1]+Language["Account"]["Info"]["Statistics"][23])
        for month_list in QuarterlyStatistics.statistics[quarter]:
            if month_list != 0 and month_list != "Label":
                QuarterlyStatistics.statistics[quarter][month_list]["Label"].setText(Language["Months"][month_number])
                month_number+=1
            elif month_list == 0:
                QuarterlyStatistics.statistics[quarter][0]["Label"].setText(Language["Account"]["Info"][6])
    
    YearlyStatistics.window.setWindowTitle(Language["Windows"][6])
    YearlyStatistics.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][32])
    for month_list in YearlyStatistics.statistics:
        if month_list != 0:
            YearlyStatistics.statistics[month_list]["Label"].setText(Language["Months"][month_list])
        else:
            YearlyStatistics.statistics[0]["Label"].setText(Language["Account"]["Info"][6])


    for index,error in enumerate(errors_list):
        error.setText(Language["Errors"][index])
        error.button(QMessageBox.StandardButton.Ok).setText(Language["General management"][3])
        if error.button(QMessageBox.StandardButton.Cancel) != None:
            error.button(QMessageBox.StandardButton.Cancel).setText(Language["General management"][4])
    
    for category in Session.categories:
        Session.categories[category].add_transaction.setText(Language["Account"]["Transactions management"][0])
        Session.categories[category].delete_transaction.setText(Language["Account"]["Transactions management"][1])
        Session.categories[category].edit_transaction.setText(Language["Account"]["Transactions management"][2])
        Session.categories[category].table_data.setHorizontalHeaderLabels((Language["Account"]["Info"][0], Language["Account"]["Info"][1], Language["Account"]["Info"][2]))
        total_value = Session.categories[category].total_value_label.text().split(" ")[1]
        Session.categories[category].total_value_label.setText(Language["Account"]["Info"][6] + total_value)
    
    MainWindow.account_current_balance.setText(Language["Account"]["Info"][3]+str(Session.current_balance))
    Incomes = SettingsWindow.total_income.text().split(" ")[2]
    SettingsWindow.total_income.setText(Language["Account"]["Info"][7]+str(Incomes))
    Expenses = SettingsWindow.total_expense.text().split(" ")[2]
    SettingsWindow.total_expense.setText(Language["Account"]["Info"][8]+str(Expenses))
    SettingsWindow.account_created_date.setText(Language["Account"]["Info"][9]+Session.account.get_account_date())  


def change_language_add_account(language: int | str):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.language = language
    else:
        Session.language = language
    Session.update_user_config()

    Language = LANGUAGES[Session.language]
    AddAccountWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.language))
    
    AddAccountWindow.message.setText(Language["Account"]["Account management"]["Messages"][0])
    AddAccountWindow.button.setText(Language["General management"][1])
    AddAccountWindow.window.setWindowTitle(Language["Windows"][1])
    AddAccountWindow.current_balance.setPlaceholderText(Language["Account"][0])
    AddAccountWindow.account_name.setPlaceholderText(Language["Account"][1])


def load_language(language):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.language = language
    else:
        Session.language = language
    Session.update_user_config()
    change_language()