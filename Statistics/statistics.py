from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias
from functools import partial
from datetime import date
from collections import defaultdict, Counter
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QPushButton

from languages import LanguageStructure
from project_configuration import MONTHS_DAYS, CATEGORY_TYPE
from DesktopQtToolkit.create_button import create_button

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ALIGN_V_CENTER, SHADOW_EFFECT_ARGUMENTS

if TYPE_CHECKING:
    from PySide6.QtWidgets import QListWidget
    from backend.models import Transaction
    from AppObjects.category import Category



logger = get_logger(__name__)
CountedTransactionsWithLowestValue:TypeAlias = dict[str, int]
CountedTransactionsWithHighestValue:TypeAlias = dict[str, int]

CategoriesWithHighestTotalValue:TypeAlias = dict[int, tuple[CountedTransactionsWithHighestValue, float, CountedTransactionsWithLowestValue, float]]
CategoriesWithLowestTotalValue:TypeAlias = dict[int, tuple[CountedTransactionsWithHighestValue, float, CountedTransactionsWithLowestValue, float]]
CategoriesTotalValues:TypeAlias = dict[int, float]


def get_min_and_max_categories(unsorted_categories:list[int], month:int) -> tuple[CategoriesWithHighestTotalValue, float, CategoriesWithLowestTotalValue, float, CategoriesTotalValues]:
    """Get categories with highest and lowest values based on transactions in month

        Arguments
        -------
            `unsorted_categories` (list): categories to sort
            `month` (int): month to get transactions
        Returns
        -------
            `tuple`:
            `Categories_with_highest_total_value` (dict) - all categories with highest value, if more than one category have the same top value\n
            `Categories_with_lowest_total_value` (dict) - all categories with lowest value, if more than one category have the same bottom value returns 0 categories if only 1 category exists\n
            `Categories_total_values` (dict) - all categories with their total value 
    """

    app_core = AppCore.instance()
    Categories_total_values:CategoriesTotalValues = {}

    for category in unsorted_categories:
        Categories_total_values[category] = round(app_core.db.statistics_query.get_monthly_transactions_sum(category, app_core.current_year, month), 2)

    highest_total_value = max(Categories_total_values.values())

    def _get_min_and_max_transactions(category:int, year:int, month:int) -> tuple[CountedTransactionsWithHighestValue, float, CountedTransactionsWithLowestValue, float]:
        """Get transactions with highest and lowest value in category

            Arguments
            ---------
                `category` (int): category to get transactions
                `year` (int): year to get transactions
                `month` (int): month to get transactions
            Returns
            -------
                `tuple`:
                    `transactions_with_highest_value` (dict) - transactions with highest value in category\n
                    `highest_transaction_value` (float) - highest transaction value in category\n
                    `transactions_with_lowest_value` (dict) - transactions with lowest value in category
                    `lowest_transaction_value` (float) - lowest transaction value in category
        """

        #Highest transactions
        highest_transaction_value = app_core.db.statistics_query.get_monthly_transactions_max_value(category, year, month)
        transactions_with_highest_value = app_core.db.statistics_query.get_monthly_transactions_by_value(category, year, month, highest_transaction_value)

        transactions_names = [str(transaction.name) for transaction in transactions_with_highest_value]
        counted_transactions_with_highest_value:CountedTransactionsWithHighestValue = Counter(transactions_names)
        
        #Lowest transactions
        lowest_transaction_value = app_core.db.statistics_query.get_monthly_transactions_min_value(category, year, month)
        transactions_with_lowest_value = app_core.db.statistics_query.get_monthly_transactions_by_value(category, year, month, lowest_transaction_value)

        transactions_names = [str(transaction.name) for transaction in transactions_with_lowest_value]
        counted_transactions_with_lowest_value:CountedTransactionsWithLowestValue = Counter(transactions_names)

        return (counted_transactions_with_highest_value, highest_transaction_value, counted_transactions_with_lowest_value, lowest_transaction_value)

    #Highest categories
    Categories_with_highest_total_value:CategoriesWithHighestTotalValue = {}
    for category in Categories_total_values:
        if Categories_total_values[category] == highest_total_value:
            transactions_statistic = _get_min_and_max_transactions(category, app_core.current_year, month)
            Categories_with_highest_total_value[category] = (*transactions_statistic,)

    #Lowest categories
    for category,total_value in Categories_total_values.copy().items():
        if total_value == 0:
            del Categories_total_values[category]

    Categories_with_lowest_total_value:CategoriesWithLowestTotalValue = {}
    lowest_total_value = 0.0
    if len(Categories_total_values) != 0:
        lowest_total_value = min([total_value for total_value in Categories_total_values.values() if total_value])
        
        for category in Categories_total_values:
            if Categories_total_values[category] == lowest_total_value and Categories_total_values[category] != highest_total_value:#If we have only one category don't add it to lowest categories (it is already highest)
                transactions_statistic = _get_min_and_max_transactions(category, app_core.current_year, month)
                Categories_with_lowest_total_value[category] = (*transactions_statistic,)

    return (Categories_with_highest_total_value, highest_total_value, Categories_with_lowest_total_value, lowest_total_value, Categories_total_values)


