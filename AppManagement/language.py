from PySide6.QtWidgets import QMessageBox

from AppObjects.session import Session
from project_configuration import AVAILABLE_LANGUAGES
from languages import LANGUAGES

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, RenameCategoryWindow, ChangeCategoryPositionWindow
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatistics, CustomRangeStatisticsView
from GUI.windows.transaction import TransactionManagementWindow



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
    Incomes = SettingsWindow.total_income.text().split(" ")[2]
    SettingsWindow.total_income.setText(Language["Account"]["Info"][7]+str(Incomes))
    Expenses = SettingsWindow.total_expense.text().split(" ")[2]
    SettingsWindow.total_expense.setText(Language["Account"]["Info"][8]+str(Expenses))
    SettingsWindow.account_created_date.setText(Language["Account"]["Info"][9] + str(Session.db.get_account().created_date))
    SettingsWindow.db_management.setText(Language["Account"]["DB management"][0])
    
    SettingsWindow.app_version.setText(Language["Account"]["Info"][10] + ".".join(map(str, Session.app_version)))
                                       
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
    CategorySettingsWindow.change_category_position.setText(Language["Account"]["Category management"][9])

    ChangeCategoryPositionWindow.enter_new_position.setText(Language["General management"][6])

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
    StatisticsWindow.custom_range_statistics.setText(Language["Account"]["Info"]["Statistics"][34])

    MonthlyStatistics.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][28])

    QuarterlyStatistics.window.setWindowTitle(Language["Windows"][5])
    QuarterlyStatistics.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][30])
    quarters_numbers = ["I","II","III","IV"]
    for quarter in QuarterlyStatistics.statistics.quarters:
        quarter.label.setText(quarters_numbers[quarter.quarter_number-1]+Language["Account"]["Info"]["Statistics"][23])
        quarter.total_quarter_statistics.label.setText(Language["Account"]["Info"][6])

        for month in quarter.months:
            month.label.setText(Language["Months"][month.month_number])
    
    YearlyStatistics.window.setWindowTitle(Language["Windows"][6])
    YearlyStatistics.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][32])
    YearlyStatistics.statistics.total_year_statistics.label.setText(Language["Account"]["Info"][6])
    for month in YearlyStatistics.statistics.months:
        month.label.setText(Language["Months"][month.month_number])
    
    CustomRangeStatistics.window.setWindowTitle(Language["Account"]["Info"]["Statistics"][34])
    CustomRangeStatistics.show_statistics.setText(Language["Account"]["Info"]["Statistics"][0])
    CustomRangeStatisticsView.window.setWindowTitle(Language["Account"]["Info"]["Statistics"][34])
    CustomRangeStatisticsView.copy_statistics.setText(Language["Account"]["Info"]["Statistics"][35])
    CustomRangeStatisticsView.copy_transactions.setText(Language["Account"]["Info"]["Statistics"][37])


    for index, message in enumerate(MainWindow.message_windows.values()):
        message.setText(Language["Errors"][index])
        message.button(QMessageBox.StandardButton.Ok).setText(Language["General management"][3])
        if message.button(QMessageBox.StandardButton.Cancel) != None:
            message.button(QMessageBox.StandardButton.Cancel).setText(Language["General management"][4])
    
    for category in Session.categories:
        Session.categories[category].add_transaction.setText(Language["Account"]["Transactions management"][0])
        Session.categories[category].delete_transaction.setText(Language["Account"]["Transactions management"][1])
        Session.categories[category].edit_transaction.setText(Language["Account"]["Transactions management"][2])
        Session.categories[category].table_data.setHorizontalHeaderLabels((Language["Account"]["Info"][0], Language["Account"]["Info"][1], Language["Account"]["Info"][2]))
        total_value = Session.categories[category].total_value_label.text().split(" ")[1]
        Session.categories[category].total_value_label.setText(Language["Account"]["Info"][6] + total_value)
    
    MainWindow.account_current_balance.setText(Language["Account"]["Info"][3]+str(Session.current_balance))


def change_language_during_add_account(language: int | str):
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