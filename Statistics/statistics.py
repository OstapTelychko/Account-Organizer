from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias, cast
from datetime import date, timedelta
from calendar import monthrange
from collections import defaultdict, Counter
from textwrap import dedent

from languages import LanguageStructure

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry


if TYPE_CHECKING:
    from PySide6.QtWidgets import QListWidget
    from backend.models import Transaction
    from AppObjects.category import Category




logger = get_logger(__name__)
CountedTransactionsWithLowestValue:TypeAlias = dict[str, int]
CountedTransactionsWithHighestValue:TypeAlias = dict[str, int]

CategoriesWithHighestTotalValue:TypeAlias = dict[int, tuple[
    CountedTransactionsWithHighestValue, float, CountedTransactionsWithLowestValue, float
]]
CategoriesWithLowestTotalValue:TypeAlias = dict[int, tuple[
    CountedTransactionsWithHighestValue, float, CountedTransactionsWithLowestValue, float
]]
CategoriesTotalValues:TypeAlias = dict[int, float]


def get_min_and_max_categories(unsorted_categories:list[int], month:int) -> tuple[
    CategoriesWithHighestTotalValue, float, CategoriesWithLowestTotalValue, float, CategoriesTotalValues
]:
    """Get categories with highest and lowest values based on transactions in month

        Arguments
        -------
            `unsorted_categories` (list): categories to sort
            `month` (int): month to get transactions
        Returns
        -------
            `Categories_with_highest_total_value` (dict): - all categories with highest value,\
                if more than one category have the same top value
            `Categories_with_lowest_total_value` (dict): - all categories with lowest value,\
                if more than one category have the same bottom value returns 0 categories if only 1 category exists<br/>
            `Categories_total_values` (dict): - all categories with their total value
    """

    app_core = AppCore.instance()
    Categories_total_values:CategoriesTotalValues = {}
    categories_sums = app_core.db.statistics_query.get_categories_monthly_transactions_sum(
        unsorted_categories, app_core.current_year, month
    )
    for category, total in zip(unsorted_categories, categories_sums):
        Categories_total_values[category] = round(total, 2)

    highest_total_value = max(Categories_total_values.values())

    def _get_min_and_max_transactions(category:int, year:int, month:int) -> tuple[
        CountedTransactionsWithHighestValue, float, CountedTransactionsWithLowestValue, float
    ]:
        """Get transactions with highest and lowest value in category

            Arguments
            ---------
                `category` (int): category to get transactions
                `year` (int): year to get transactions
                `month` (int): month to get transactions
            Returns
            -------
                `tuple`:
                    `transactions_with_highest_value` (dict) - transactions with highest value in category<br/>
                    `highest_transaction_value` (float) - highest transaction value in category<br/>
                    `transactions_with_lowest_value` (dict) - transactions with lowest value in category<br/>
                    `lowest_transaction_value` (float) - lowest transaction value in category
        """

        #Highest transactions
        highest_transaction_value = app_core.db.statistics_query.get_monthly_transactions_max_value(category, year, month)
        transactions_with_highest_value = app_core.db.statistics_query.get_monthly_transactions_by_value(
            category, year, month, highest_transaction_value
        )

        transactions_names = [str(transaction.name) for transaction in transactions_with_highest_value]
        counted_transactions_with_highest_value:CountedTransactionsWithHighestValue = Counter(transactions_names)
        
        #Lowest transactions
        lowest_transaction_value = app_core.db.statistics_query.get_monthly_transactions_min_value(category, year, month)
        transactions_with_lowest_value = app_core.db.statistics_query.get_monthly_transactions_by_value(
            category, year, month, lowest_transaction_value
        )

        transactions_names = [str(transaction.name) for transaction in transactions_with_lowest_value]
        counted_transactions_with_lowest_value:CountedTransactionsWithLowestValue = Counter(transactions_names)

        return counted_transactions_with_highest_value,\
            highest_transaction_value,\
            counted_transactions_with_lowest_value,\
            lowest_transaction_value

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