def add_statistic(statistic_list:QListWidget, statistic_data:tuple[CategoriesWithHighestTotalValue, float, CategoriesWithLowestTotalValue, float, CategoriesTotalValues], words:list[int]) -> None:
    """Add statistic to the list

        Arguments
        ---------
            `statistic_list` (QListWidget): list to add statistic
            `statistic_data` (tuple): statistic data to add
            `words` (list): language specific words to add statistic
    """

    def _add_highest_and_lowest_transactions(category:int, statistic:CategoriesWithHighestTotalValue|CategoriesWithLowestTotalValue) -> None:
        """Add highest and lowest transactions to the list

            Arguments
            ---------
                `category` (int): category to add transactions
                `statistic` (dict): statistic data to add transactions
        """

        #Highest transactions
        statistic_list.addItem("\n"+LanguageStructure.Statistics.get_translation(words[4]))
        for transaction_name, transaction_occurrences in statistic[category][0].items():
            if transaction_name == "":
                transaction_name = LanguageStructure.Statistics.get_translation(12)
            statistic_list.addItem(f"{transaction_name} - {statistic[category][1]}" if transaction_occurrences == 1 else f"{transaction_occurrences}x {transaction_name} - {statistic[category][1]}")
        
        #Lowest transactions
        if statistic[category][3] != statistic[category][1]:
            statistic_list.addItem("\n"+LanguageStructure.Statistics.get_translation(words[5]))
            for transaction_name, transaction_occurrences in statistic[category][2].items():

                if transaction_name == "":
                    transaction_name = LanguageStructure.Statistics.get_translation(12)
                statistic_list.addItem(f"{transaction_name} - {statistic[category][3]}" if transaction_occurrences == 1 else f"{transaction_occurrences}x {transaction_name} - {statistic[category][3]}")
    
    app_core = AppCore.instance()
    #Highest category
    if len(statistic_data[0]) == 1:
        most_category = [*statistic_data[0].keys()][0]
        statistic_list.addItem(LanguageStructure.Statistics.get_translation(words[0]) + app_core.categories[most_category].name+f"  ({statistic_data[1]})")
        _add_highest_and_lowest_transactions(most_category, statistic_data[0])

    elif len(statistic_data[0]) >= 2:#Highest categories
        highest_categories = [category for category in statistic_data[0]]
        highest_categories_names = str((*[app_core.categories[category].name for category in highest_categories],)).replace("'","")
        statistic_list.addItem(f"{LanguageStructure.Statistics.get_translation(words[1])}  {highest_categories_names}  ({statistic_data[1]})")

        for category in highest_categories:
            statistic_list.addItem(f"\n{LanguageStructure.Statistics.get_translation(16)} {app_core.categories[category].name}")
            _add_highest_and_lowest_transactions(category, statistic_data[0])

    #Lowest category
    if len(statistic_data[2]) == 1:
        least_category = [*statistic_data[2].keys()][0] 
        statistic_list.addItem("\n"+LanguageStructure.Statistics.get_translation(words[2])+app_core.categories[least_category].name+f" ({statistic_data[3]})")
        _add_highest_and_lowest_transactions(least_category, statistic_data[2])

    elif len(statistic_data[2]) >= 2:#Lowest categories
        lowest_categories = [category for category in statistic_data[2]]
        lowest_categories_names = str((*[app_core.categories[category].name for category in lowest_categories],)).replace("'","")
        statistic_list.addItem(f"\n\n{LanguageStructure.Statistics.get_translation(words[3])}  {lowest_categories_names}  ({statistic_data[3]})")

        for category in lowest_categories:
            statistic_list.addItem(f"\n{LanguageStructure.Statistics.get_translation(16)} {app_core.categories[category].name}")
            _add_highest_and_lowest_transactions(category, statistic_data[2])


