from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias, cast
from datetime import date, timedelta
from calendar import monthrange
from collections import defaultdict, Counter
from textwrap import dedent

from languages import LanguageStructure
from project_configuration import CategoryType
from GeneralTools.Utils import generate_month_range

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from GUI.gui_constants import INVESTMENTS_COLOR


if TYPE_CHECKING:
    from PySide6.QtWidgets import QListWidget
    from backend.models import Transaction
    from backend.investment_query import InvestmentsPeriodStatistics
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

    # Zero totals stay in the breakdown but are never ranked.
    ranked_total_values: CategoriesTotalValues = {
        category: total for category, total in Categories_total_values.items() if total != 0
    }
    highest_total_value: float = max(ranked_total_values.values(), default=0.0)

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
    for category, total in ranked_total_values.items():
        if total == highest_total_value:
            transactions_statistic = _get_min_and_max_transactions(category, app_core.current_year, month)
            Categories_with_highest_total_value[category] = (*transactions_statistic,)

    #Lowest categories
    Categories_with_lowest_total_value:CategoriesWithLowestTotalValue = {}
    lowest_total_value: float = min(ranked_total_values.values(), default=0.0)
    if lowest_total_value != highest_total_value:
        for category, total in ranked_total_values.items():
            if total == lowest_total_value:
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


def _format_percentage(value: float, total: float, *, warn: bool = False) -> str:
    """Format value's share of total, highlighting a warning only for a defined share."""
    if total == 0:
        return "—"
    number: str = f"{value / total * 100:.2f}".rstrip("0").rstrip(".")
    return f"<span style='color:red'>{number}%</span>" if warn else f"{number}%"


def _format_category_total_value(
    category_name: str, total_value: float, category_type: str,
    total_income: float, total_expense: float, days_amount: int, months_amount: int,
) -> str:
    """Format a category's period amount and shares, followed by its existing averages."""
    income_share: str = _format_percentage(total_value, total_income)
    shares: str = f"{income_share} {LanguageStructure.Statistics.get_translation(42)}"
    if category_type == CategoryType.Expense:
        expense_share: str = _format_percentage(
            total_value, total_expense, warn=total_value > total_expense / 2
        )
        shares += f", {expense_share} {LanguageStructure.Statistics.get_translation(43)}"

    if total_value == 0:
        return f"{category_name} - {total_value} ({shares})"

    average_per_day: float = round(total_value / days_amount, 2)
    average_per_month: float = round(total_value / months_amount, 2)
    average_per_day_text: str = LanguageStructure.Statistics.get_translation(40)
    average_per_month_text: str = LanguageStructure.Statistics.get_translation(41)
    color: str = "green" if category_type == CategoryType.Income else "red"

    average_per_day_text += f"<span style='color:{color}'>{average_per_day}</span>"
    average_per_month_text += f"<span style='color:{color}'>{average_per_month}</span>"
    if months_amount == 1:
        average_text = f"({average_per_day_text})"
    else:
        average_text = f"({average_per_day_text}, {average_per_month_text})"


    return (
        f"{category_name} - <span style='color:{color}'>{total_value}</span> "
        f"({shares}) {average_text}"
    )


def _get_custom_range_months_amount(from_date:date, to_date:date) -> int:
    """Return the number of calendar months covered by a custom date range."""

    return max(1, (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month))


def add_total_statistics(
        statistic:CategoriesTotalValues,
        words:list[int],
        total_statistics_list:QListWidget,
        category_type:str,
        total_income: float,
        total_expense: float,
        days_amount: int,
        months_amount: int,
    ) -> None:
    """Add total statistics to the list

        Arguments
        ---------
            `statistic` (dict): statistic data to add
            `words` (list): language specific words to add statistic
            `total_statistics_list` (QListWidget): list to add statistic
    """        

    app_core = AppCore.instance()
    ranked: CategoriesTotalValues = {
        category: total for category, total in statistic.items() if total != 0
    }
    if ranked:
        max_category: int = max(ranked, key=ranked.__getitem__)
        min_category: int = min(ranked, key=ranked.__getitem__)
        total_statistics_list.addItem(
            LanguageStructure.Statistics.get_translation(words[0])
            + app_core.categories[max_category].name
            + f" ({ranked[max_category]}) <br/>"
        )
        if min_category != max_category:
            total_statistics_list.addItem(
                LanguageStructure.Statistics.get_translation(words[1])
                + app_core.categories[min_category].name
                + f" ({ranked[min_category]})<br/>"
            )

    sorted_categories = dict(sorted(statistic.items(), key=lambda category: category[1], reverse=True))
    for category, total_value in sorted_categories.items():
        total_statistics_list.addItem(
            _format_category_total_value(
                app_core.categories[category].name,
                total_value,
                category_type,
                total_income,
                total_expense,
                days_amount,
                months_amount,
            )
        )