def add_statistic(statistic_list:QListWidget, statistic_data:tuple[
        CategoriesWithHighestTotalValue, float, CategoriesWithLowestTotalValue, float, CategoriesTotalValues],
        words:list[int]
) -> None:
    """Add statistic to the list

        Arguments
        ---------
            `statistic_list` (QListWidget): list to add statistic
            `statistic_data` (tuple): statistic data to add
            `words` (list): language specific words to add statistic
    """

    def _add_highest_and_lowest_transactions(
            category:int,
            statistic:CategoriesWithHighestTotalValue|CategoriesWithLowestTotalValue
        ) -> None:
        """Add highest and lowest transactions to the list

            Arguments
            ---------
                `category` (int): category to add transactions
                `statistic` (dict): statistic data to add transactions
        """

        #Highest transactions
        statistic_list.addItem("<br/>"+LanguageStructure.Statistics.get_translation(words[4]))
        for transaction_name, transaction_occurrences in statistic[category][0].items():
            if transaction_name == "":
                transaction_name = LanguageStructure.Statistics.get_translation(12)
            if transaction_occurrences == 1:
                statistic_list.addItem(f"{transaction_name} - {statistic[category][1]}")
            else:
                statistic_list.addItem(f"{transaction_occurrences}x {transaction_name} - {statistic[category][1]}")
        
        #Lowest transactions
        if statistic[category][3] != statistic[category][1]:
            statistic_list.addItem("<br/>"+LanguageStructure.Statistics.get_translation(words[5]))
            for transaction_name, transaction_occurrences in statistic[category][2].items():

                if transaction_name == "":
                    transaction_name = LanguageStructure.Statistics.get_translation(12)
                if transaction_occurrences == 1:
                    statistic_list.addItem(f"{transaction_name} - {statistic[category][3]}")
                else:
                    statistic_list.addItem(f"{transaction_occurrences}x {transaction_name} - {statistic[category][3]}")

    app_core = AppCore.instance()
    #Highest category
    if len(statistic_data[0]) == 1:
        most_category = [*statistic_data[0].keys()][0]
        statistic_list.addItem(
            LanguageStructure.Statistics.get_translation(words[0])
            + app_core.categories[most_category].name+
            f"  ({statistic_data[1]})"
        )
        _add_highest_and_lowest_transactions(most_category, statistic_data[0])

    elif len(statistic_data[0]) >= 2:#Highest categories
        highest_categories = [category for category in statistic_data[0]]
        highest_categories_names = str((*[app_core.categories[category].name for category in highest_categories],)).replace("'","")
        statistic_list.addItem(
            f"{LanguageStructure.Statistics.get_translation(words[1])}  {highest_categories_names}  ({statistic_data[1]})"
        )

        for category in highest_categories:
            statistic_list.addItem(f"<br/>{LanguageStructure.Statistics.get_translation(16)} {app_core.categories[category].name}")
            _add_highest_and_lowest_transactions(category, statistic_data[0])

    #Lowest category
    if len(statistic_data[2]) == 1:
        least_category = [*statistic_data[2].keys()][0] 
        statistic_list.addItem(
            f"<br/>{LanguageStructure.Statistics.get_translation(words[2])}"
            f"{app_core.categories[least_category].name} ({statistic_data[3]})"
        )
        _add_highest_and_lowest_transactions(least_category, statistic_data[2])

    elif len(statistic_data[2]) >= 2:#Lowest categories
        lowest_categories = [category for category in statistic_data[2]]
        lowest_categories_names = str((*[app_core.categories[category].name for category in lowest_categories],)).replace("'","")
        statistic_list.addItem(f"<br/><br/>{LanguageStructure.Statistics.get_translation(words[3])}  {lowest_categories_names}  ({statistic_data[3]})")

        for category in lowest_categories:
            statistic_list.addItem(f"<br/>{LanguageStructure.Statistics.get_translation(16)} {app_core.categories[category].name}")
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

    total_statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(words[0])
         + app_core.categories[max_category].name +
        f" ({max_total_value}) <br/>"
    )

    if min_category != max_category:
        total_statistics_list.addItem(
            LanguageStructure.Statistics.get_translation(words[1])
            + app_core.categories[min_category].name
            + f" ({min_total_value})<br/>"
        )

    sorted_categories = dict(sorted(statistic.items(), key=lambda category: category[1], reverse=True))
    for category, total_value in sorted_categories.items():
        total_statistics_list.addItem(f"{app_core.categories[category].name} - {total_value}")