def add_total_statistics(statistic:CategoriesTotalValues, words:list[int], total_statistics_list:QListWidget) -> None:
    """Add total statistics to the list

        Arguments
        ---------
            `statistic` (dict): statistic data to add
            `words` (list): language specific words to add statistic
            `total_statistics_list` (QListWidget): list to add statistic
    """        

    app_core = AppCore.instance()
    max_total_value  = max(total_value for total_value in statistic.values())
    min_total_value = min(total_value for total_value in statistic.values())

    max_category = [category for category,total_value in statistic.items() if total_value == max_total_value ][0]
    min_category = [category for category,total_value in statistic.items() if total_value == min_total_value ][0]

    total_statistics_list.addItem(LanguageStructure.Statistics.get_translation(words[0]) + app_core.categories[max_category].name + f" ({max_total_value}) \n")

    if min_category != max_category:
        total_statistics_list.addItem(LanguageStructure.Statistics.get_translation(words[1]) + app_core.categories[min_category].name + f" ({min_total_value})\n")

    sorted_categories = dict(sorted(statistic.items(), key=lambda category: category[1], reverse=True))
    for category, total_value in sorted_categories.items():
        total_statistics_list.addItem(f"{app_core.categories[category].name} - {total_value}")


def add_month_statistics(Incomes_categories:list[int], Expenses_categories:list[int], month_statistics:QListWidget, current_month:int) -> None:
    """Add month statistics to the list

        Arguments
        ---------
            `Incomes_categories` (dict): income categories to add statistics
            `Expenses_categories` (dict): expense categories to add statistics
            `month_statistics` (QListWidget): list to add statistic
            `current_month` (int): month to add statistics
    """

    Incomes_statistic = get_min_and_max_categories(Incomes_categories, current_month)
    Expenses_statistic = get_min_and_max_categories(Expenses_categories, current_month)

    total_income = round(sum([Incomes_statistic[4][total_value] for total_value in Incomes_statistic[4]]), 2)
    total_expense = round(sum([Expenses_statistic[4][total_value] for total_value in Expenses_statistic[4]]), 2)
    days_amount = MONTHS_DAYS[current_month-1] + (current_month == 2 and AppCore.instance().current_year % 4 == 0)#Add one day to February (29) if year is leap

    month_statistics.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
    month_statistics.addItem(LanguageStructure.Statistics.get_translation(5)+str(round(total_income/days_amount, 2))+"\n")

    month_statistics.addItem(LanguageStructure.Statistics.get_translation(6)+str(total_expense))
    month_statistics.addItem(LanguageStructure.Statistics.get_translation(7)+str(round(total_expense/days_amount, 2))+"\n")

    month_statistics.addItem(LanguageStructure.Statistics.get_translation(8)+str(round(total_income - total_expense, 2)))

    month_statistics.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(1))
    add_statistic(month_statistics, Incomes_statistic, [9,10,13,14,11,15])
    month_statistics.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(2))
    add_statistic(month_statistics, Expenses_statistic, [17,18,20,21,19,22])