def _expense_total_text(total_income: float, total_expense: float) -> str:
    """Return the expense summary, warning when spending meets or exceeds income."""
    share: str = _format_percentage(total_expense, total_income, warn=total_expense >= total_income)
    return f"{LanguageStructure.Statistics.get_translation(6)}{total_expense} ({share})"


def _format_net_amount(amount: float, total_income: float) -> str:
    """Format a period result and its share of income, highlighting losses."""
    result: float = round(amount, 2)
    negative: bool = result < 0
    text: str = f"<span style='color:red'>{result}</span>" if negative else str(result)
    share: str = _format_percentage(result, total_income, warn=negative)
    return f"{text} ({share})"


def get_net_result_text(
    total_income: float,
    total_expense: float,
    investment_statistics: InvestmentsPeriodStatistics | None,
) -> str:
    """Show the period's net income, separating cash and combined changes when investments exist."""
    net_income: float = total_income - total_expense
    if investment_statistics is None:
        return LanguageStructure.Statistics.get_translation(8) + _format_net_amount(net_income, total_income)

    totals = investment_statistics.totals
    cash: float = net_income - totals.deposits + totals.withdrawals
    # Transfers between cash and investments cancel in the combined change.
    combined: float = net_income + totals.value_change
    return (
        f"{LanguageStructure.Investments.get_translation(11)}{_format_net_amount(cash, total_income)}, "
        f"{LanguageStructure.Investments.get_translation(15)}{_format_net_amount(combined, total_income)}"
    )


def add_investments_statistics(
        statistics_list:QListWidget,
        investment_statistics:InvestmentsPeriodStatistics
    ) -> None:
    """Add Investments sums of the period and the state of each Investments category to the list

        Arguments
        ---------
            `statistics_list` (QListWidget): list to add statistic
            `investment_statistics` (InvestmentsPeriodStatistics): sums and values of Investments categories
    """

    app_core = AppCore.instance()
    investment_totals = investment_statistics.totals

    # Deposits are colored as expenses and withdrawals as incomes, because they move money of the balance
    statistics_list.addItem("<br/><br/>" + LanguageStructure.Investments.get_translation(0))
    statistics_list.addItem(
        f"{LanguageStructure.Investments.get_translation(8)}<span style='color:red'>{investment_totals.deposits}</span>"
    )
    statistics_list.addItem(
        f"{LanguageStructure.Investments.get_translation(9)}"
        f"<span style='color:green'>{investment_totals.withdrawals}</span>"
    )
    statistics_list.addItem(
        f"{LanguageStructure.Investments.get_translation(10)}"
        f"<span style='color:{'green' if investment_totals.value_change >= 0 else 'red'}'>"
        f"{investment_totals.value_change}</span><br/>"
    )
    for category_id, category_totals in investment_statistics.categories_totals.items():
        change_color = "green" if category_totals.value_change >= 0 else "red"
        category_value = investment_statistics.categories_values[category_id]
        statistics_list.addItem(
            LanguageStructure.Investments.get_translation(14)
            .replace("%category%", app_core.categories[category_id].name)
            .replace("%value%", f"<span style='color:{INVESTMENTS_COLOR}'>{category_value}</span>")
            .replace("%deposits%", f"<span style='color:red'>{category_totals.deposits}</span>")
            .replace("%withdrawals%", f"<span style='color:green'>{category_totals.withdrawals}</span>")
            .replace("%change%", f"<span style='color:{change_color}'>{category_totals.value_change}</span>")
        )