def add_month_statistics(
        Incomes_categories:list[int],
        Expenses_categories:list[int],
        month_statistics:QListWidget,
        current_month:int
    ) -> None:
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
    _, days_amount = monthrange(AppCore.instance().current_year, current_month)

    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(4)}{total_income}")
    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(5)}{round(total_income/days_amount, 2)}<br/>")

    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(6)}{total_expense}")
    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(7)}{round(total_expense/days_amount, 2)}<br/>")

    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(8)}{round(total_income - total_expense, 2)}")

    month_statistics.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(1))
    add_statistic(month_statistics, Incomes_statistic, [9,10,13,14,11,15])
    month_statistics.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(2))
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

    Incomes_categories_have_transactions = app_core.db.transaction_query.check_categories_have_transactions(
        Incomes_categories, app_core.current_year, app_core.current_month)
    Expenses_categories_have_transactions = app_core.db.transaction_query.check_categories_have_transactions(
        Expenses_categories, app_core.current_year, app_core.current_month)

    if not (Incomes_categories_have_transactions and Expenses_categories_have_transactions):
        return WindowsRegistry.Messages.no_transactions.exec()
    
    add_month_statistics(
        Incomes_categories, Expenses_categories, WindowsRegistry.MonthlyStatistics.statistics, app_core.current_month
    )
    
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

        categories_total_values:dict[int, list[float]] = app_core.db.statistics_query.get_categories_monthly_transactions_sum_by_months(
            Incomes_categories, app_core.current_year, [month.month_number for month in quarter.months])
        for income_category in Incomes_categories:
            Incomes_categories_total_values[income_category] = round(sum(categories_total_values[income_category]), 2)
        
        categories_total_values.clear()
        categories_total_values = app_core.db.statistics_query.get_categories_monthly_transactions_sum_by_months(
            Expenses_categories, app_core.current_year, [month.month_number for month in quarter.months])
        for expenses_category in Expenses_categories:
            Expenses_categories_total_values[expenses_category] = round(sum(categories_total_values[expenses_category]), 2)

        #Entire quarter statistics
        total_income:float = round(sum(total_value for total_value in Incomes_categories_total_values.values()), 2)
        total_expense:float = round(sum(total_value for total_value in Expenses_categories_total_values.values()), 2)

        quarter_number = quarter.quarter_number
        months_in_quarter = range((quarter_number - 1) * 3 + 1, quarter_number * 3 + 1)
        days_amount = sum(monthrange(app_core.current_year, month)[1] for month in months_in_quarter)

        Total_statistic_list = quarter.total_quarter_statistics.data

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(5)+str(round(total_income/days_amount, 2))+"<br/>")

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(6)+str(total_expense))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(7)+str(round(total_expense/days_amount, 2))+"<br/>")

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(8)+str(round(total_income - total_expense, 2)))

        Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(1))
        add_total_statistics(Incomes_categories_total_values, [9,13], Total_statistic_list)

        Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(2))
        add_total_statistics(Expenses_categories_total_values, [17,20], Total_statistic_list)

        #Months statistics
        for month in quarter.months:
            Incomes_categories_have_transactions = app_core.db.transaction_query.check_categories_have_transactions(
                                                        Incomes_categories, app_core.current_year, month.month_number)
            Expenses_categories_have_transactions = app_core.db.transaction_query.check_categories_have_transactions(
                                                        Expenses_categories, app_core.current_year, month.month_number)

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

    categories_total_values:dict[int, list[float]] = app_core.db.statistics_query.get_categories_monthly_transactions_sum_by_months(
        Incomes_categories, app_core.current_year, list(range(1,13)))
    for income_category in Incomes_categories:
        Incomes_categories_total_values[income_category] = round(sum(categories_total_values[income_category]), 2)
    
    categories_total_values.clear()
    categories_total_values = app_core.db.statistics_query.get_categories_monthly_transactions_sum_by_months(
        Expenses_categories, app_core.current_year, list(range(1,13)))
    for expenses_category in Expenses_categories:
        Expenses_categories_total_values[expenses_category] = round(sum(categories_total_values[expenses_category]), 2)

    #Entire year statistics
    total_income = round(sum(Incomes_categories_total_values.values()), 2)
    total_expense = round(sum(Expenses_categories_total_values.values()), 2)
    days_amount = 365 if app_core.current_year % 4 != 0 else 366# 365 days if year is not leap

    Total_statistic_list = WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(25)+str(round(total_income/12, 2)))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(24)+str(round(total_income/days_amount, 2))+"<br/>")

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(6)+str(total_expense))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(27)+str(round(total_expense/12, 2)))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(26)+str(round(total_expense/days_amount, 2))+"<br/>")

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(8)+f"{round(total_income - total_expense, 2)}")

    Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(1))
    add_total_statistics(Incomes_categories_total_values, [9,13], Total_statistic_list)

    Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(2))
    add_total_statistics(Expenses_categories_total_values, [17,20], Total_statistic_list)

    for ymonth in WindowsRegistry.YearlyStatistics.statistics.months:
        Incomes_categories_have_transactions = app_core.db.transaction_query.check_categories_have_transactions(
            Incomes_categories, app_core.current_year, ymonth.month_number)
        Expenses_categories_have_transactions = app_core.db.transaction_query.check_categories_have_transactions(
            Expenses_categories, app_core.current_year, ymonth.month_number)

        if Incomes_categories_have_transactions and Expenses_categories_have_transactions:
            add_month_statistics(Incomes_categories, Expenses_categories, ymonth.data, ymonth.month_number)
        else:
            ymonth.data.addItem(WindowsRegistry.Messages.no_transactions.text())

    WindowsRegistry.StatisticsWindow.done(1)
    logger.debug(f"Yearly statistics window is shown. Current year: {app_core.current_year}")
    return WindowsRegistry.YearlyStatistics.exec()
        