def show_monthly_statistics() -> int:
    """This method is used to show the monthly statistics window."""

    app_core = AppCore.instance()
    WindowsRegistry.MonthlyStatistics.setWindowTitle(LanguageStructure.Months.get_translation(app_core.current_month))
    WindowsRegistry.MonthlyStatistics.statistics.clear()

    Incomes_categories = [category for category in app_core.categories if app_core.categories[category].type == "Incomes"]
    Expenses_categories = [category for category in app_core.categories if app_core.categories[category].type == "Expenses"]

    if len(app_core.categories) < 2 or len(Incomes_categories) < 1 or len(Expenses_categories) < 1:
        return WindowsRegistry.Messages.no_category.exec()
    
    Incomes_categories_have_transactions = any([bool(len(app_core.db.transaction_query.get_transactions_by_month(category, app_core.current_year, app_core.current_month))) for category in Incomes_categories])
    Expenses_categories_have_transactions = any([bool(len(app_core.db.transaction_query.get_transactions_by_month(category, app_core.current_year, app_core.current_month))) for category in Expenses_categories])

    if not (Incomes_categories_have_transactions and Expenses_categories_have_transactions):
        return WindowsRegistry.Messages.no_transactions.exec()
    
    add_month_statistics(Incomes_categories, Expenses_categories, WindowsRegistry.MonthlyStatistics.statistics, app_core.current_month)
    
    WindowsRegistry.StatisticsWindow.done(1)
    logger.debug(f"Monthly statistics window is shown. Current month: {LanguageStructure.Months.get_translation(app_core.current_month)}")
    return WindowsRegistry.MonthlyStatistics.exec()


def show_quarterly_statistics() -> int:
    """This method is used to show the quarterly statistics window."""

    app_core = AppCore.instance()
    #Clear quarters statistics
    for quarter in WindowsRegistry.QuarterlyStatistics.statistics.quarters:
        quarter.total_quarter_statistics.data.clear()
        for month in quarter.months:
            month.data.clear()

    Incomes_categories = [category for category in app_core.categories if app_core.categories[category].type == "Incomes"]
    Expenses_categories = [category for category in app_core.categories if app_core.categories[category].type == "Expenses"]

    if len(app_core.categories) < 2 or len(Expenses_categories) < 1 or len(Incomes_categories) < 1:
        return WindowsRegistry.Messages.no_category.exec()
    
    for quarter in WindowsRegistry.QuarterlyStatistics.statistics.quarters:
        Incomes_categories_total_values:CategoriesTotalValues = {}
        Expenses_categories_total_values:CategoriesTotalValues = {}

        categories_total_values:dict[int, list[float]] = {}
        for income_category in Incomes_categories:
            categories_total_values[income_category] = []

            for month in quarter.months:
                categories_total_values[income_category].append(round(app_core.db.statistics_query.get_monthly_transactions_sum(income_category, app_core.current_year, month.month_number), 2))
            Incomes_categories_total_values[income_category] = round(sum(categories_total_values[income_category]), 2)
        
        categories_total_values.clear()
        for expenses_category in Expenses_categories:
            categories_total_values[expenses_category] = []

            for month in quarter.months:
                categories_total_values[expenses_category].append(round(app_core.db.statistics_query.get_monthly_transactions_sum(expenses_category, app_core.current_year, month.month_number), 2))
            Expenses_categories_total_values[expenses_category] = round(sum(categories_total_values[expenses_category]), 2)

        #Entire quarter statistics
        total_income:float = round(sum(total_value for total_value in Incomes_categories_total_values.values()), 2)
        total_expense:float = round(sum(total_value for total_value in Expenses_categories_total_values.values()), 2)
        quarter_number = quarter.quarter_number
        days_amount = sum(MONTHS_DAYS[(quarter_number-1)*3:quarter_number*3]) + (quarter_number == 1 and app_core.current_year % 4 == 0)

        Total_statistic_list = quarter.total_quarter_statistics.data

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(5)+str(round(total_income/days_amount, 2))+"\n")

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(6)+str(total_expense))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(7)+str(round(total_expense/days_amount, 2))+"\n")

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(8)+str(round(total_income - total_expense, 2)))

        Total_statistic_list.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(1))
        add_total_statistics(Incomes_categories_total_values, [9,13], Total_statistic_list)

        Total_statistic_list.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(2))
        add_total_statistics(Expenses_categories_total_values, [17,20], Total_statistic_list)

        #Months statistics
        for month in quarter.months:
            Incomes_categories_have_transactions = any([bool(len(app_core.db.transaction_query.get_transactions_by_month(category, app_core.current_year, month.month_number))) for category in Incomes_categories])
            Expenses_categories_have_transactions = any([bool(len(app_core.db.transaction_query.get_transactions_by_month(category, app_core.current_year, month.month_number))) for category in Expenses_categories])

            if Incomes_categories_have_transactions and Expenses_categories_have_transactions:
                add_month_statistics(Incomes_categories, Expenses_categories, month.data, month.month_number)
            else:
                month.data.addItem(WindowsRegistry.Messages.no_transactions.text())

    WindowsRegistry.StatisticsWindow.done(1)
    logger.debug(f"Quarterly statistics window is shown. Current year: {app_core.current_year}")
    return WindowsRegistry.QuarterlyStatistics.exec()