def add_month_statistics(
        Incomes_categories:list[int],
        Expenses_categories:list[int],
        month_statistics:QListWidget,
        current_month:int
    ) -> None:
    """Add month statistics to the list. Blocks of category types without transactions in the month are skipped.

        Arguments
        ---------
            `Incomes_categories` (dict): income categories to add statistics
            `Expenses_categories` (dict): expense categories to add statistics
            `month_statistics` (QListWidget): list to add statistic
            `current_month` (int): month to add statistics
    """

    def add_categories_months_sum(categories:dict[int, float], category_type:str) -> None:
        """Add categories months sum to the list

            Arguments
            ---------
                `categories` (dict): categories to add months sum
        """
        month_statistics.addItem(f"<br/>{LanguageStructure.Search.get_translation(6)}")
        for category_id, total_value in categories.items():
            month_statistics.addItem(
                _format_category_total_value(
                    AppCore.instance().categories[category_id].name,
                    total_value,
                    category_type,
                    total_income,
                    total_expense,
                    days_amount,
                    1,
                )
            )

    app_core = AppCore.instance()
    Incomes_statistic = get_min_and_max_categories(Incomes_categories, current_month)\
        if app_core.db.transaction_query.check_categories_have_transactions(
            Incomes_categories, app_core.current_year, current_month
        ) else None
    Expenses_statistic = get_min_and_max_categories(Expenses_categories, current_month)\
        if app_core.db.transaction_query.check_categories_have_transactions(
            Expenses_categories, app_core.current_year, current_month
        ) else None

    total_income = round(sum(Incomes_statistic[4].values()), 2) if Incomes_statistic is not None else 0.0
    total_expense = round(sum(Expenses_statistic[4].values()), 2) if Expenses_statistic is not None else 0.0
    _, days_amount = monthrange(app_core.current_year, current_month)
    month_start, month_end = generate_month_range(app_core.current_year, current_month)
    investment_categories = app_core.get_investment_categories_ids()
    investment_statistics = app_core.db.investment_query.get_period_statistics(
        investment_categories, month_start, month_end
    ) if investment_categories else None

    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(4)}{total_income}")
    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(5)}{round(total_income/days_amount, 2)}<br/>")

    month_statistics.addItem(_expense_total_text(total_income, total_expense))
    month_statistics.addItem(f"{LanguageStructure.Statistics.get_translation(7)}{round(total_expense/days_amount, 2)}<br/>")

    month_statistics.addItem(get_net_result_text(total_income, total_expense, investment_statistics))

    if Incomes_statistic is not None:
        month_statistics.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(1))
        add_statistic(month_statistics, Incomes_statistic, [9,10,13,14,11,15])
        add_categories_months_sum(Incomes_statistic[4], CategoryType.Income)

    if Expenses_statistic is not None:
        month_statistics.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(2))
        add_statistic(month_statistics, Expenses_statistic, [17,18,20,21,19,22])
        add_categories_months_sum(Expenses_statistic[4], CategoryType.Expense)

    if investment_statistics is not None:
        add_investments_statistics(month_statistics, investment_statistics)