def show_custom_range_statistics_window() -> None:
    """This method is used to show the custom range statistics window. Where parameters like from and to date are set."""

    categories = list(AppCore.instance().categories.values())
    WindowsRegistry.CustomRangeStatistics.categories_selection.add_categories_to_selection(categories)
    
    WindowsRegistry.StatisticsWindow.done(1)
    WindowsRegistry.CustomRangeStatistics.exec()


def show_custom_range_statistics_view() -> int:
    """This method is used to show the actual custom range statistics."""

    #Reset statistics and transactions list
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.clear()
    WindowsRegistry.CustomRangeStatisticsView.transactions_list.clear()

    from_date = WindowsRegistry.CustomRangeStatistics.from_date.date()
    to_date = WindowsRegistry.CustomRangeStatistics.to_date.date()

    if from_date.daysTo(to_date) <= 0:
        return WindowsRegistry.Messages.wrong_date.exec()
    
    if len(WindowsRegistry.CustomRangeStatistics.categories_selection.selected_categories_data) == 0:
        return WindowsRegistry.Messages.no_selected_category.exec()

    date_difference:timedelta = cast(date, to_date.toPython()) - cast(date, from_date.toPython()) # pyright: ignore[reportOperatorIssue]
    days_amount = date_difference.days

    Incomes_categories = [category[0] for category in WindowsRegistry.CustomRangeStatistics.categories_selection.selected_categories_data.values() if category[0].type == "Incomes"]
    Expenses_categories = [category[0] for category in WindowsRegistry.CustomRangeStatistics.categories_selection.selected_categories_data.values() if category[0].type == "Expenses"]

    all_transactions = AppCore.instance().db.statistics_query.get_transactions_by_range(
        list(map(lambda category: category.id, Incomes_categories+Expenses_categories)),
        cast(date, from_date.toPython()), cast(date, to_date.toPython())
    )
    categorized_transactions:defaultdict[int, list[Transaction]] = defaultdict(list)
    for transaction in all_transactions:
        categorized_transactions[transaction.category_id].append(transaction)

    Incomes_categories_total_values = {}
    Expenses_categories_total_values = {}

    Incomes_categories_transactions:dict[Category, list[Transaction]] = {}
    Expenses_categories_transactions:dict[Category, list[Transaction]] = {}

    for income_category in Incomes_categories:
        category_transactions = categorized_transactions[income_category.id]
        total_value = round(sum([transaction.value for transaction in category_transactions]), 2)

        Incomes_categories_transactions[income_category] = sorted(
            category_transactions, key=lambda transaction: transaction.date
        )
        Incomes_categories_total_values[income_category.id] = total_value
        
    for expense_category in Expenses_categories:
        category_transactions = categorized_transactions[expense_category.id]
        total_value = round(sum([transaction.value for transaction in category_transactions]), 2)

        Expenses_categories_transactions[expense_category] = sorted(
            category_transactions, key=lambda transaction: transaction.date
        )
        Expenses_categories_total_values[expense_category.id] = total_value
    
    total_income = round(sum(total_value for total_value in Incomes_categories_total_values.values()), 2)
    total_expense = round(sum(total_value for total_value in Expenses_categories_total_values.values()), 2)

    #Custom range statistics
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(4)+str(total_income)
    )
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(24)+str(round(total_income/days_amount, 2))+"<br/>"
    )

    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(6)+str(total_expense)
    )
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(26)+str(round(total_expense/days_amount, 2))+"<br/>"
    )

    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(8)+f"{round(total_income - total_expense, 2)}"
    )

    if len(Incomes_categories):
        WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
            "<br/><br/>"+LanguageStructure.MainWindow.get_translation(1)
        )
        add_total_statistics(Incomes_categories_total_values, [9,13], WindowsRegistry.CustomRangeStatisticsView.statistics_list)

    if len(Expenses_categories):
        WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
            "<br/><br/>"+LanguageStructure.MainWindow.get_translation(2)
        )
        add_total_statistics(Expenses_categories_total_values, [17,20], WindowsRegistry.CustomRangeStatisticsView.statistics_list)
    
    def add_transaction_to_transactions_list(transaction:Transaction) -> None:
        day = transaction.date.day                
        month = transaction.date.month
        year = transaction.date.year
        item_text = dedent(f"""
        <table width="100%">
            <tr>
                <td width="15%">{day:02}/{month:02}/{year}</td>
                <td width="20%" align="right">{transaction.value}</td>
                <td width="65%" align="center">{transaction.name}</td>
            </tr>
        </table>
        """)
        WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(item_text)
    
    def add_category_to_statistics(categories_transactions:dict[Category, list[Transaction]]) -> None:
        for category, category_transactions in categories_transactions.items():
            if len(category_transactions) == 0:
                WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(
                    f"<br/>{category.name} {LanguageStructure.Statistics.get_translation(39)}<br/>"
                )
            else:
                WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(f"<br/>{category.name}<br/>")
                for transaction in category_transactions:
                    add_transaction_to_transactions_list(transaction)
    #Transactions list
    if len(Incomes_categories_transactions):
        WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(
            LanguageStructure.MainWindow.get_translation(1)+"<br/>"
        )
        add_category_to_statistics(Incomes_categories_transactions)
    
    if len(Expenses_categories_transactions):
        WindowsRegistry.CustomRangeStatisticsView.transactions_list.addItem(
            "<br/><br/>"+LanguageStructure.MainWindow.get_translation(2)+"<br/>"
        )
        add_category_to_statistics(Expenses_categories_transactions)

    logger.debug(f"Custom range statistics window is shown. From date: {from_date} To date: {to_date}")
    return WindowsRegistry.CustomRangeStatisticsView.exec()