def show_yearly_statistics() -> int:
    """This method is used to show the yearly statistics window."""

    app_core = AppCore.instance()
    #Clear yearly statistics
    WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data.clear()
    for ymonth in WindowsRegistry.YearlyStatistics.statistics.months:
        ymonth.data.clear()
    
    Incomes_categories = [category for category in app_core.categories if app_core.categories[category].type == "Incomes"]
    Expenses_categories = [category for category in app_core.categories if app_core.categories[category].type == "Expenses"]

    if len(app_core.categories) < 2 or len(Expenses_categories) < 1 or len(Incomes_categories) < 1:
        return WindowsRegistry.Messages.no_category.exec()
    
    Incomes_categories_total_values:CategoriesTotalValues = {}
    Expenses_categories_total_values:CategoriesTotalValues = {}

    categories_total_values:dict[int, list[float]] = {}
    for income_category in Incomes_categories:
        categories_total_values[income_category] = []

        for month in range(1,13):
            categories_total_values[income_category].append(round(app_core.db.statistics_query.get_monthly_transactions_sum(income_category, app_core.current_year, month), 2))
        Incomes_categories_total_values[income_category] = round(sum(categories_total_values[income_category]), 2)
    
    categories_total_values.clear()
    for expenses_category in Expenses_categories:
        categories_total_values[expenses_category] = []

        for month in range(1,13):
            categories_total_values[expenses_category].append(round(app_core.db.statistics_query.get_monthly_transactions_sum(expenses_category, app_core.current_year, month), 2))
        Expenses_categories_total_values[expenses_category] = round(sum(categories_total_values[expenses_category]), 2)

    #Entire year statistics
    total_income = round(sum(Incomes_categories_total_values.values()), 2)
    total_expense = round(sum(Expenses_categories_total_values.values()), 2)
    days_amount = 365 if app_core.current_year % 4 != 0 else 366# 365 days if year is not leap

    Total_statistic_list = WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(25)+str(round(total_income/12, 2)))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(24)+str(round(total_income/days_amount, 2))+"\n")

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(6)+str(total_expense))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(27)+str(round(total_expense/12, 2)))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(26)+str(round(total_expense/days_amount, 2))+"\n")

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(8)+f"{round(total_income - total_expense, 2)}")

    Total_statistic_list.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(1))
    add_total_statistics(Incomes_categories_total_values, [9,13], Total_statistic_list)

    Total_statistic_list.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(2))
    add_total_statistics(Expenses_categories_total_values, [17,20], Total_statistic_list)

    for ymonth in WindowsRegistry.YearlyStatistics.statistics.months:
        Incomes_categories_have_transactions = any([bool(len(app_core.db.transaction_query.get_transactions_by_month(category, app_core.current_year, ymonth.month_number))) for category in Incomes_categories])
        Expenses_categories_have_transactions = any([bool(len(app_core.db.transaction_query.get_transactions_by_month(category, app_core.current_year, ymonth.month_number))) for category in Expenses_categories])

        if Incomes_categories_have_transactions and Expenses_categories_have_transactions:
            add_month_statistics(Incomes_categories, Expenses_categories, ymonth.data, ymonth.month_number)
        else:
            ymonth.data.addItem(WindowsRegistry.Messages.no_transactions.text())

    WindowsRegistry.StatisticsWindow.done(1)
    logger.debug(f"Yearly statistics window is shown. Current year: {app_core.current_year}")
    return WindowsRegistry.YearlyStatistics.exec()
        

