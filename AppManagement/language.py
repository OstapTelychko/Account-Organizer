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
    Windows = Language["Windows"]

    SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.language))

    MainWindow.account_current_balance.setText(Windows["Main"][0]+str(round(Session.current_balance, 2)))
    MainWindow.current_month.setText(Language["Months"][Session.current_month])
    MainWindow.Incomes_and_expenses.setTabText(0, Windows["Main"][1])
    MainWindow.Incomes_and_expenses.setTabText(1, Windows["Main"][2])
    MainWindow.add_incomes_category.setText(Windows["Main"]["Categories"][0])
    MainWindow.add_expenses_category.setText(Windows["Main"]["Categories"][0])
    MainWindow.statistics.setText(Windows["Statistics"][0])
    MainWindow.mini_calculator_label.setText(Windows["Main"]["Mini calculator"][0])

    SettingsWindow.window.setWindowTitle(Windows["Settings"][0])
    SettingsWindow.delete_account.setText(Windows["Settings"]["Account"][0])
    SettingsWindow.add_account.setText(Windows["Settings"]["Account"][1])
    SettingsWindow.rename_account.setText(Windows["Settings"]["Account"][2])
    Incomes = SettingsWindow.total_income.text().split(":")[1].replace(" ","")
    SettingsWindow.total_income.setText(Windows["Statistics"][4]+str(Incomes))
    Expenses = SettingsWindow.total_expense.text().split(":")[1].replace(" ","")
    SettingsWindow.total_expense.setText(Windows["Statistics"][6]+str(Expenses))
    SettingsWindow.account_created_date.setText(Windows["Settings"][1] + str(Session.db.get_account().created_date))
    SettingsWindow.db_management.setText(Windows["Settings"]["DB management"][0])
    
    SettingsWindow.app_version.setText(Windows["Settings"][2] + ".".join(map(str, Session.app_version)))
                                       
    RenameAccountWindow.message.setText(Windows["Settings"]["Account"]["Messages"][1])
    RenameAccountWindow.button.setText(Language["General management"][5])
    RenameAccountWindow.new_account_name.setPlaceholderText(Windows["Settings"]["Account"][3])
    RenameAccountWindow.window.setWindowTitle(Windows["Settings"]["Account"][2])

    AddCategoryWindow.category_name.setPlaceholderText(Windows["Main"]["Transactions"][0])
    AddCategoryWindow.button.setText(Language["General management"][1])
    AddCategoryWindow.window.setWindowTitle(Windows["Main"]["Categories"][0])

    CategorySettingsWindow.delete_category.setText(Windows["Main"]["Categories"][1])
    CategorySettingsWindow.rename_category.setText(Windows["Main"]["Categories"][2])
    CategorySettingsWindow.copy_transactions.setText(Windows["Main"]["Categories"][4])
    CategorySettingsWindow.change_category_position.setText(Windows["Main"]["Categories"][9])

    ChangeCategoryPositionWindow.enter_new_position.setText(Language["General management"][6])

    RenameCategoryWindow.new_category_name.setPlaceholderText(Windows["Main"]["Categories"][3])
    RenameCategoryWindow.button.setText(Language["General management"][2])

    TransactionManagementWindow.button.setText(Language["General management"][5])
    TransactionManagementWindow.transaction_name.setPlaceholderText(Windows["Main"]["Transactions"][0])
    TransactionManagementWindow.transaction_day.setPlaceholderText(Windows["Main"]["Transactions"][1])
    TransactionManagementWindow.transaction_value.setPlaceholderText(Windows["Main"]["Transactions"][2])

    StatisticsWindow.window.setWindowTitle(Windows["Statistics"][0])
    StatisticsWindow.monthly_statistics.setText(Windows["Statistics"][1])
    StatisticsWindow.quarterly_statistics.setText(Windows["Statistics"][2])
    StatisticsWindow.yearly_statistics.setText(Windows["Statistics"][3])
    StatisticsWindow.custom_range_statistics.setText(Windows["Statistics"][34])

    MonthlyStatistics.copy_statistics.setText(Windows["Statistics"][28])

    QuarterlyStatistics.window.setWindowTitle(Windows["Statistics"][2])
    QuarterlyStatistics.copy_statistics.setText(Windows["Statistics"][30])
    quarters_numbers = ["I","II","III","IV"]
    for quarter in QuarterlyStatistics.statistics.quarters:
        quarter.label.setText(quarters_numbers[quarter.quarter_number-1]+Windows["Statistics"][23])
        quarter.total_quarter_statistics.label.setText(Windows["Main"]["Categories"][10])

        for month in quarter.months:
            month.label.setText(Language["Months"][month.month_number])
    
    YearlyStatistics.window.setWindowTitle(Windows["Statistics"][3])
    YearlyStatistics.copy_statistics.setText(Windows["Statistics"][32])
    YearlyStatistics.statistics.total_year_statistics.label.setText(Windows["Main"]["Categories"][10])
    for month in YearlyStatistics.statistics.months:
        month.label.setText(Language["Months"][month.month_number])
    
    CustomRangeStatistics.window.setWindowTitle(Windows["Statistics"][34])
    CustomRangeStatistics.show_statistics.setText(Windows["Statistics"][0])
    CustomRangeStatisticsView.window.setWindowTitle(Windows["Statistics"][34])
    CustomRangeStatisticsView.copy_statistics.setText(Windows["Statistics"][35])
    CustomRangeStatisticsView.copy_transactions.setText(Windows["Statistics"][37])


    for index, message in enumerate(MainWindow.message_windows.values()):
        message.setText(Language["Messages"][index])
        message.button(QMessageBox.StandardButton.Ok).setText(Language["General management"][3])
        if message.button(QMessageBox.StandardButton.Cancel) != None:
            message.button(QMessageBox.StandardButton.Cancel).setText(Language["General management"][4])
    
    for category in Session.categories:
        Session.categories[category].delete_transaction.setText(Language["General management"][0])
        Session.categories[category].add_transaction.setText(Language["General management"][1])
        Session.categories[category].edit_transaction.setText(Language["General management"][7])
        Session.categories[category].table_data.setHorizontalHeaderLabels((Windows["Main"]["Transactions"][0], Windows["Main"]["Transactions"][1], Windows["Main"]["Transactions"][2]))
        total_value = Session.categories[category].total_value_label.text().split(" ")[1]
        Session.categories[category].total_value_label.setText(Windows["Main"]["Categories"][10] + total_value)
    
    MainWindow.account_current_balance.setText(Windows["Main"][0]+str(Session.current_balance))


def change_language_during_add_account(language: int | str):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.language = language
    else:
        Session.language = language
    Session.update_user_config()

    Language = LANGUAGES[Session.language]
    AddAccountWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(Session.language))
    
    AddAccountWindow.message.setText(Language["Windows"]["Settings"]["Account"]["Messages"][0])
    AddAccountWindow.button.setText(Language["General management"][1])
    AddAccountWindow.window.setWindowTitle(Language["Windows"]["Settings"]["Account"][1])
    AddAccountWindow.current_balance.setPlaceholderText(Language["Windows"]["Settings"]["Account"][4])
    AddAccountWindow.account_name.setPlaceholderText(Language["Windows"]["Settings"]["Account"][5])


def load_language(language):
    if type(language) is int:# var language is a string when the language is loaded from the user config
        language = AVAILABLE_LANGUAGES[language]
        Session.language = language
    else:
        Session.language = language
    Session.update_user_config()
    change_language()