def show_monthly_statistics() -> int:
    """This method is used to show the monthly statistics window."""

    app_core = AppCore.instance()
    WindowsRegistry.MonthlyStatistics.setWindowTitle(LanguageStructure.Months.get_translation(app_core.current_month))
    WindowsRegistry.MonthlyStatistics.statistics.clear()
    Incomes_categories, Expenses_categories = app_core.get_income_and_expense_categories_as_ids()

    if len(app_core.categories) == 0:
        return WindowsRegistry.Messages.no_category.exec()

    if not app_core.db.transaction_query.check_categories_have_transactions(
        list(app_core.categories), app_core.current_year, app_core.current_month
    ):
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

    Incomes_categories, Expenses_categories = app_core.get_income_and_expense_categories_as_ids()
    investment_categories = app_core.get_investment_categories_ids()

    if len(app_core.categories) == 0:
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
        quarter_start = generate_month_range(app_core.current_year, months_in_quarter[0])[0]
        quarter_end = generate_month_range(app_core.current_year, months_in_quarter[-1])[1]
        investment_statistics = app_core.db.investment_query.get_period_statistics(
            investment_categories, quarter_start, quarter_end
        ) if investment_categories else None

        Total_statistic_list = quarter.total_quarter_statistics.data

        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(25)+str(round(total_income/3, 2)))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(5)+str(round(total_income/days_amount, 2))+"<br/>")

        Total_statistic_list.addItem(_expense_total_text(total_income, total_expense))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(27)+str(round(total_expense/3, 2)))
        Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(7)+str(round(total_expense/days_amount, 2))+"<br/>")

        Total_statistic_list.addItem(get_net_result_text(total_income, total_expense, investment_statistics))

        if Incomes_categories:
            Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(1))
            add_total_statistics(
                Incomes_categories_total_values,
                [9,13],
                Total_statistic_list,
                CategoryType.Income,
                total_income,
                total_expense,
                days_amount,
                3,
            )

        if Expenses_categories:
            Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(2))
            add_total_statistics(
                Expenses_categories_total_values,
                [17,20],
                Total_statistic_list,
                CategoryType.Expense,
                total_income,
                total_expense,
                days_amount,
                3,
            )

        if investment_statistics is not None:
            add_investments_statistics(Total_statistic_list, investment_statistics)

        #Months statistics
        for month in quarter.months:
            if app_core.db.transaction_query.check_categories_have_transactions(
                list(app_core.categories), app_core.current_year, month.month_number
            ):
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
    
    Incomes_categories, Expenses_categories = app_core.get_income_and_expense_categories_as_ids()
    investment_categories = app_core.get_investment_categories_ids()
    if len(app_core.categories) == 0:
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
    year_start = date(app_core.current_year, 1, 1)
    year_end = date(app_core.current_year, 12, 31)
    investment_statistics = app_core.db.investment_query.get_period_statistics(
        investment_categories, year_start, year_end
    ) if investment_categories else None

    Total_statistic_list = WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data

    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(4)+str(total_income))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(25)+str(round(total_income/12, 2)))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(24)+str(round(total_income/days_amount, 2))+"<br/>")

    Total_statistic_list.addItem(_expense_total_text(total_income, total_expense))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(27)+str(round(total_expense/12, 2)))
    Total_statistic_list.addItem(LanguageStructure.Statistics.get_translation(26)+str(round(total_expense/days_amount, 2))+"<br/>")

    Total_statistic_list.addItem(get_net_result_text(total_income, total_expense, investment_statistics))

    if Incomes_categories:
        Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(1))
        add_total_statistics(
            Incomes_categories_total_values, [9, 13], Total_statistic_list, CategoryType.Income,
            total_income, total_expense, days_amount, 12,
        )

    if Expenses_categories:
        Total_statistic_list.addItem("<br/><br/>"+LanguageStructure.MainWindow.get_translation(2))
        add_total_statistics(
            Expenses_categories_total_values, [17, 20], Total_statistic_list, CategoryType.Expense,
            total_income, total_expense, days_amount, 12,
        )

    if investment_statistics is not None:
        add_investments_statistics(Total_statistic_list, investment_statistics)

    for ymonth in WindowsRegistry.YearlyStatistics.statistics.months:
        if app_core.db.transaction_query.check_categories_have_transactions(
            list(app_core.categories), app_core.current_year, ymonth.month_number
        ):
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
    
    investment_categories = AppCore.instance().get_investment_categories_ids()
    if len(WindowsRegistry.CustomRangeStatistics.categories_selection.selected_categories_data) == 0\
        and not investment_categories:
        return WindowsRegistry.Messages.no_selected_category.exec()

    date_difference:timedelta = cast(date, to_date.toPython()) - cast(date, from_date.toPython()) # pyright: ignore[reportOperatorIssue]
    days_amount = date_difference.days

    Incomes_categories, Expenses_categories = WindowsRegistry.CustomRangeStatistics.categories_selection.get_selected_income_and_expense_categories()

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
    investment_statistics = AppCore.instance().db.investment_query.get_period_statistics(
        investment_categories, cast(date, from_date.toPython()), cast(date, to_date.toPython())
    ) if investment_categories else None

    #Custom range statistics
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(4)+str(total_income)
    )
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(24)+str(round(total_income/days_amount, 2))+"<br/>"
    )

    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        _expense_total_text(total_income, total_expense)
    )
    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        LanguageStructure.Statistics.get_translation(26)+str(round(total_expense/days_amount, 2))+"<br/>"
    )

    WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
        get_net_result_text(total_income, total_expense, investment_statistics)
    )

    months = _get_custom_range_months_amount(
        cast(date, from_date.toPython()), cast(date, to_date.toPython())
    )
    if len(Incomes_categories):
        WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
            "<br/><br/>"+LanguageStructure.MainWindow.get_translation(1)
        )
        add_total_statistics(
            Incomes_categories_total_values, [9, 13], WindowsRegistry.CustomRangeStatisticsView.statistics_list,
            CategoryType.Income, total_income, total_expense, days_amount, months,
        )

    if len(Expenses_categories):
        WindowsRegistry.CustomRangeStatisticsView.statistics_list.addItem(
            "<br/><br/>"+LanguageStructure.MainWindow.get_translation(2)
        )
        add_total_statistics(
            Expenses_categories_total_values, [17, 20], WindowsRegistry.CustomRangeStatisticsView.statistics_list,
            CategoryType.Expense, total_income, total_expense, days_amount, months,
        )

    if investment_statistics is not None:
        add_investments_statistics(WindowsRegistry.CustomRangeStatisticsView.statistics_list, investment_statistics)
    
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