def show_custom_range_statistics_window() -> None:
    """This method is used to show the custom range statistics window. Where parameters like from and to date are set."""

    #Remove previous categories
    while WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.count():
        WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.takeAt(0).widget().setParent(None)#type: ignore[call-overload] #MyPy doesn't recognize that None works as detaching method

    while WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.count():
        WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.takeAt(0).widget().setParent(None)#type: ignore[call-overload]

    WindowsRegistry.CustomRangeStatistics.selected_categories_list.clear()
    WindowsRegistry.CustomRangeStatistics.selected_categories_data.clear()

    categories = sorted(AppCore.instance().categories.values(), key=lambda category: category.type)

    for category in categories:
        category_name = QLabel(category.name)
        category_name.setProperty("class", "light-text")

        remove_category_statistics_list = create_button("Remove", (100, 40))
        remove_category_statistics_list.setText(LanguageStructure.GeneralManagement.get_translation(0))
        remove_category_statistics_list.setDisabled(True)

        add_category_statistics_list = create_button("Add", (100, 40))
        add_category_statistics_list.setText(LanguageStructure.GeneralManagement.get_translation(1))

        category_layout = QHBoxLayout()
        category_layout.addWidget(category_name, alignment=ALIGN_H_CENTER)
        category_layout.addWidget(add_category_statistics_list, alignment=ALIGNMENT.AlignRight)
        category_layout.addWidget(remove_category_statistics_list, alignment=ALIGNMENT.AlignRight)

        category_wrapper = QWidget()
        category_wrapper.setLayout(category_layout)
        category_wrapper.setProperty("class", "category_list_item")
        category_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(category_wrapper, **SHADOW_EFFECT_ARGUMENTS))

        if category.type == CATEGORY_TYPE[0]:#Income
            category_type_translate = LanguageStructure.MainWindow.get_translation(1)
            WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.addWidget(category_wrapper, alignment=ALIGN_V_CENTER)
        else:
            category_type_translate = LanguageStructure.MainWindow.get_translation(2)
            WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.addWidget(category_wrapper, alignment=ALIGN_V_CENTER)

        remove_category_statistics_list.clicked.connect(partial(remove_category_from_statistics_list, category, add_category_statistics_list, remove_category_statistics_list))
        add_category_statistics_list.clicked.connect(partial(add_category_to_statistics_list, category, category_type_translate, remove_category_statistics_list, add_category_statistics_list))
    
    WindowsRegistry.StatisticsWindow.done(1)
    WindowsRegistry.CustomRangeStatistics.exec()


def add_category_to_statistics_list(category:Category, category_type_translate:str, remove_button:QPushButton, add_button:QPushButton) -> None:
    """Add category to the custom range statistics list

        Arguments
        ---------
            `category` (Category): category to add to selected categories
            `category_type_translate` (str): translated category type
            `remove_button` (QPushButton): enable button to remove category
            `add_button` (QPushButton): disable button to add category
    """

    #Reset selected categories
    WindowsRegistry.CustomRangeStatistics.selected_categories_list.clear()

    WindowsRegistry.CustomRangeStatistics.selected_categories_data[category.id] = (category, category_type_translate)

    selected_categories = WindowsRegistry.CustomRangeStatistics.selected_categories_data

    for iteration, selected_category in enumerate(selected_categories):
        WindowsRegistry.CustomRangeStatistics.selected_categories_list.addItem(
            f"{iteration+1}. {selected_categories[selected_category][0].name} ({selected_categories[selected_category][1]})"
        )
    remove_button.setDisabled(False)
    add_button.setDisabled(True)


def add_all_categories_to_statistics_list(sender_button:QPushButton) -> None:
    """Add all categories to the custom range statistics list

        Arguments
        ---------
            `sender_button` (QPushButton): button that was clicked
    """

    if sender_button is WindowsRegistry.CustomRangeStatistics.add_all_incomes_categories:
        for category_wrapper_index in range(WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.count()):
            category_wrapper = WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.itemAt(category_wrapper_index).widget()

            for widget in category_wrapper.children():
                if isinstance(widget, QPushButton) and widget.text() == LanguageStructure.GeneralManagement.get_translation(1):
                    widget.click()

    elif sender_button is WindowsRegistry.CustomRangeStatistics.add_all_expenses_categories:
        for category_wrapper_index in range(WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.count()):
            category_wrapper = WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.itemAt(category_wrapper_index).widget()

            for widget in category_wrapper.children():
                if isinstance(widget, QPushButton) and widget.text() == LanguageStructure.GeneralManagement.get_translation(1):
                    widget.click()


def remove_category_from_statistics_list(category:Category, add_button:QPushButton, remove_button:QPushButton) -> None:
    """Remove category from the custom range statistics list

        Arguments
        ---------
            `category` (Category): category to remove from selected categories
            `add_button` (QPushButton): enable button to add category
            `remove_button` (QPushButton): disable button to remove category
    """

    #Reset selected categories
    WindowsRegistry.CustomRangeStatistics.selected_categories_list.clear()
    del WindowsRegistry.CustomRangeStatistics.selected_categories_data[category.id]

    selected_categories = WindowsRegistry.CustomRangeStatistics.selected_categories_data

    for iteration, selected_category in enumerate(selected_categories):
        WindowsRegistry.CustomRangeStatistics.selected_categories_list.addItem(
            f"{iteration+1}. {selected_categories[selected_category][0].name} ({selected_categories[selected_category][1]})"
        )
    remove_button.setDisabled(True)
    add_button.setDisabled(False)


def remove_all_categories_from_statistics_list(sender_button:QPushButton) -> None:
    """Remove all categories from the custom range statistics list

        Arguments
        ---------
            `sender_button` (QPushButton): button that was clicked
    """

    if sender_button is WindowsRegistry.CustomRangeStatistics.remove_all_incomes_categories:
        for category_wrapper_index in range(WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.count()):
            category_wrapper = WindowsRegistry.CustomRangeStatistics.incomes_categories_list_layout.itemAt(category_wrapper_index).widget()

            for widget in category_wrapper.children():
                if isinstance(widget, QPushButton) and widget.text() == LanguageStructure.GeneralManagement.get_translation(0):
                    widget.click()
    
    elif sender_button is WindowsRegistry.CustomRangeStatistics.remove_all_expenses_categories:
        for category_wrapper_index in range(WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.count()):
            category_wrapper = WindowsRegistry.CustomRangeStatistics.expenses_categories_list_layout.itemAt(category_wrapper_index).widget()

            for widget in category_wrapper.children():
                if isinstance(widget, QPushButton) and widget.text() == LanguageStructure.GeneralManagement.get_translation(0):
                    widget.click()


def show_custom_range_statistics_view() -> int:
    """This method is used to show the actual custom range statistics."""

    #Reset statistics and transactions list
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.clear()
    WindowsRegistry.CustomRangeStatisticsView.transactions_list.clear()

    from_date = WindowsRegistry.CustomRangeStatistics.from_date.date()
    to_date = WindowsRegistry.CustomRangeStatistics.to_date.date()

    if from_date.daysTo(to_date) <= 0:
        return WindowsRegistry.Messages.wrong_date.exec()
    
    if len(WindowsRegistry.CustomRangeStatistics.selected_categories_data) == 0:
        return WindowsRegistry.Messages.no_selected_category.exec()
    
    date_difference = date(to_date.year(), to_date.month(), to_date.day()) - date(from_date.year(), from_date.month(), from_date.day()) 
    days_amount = date_difference.days

    from_date_number = from_date.year()*1000 + from_date.month()*100 + from_date.day()
    to_date_number = to_date.year()*1000 + to_date.month()*100 + to_date.day()

    Incomes_categories = [category[0] for category in WindowsRegistry.CustomRangeStatistics.selected_categories_data.values() if category[0].type == "Incomes"]
    Expenses_categories = [category[0] for category in WindowsRegistry.CustomRangeStatistics.selected_categories_data.values() if category[0].type == "Expenses"]

    all_transactions = AppCore.instance().db.statistics_query.get_transactions_by_range(list(map(lambda category: category.id, Incomes_categories+Expenses_categories)), from_date_number, to_date_number)
    categorized_transactions:defaultdict[int, list[Transaction]] = defaultdict(list)
    for transaction in all_transactions:
        categorized_transactions[transaction.category_id].append(transaction)

    Incomes_categories_total_values = {}
    Expenses_categories_total_values = {}

    Incomes_categories_transactions:dict[Category, list[Transaction]] = {}
    Expenses_categories_transactions:dict[Category, list[Transaction]] = {}

    for income_cateogry in Incomes_categories:
        category_transactions = categorized_transactions[income_cateogry.id]
        total_value = round(sum([transaction.value for transaction in category_transactions]), 2)

        Incomes_categories_transactions[income_cateogry] = sorted(category_transactions, key=lambda transaction: date(transaction.year, transaction.month, transaction.day))
        Incomes_categories_total_values[income_cateogry.id] = total_value
        
    for expense_category in Expenses_categories:
        category_transactions = categorized_transactions[expense_category.id]
        total_value = round(sum([transaction.value for transaction in category_transactions]), 2)

        Expenses_categories_transactions[expense_category] = sorted(category_transactions, key=lambda transaction: date(transaction.year, transaction.month, transaction.day))
        Expenses_categories_total_values[expense_category.id] = total_value
    
    total_income = round(sum(total_value for total_value in Incomes_categories_total_values.values()), 2)
    total_expense = round(sum(total_value for total_value in Expenses_categories_total_values.values()), 2)

    #Custom range statistics
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(LanguageStructure.Statistics.get_translation(24)+str(round(total_income/days_amount, 2))+"\n")

    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(LanguageStructure.Statistics.get_translation(6)+str(total_expense))
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(LanguageStructure.Statistics.get_translation(26)+str(round(total_expense/days_amount, 2))+"\n")

    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(LanguageStructure.Statistics.get_translation(8)+f"{round(total_income - total_expense, 2)}")

    if len(Incomes_categories):
        WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(1))
        add_total_statistics(Incomes_categories_total_values, [9,13], WindowsRegistry.CustomRangeStatisticsView.statistics_list)

    if len(Expenses_categories):
        WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem("\n\n"+LanguageStructure.MainWindow.get_translation(2))
        add_total_statistics(Expenses_categories_total_values, [17,20], WindowsRegistry.CustomRangeStatisticsView.statistics_list)
    
    #Transactions list
    if len(Incomes_categories_transactions):
        WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(LanguageStructure.MainWindow.get_translation(1)+"\n\n")
        for category, category_transactions in Incomes_categories_transactions.items():
            WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem("\n"+category.name+"\n")

            for transaction in category_transactions:
                day = transaction.day                
                month = transaction.month

                WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(f"{day:02}/{month:02}/{transaction.year}\t{transaction.value}\t{transaction.name}")
    
    if len(Expenses_categories_transactions):
        WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem("\n\n\n"+LanguageStructure.MainWindow.get_translation(2)+"\n\n")
        for category, category_transactions in Expenses_categories_transactions.items():
            WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem("\n"+category.name+"\n")

            for transaction in category_transactions:
                day = transaction.day                
                month = transaction.month

                WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(f"{day:02}/{month:02}/{transaction.year}\t{transaction.value}\t{transaction.name}")
        
    logger.debug(f"Custom range statistics window is shown. From date: {from_date} To date: {to_date}")
    return WindowsRegistry.CustomRangeStatisticsView.exec()
