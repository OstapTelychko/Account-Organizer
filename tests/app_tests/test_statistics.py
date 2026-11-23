from __future__ import annotations
from typing import TYPE_CHECKING
import random
import re

from datetime import date
from PySide6.QtCore import QTimer, QDate
from PySide6.QtWidgets import QListWidget
from calendar import monthrange, isleap
from textwrap import dedent

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from languages import LanguageStructure
from AppObjects.app_core import AppCore
from AppObjects.category import Category
from AppObjects.windows_registry import WindowsRegistry
from project_configuration import CategoryType
from GeneralTools.html_to_text import html_to_text
from GUI.category import load_category
from Statistics.statistics import (
    _expense_total_text,
    _format_category_total_value,
    _get_custom_range_months_amount,
    add_month_statistics,
    add_total_statistics,
    get_min_and_max_categories,
    get_net_result_text,
    show_custom_range_statistics_view,
)
from GeneralTools.Utils import shift_month

if TYPE_CHECKING:
    from typing import Callable
    from DesktopQtToolkit.list_widget import CustomListWidget


class TestStatistics(DBTestCase, OutOfScopeTestCase):
    """Test statistics of the application."""

    def setUp(self) -> None:
        """Set up the test case. It creates translations so you don't have to create them in every test case."""

        self.translated_incomes = LanguageStructure.MainWindow.get_translation(1)
        self.translated_expenses = LanguageStructure.MainWindow.get_translation(2)
        return super().setUp()


    def open_statistics_window(self, func:Callable[[], None]) -> None:
        """Open statistics window and call function after some delay."""

        QTimer.singleShot(100, self.catch_failure(func))
        self.click_on_widget(WindowsRegistry.MainWindow.statistics)
    

    def create_monthly_statistics(self, days_amount:int) -> list[str]:
        """Create monthly statistics for the current month.

            Arguments
            ---------
                `days_amount` : (int) - Number of days in the current month.
            Returns
            -------
                `list` - List of strings with the monthly statistics.
        """

        return [
            f"{LanguageStructure.Statistics.get_translation(4)}1000.0",
            f"{LanguageStructure.Statistics.get_translation(5)}{round(1000/days_amount, 2)}",
            re.escape(f"{LanguageStructure.Statistics.get_translation(6)}1000.0 (100%)"),
            f"{LanguageStructure.Statistics.get_translation(7)}{round(1000/days_amount, 2)}",
            re.escape(f"{LanguageStructure.Statistics.get_translation(8)}0.0 (0%)"),
            f"{self.translated_incomes}",
            fr"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name}\s+\(1000.0\)",
            f"{LanguageStructure.Statistics.get_translation(11)}",
            fr"{self.test_income_transaction_name}\s+-\s+1000.0",
            re.escape(self.create_category_total_statistics(self.income_category.name, 1000.0, days_amount, 1, CategoryType.Income)),
            f"{self.translated_expenses}",
            fr"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name}\s+\(1000.0\)",
            f"{LanguageStructure.Statistics.get_translation(19)}",
            fr"{self.test_expenses_transaction_name}\s+-\s+1000.0",
            re.escape(self.create_category_total_statistics(self.expenses_category.name, 1000.0, days_amount, 1, CategoryType.Expense)),]


    def create_category_total_statistics(
            self,
            category_name:str,
            total_value:float,
            days_amount:int,
            months_amount:int,
            category_type: str
        ) -> str:
        """Build the expected row for the fixture's single category of each type."""

        shares: str = f"100% {LanguageStructure.Statistics.get_translation(42)}"
        if category_type == CategoryType.Expense:
            shares += f", 100% {LanguageStructure.Statistics.get_translation(43)}"

        average_per_day = round(total_value / days_amount, 2)
        if months_amount == 1:
            return (
                f"{category_name} - {total_value} ({shares}) "
                f"({LanguageStructure.Statistics.get_translation(40)}{average_per_day})"
            )

        average_per_month = round(total_value / months_amount, 2)

        average_per_day_text = f"{LanguageStructure.Statistics.get_translation(40)}{average_per_day}"
        average_per_month_text = f"{LanguageStructure.Statistics.get_translation(41)}{average_per_month}"

        return (
            f"{category_name} - {total_value} ({shares}) "
            f"({average_per_day_text}, {average_per_month_text})"
        )


    def get_actual_statistics(self, statistics_list_widget:CustomListWidget) -> str:
        """Get actual statistics from the list widget as string.

            Arguments
            ---------
                `statistics_list_widget` : (CustomListWidget) - List widget with statistics.
        """
        return "".join(
            statistics_list_widget.item(index).text()
            for index in range(statistics_list_widget.count())
        )


    def get_plain_statistics(self, statistics_list_widget:CustomListWidget) -> str:
        """Get actual statistics converted to plain text like the clipboard copy helpers do."""

        return html_to_text(self.get_actual_statistics(statistics_list_widget))
    

    def generate_custom_range_statistics_transactions(self, transaction_value: float, transaction_name: str, day: int = 0) -> list[str]:
        result = []
        for month in range(1, 7):
            if day == 0:
                day = date.today().day
            year = AppCore.instance().current_year
            item_text = dedent(f"""
            <table width="100%">
                <tr>
                    <td width="15%">{day:02}/{month:02}/{year}</td>
                    <td width="20%" align="right">{transaction_value}</td>
                    <td width="65%" align="center">{transaction_name}</td>
                </tr>
            </table>
            """)
            result.append(item_text)

        return result


    def test_1_show_monthly_statistics(self) -> None:
        """Test showing monthly statistics."""

        app_core = AppCore.instance()
        _, days_amount = monthrange(app_core.current_year, app_core.current_month)

        def _open_monthly_statics_window() -> None:
            """Click button that show monthly statistics window."""

            def _check_monthly_statistics() -> None:
                """Check if monthly statistics are correct."""

                expected_monthly_statistics = self.create_monthly_statistics(days_amount)
                actual_statistics = self.get_plain_statistics(WindowsRegistry.MonthlyStatistics.statistics)

                for expected_row in expected_monthly_statistics:
                    self.assertRegex(
                        actual_statistics, expected_row, f"In month statistics regex {expected_row} not found"
                    )
                    
                WindowsRegistry.MonthlyStatistics.done(1)
            
            QTimer.singleShot(100, self.catch_failure(_check_monthly_statistics))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.monthly_statistics)
        self.open_statistics_window(_open_monthly_statics_window)
        qsleep(500)
    

    def test_2_show_quarterly_statistics(self) -> None:
        """Test showing quarterly statistics."""

        app_core = AppCore.instance()
        month_without_transactions = 12 if app_core.current_month != 12 else 1
        quarter_without_transaction = 4 if app_core.current_month != 12 else 1

        for month in range(1, 13):
            if month not in (app_core.current_month, month_without_transactions):
                app_core.db.transaction_query.add_transaction(
                    self.income_category.id, date(app_core.current_year, month, 1), 1000, "Test income transaction"
                )
                app_core.db.transaction_query.add_transaction(
                    self.expenses_category.id, date(app_core.current_year, month, 1), 1000, "Test expenses transaction"
                )
        
        def _open_quarterly_statistics_window() -> None:
            """Click button that show quarterly statistics window."""

            def _check_quarterly_statistics() -> None:
                """Check if quarterly statistics are correct."""

                for quarter in WindowsRegistry.QuarterlyStatistics.statistics.quarters:
                    quarter_number = quarter.quarter_number
                    months_in_quarter = range((quarter_number - 1) * 3 + 1, quarter_number * 3 + 1)
                    days_amount = sum(monthrange(app_core.current_year, month)[1] for month in months_in_quarter)

                    if quarter_number != quarter_without_transaction:
                        total_income = 3000.0
                        total_expense = 3000.0
                    else:
                        total_income = 2000.0
                        total_expense = 2000.0

                    expected_total_quarterly_statistics = [
                        f"{LanguageStructure.Statistics.get_translation(4)}{total_income}",
                        f"{LanguageStructure.Statistics.get_translation(25)}{round(total_income/3, 2)}",
                        f"{LanguageStructure.Statistics.get_translation(5)}{round(total_income/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(6)}{total_expense} (100%)",
                        f"{LanguageStructure.Statistics.get_translation(27)}{round(total_expense/3, 2)}",
                        f"{LanguageStructure.Statistics.get_translation(7)}{round(total_expense/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(8)}0.0 (0%)",
                        f"<br/><br/>{self.translated_incomes}",
                        f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name} ({total_income}) <br/>",
                        self.create_category_total_statistics(self.income_category.name, total_income, days_amount, 3, CategoryType.Income),
                        f"<br/><br/>{self.translated_expenses}",
                        f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name} ({total_expense}) <br/>",
                        self.create_category_total_statistics(self.expenses_category.name, total_expense, days_amount, 3, CategoryType.Expense),]

                    statistics_data = quarter.total_quarter_statistics.data
                    self.assertEqual(
                        len(expected_total_quarterly_statistics), statistics_data.count(),
                        f"Quarterly statistics have another amount of rows. Expected amount \
                        {len(expected_total_quarterly_statistics)} found {statistics_data.count()} rows"
                        )

                    for index, expected_row in enumerate(expected_total_quarterly_statistics):
                        self.assertEqual(
                            html_to_text(expected_row), html_to_text(statistics_data.item(index).text()),
                            f"In quarterly statistics row {index} expected result {expected_row} not \
                            {html_to_text(statistics_data.item(index).text())}"
                        )

                    for month in quarter.months:
                        statistics_data = month.data

                        current_month = month.month_number
                        _, month_days_amount = monthrange(app_core.current_year, current_month)
                        expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)
                        actual_statistics = self.get_plain_statistics(statistics_data)

                        if current_month != month_without_transactions:

                            for expected_row in expected_monthly_statistics:
                                self.assertRegex(
                                    actual_statistics, expected_row,
                                    f"In quarter {quarter_number} month {current_month} statistics regex {expected_row} not found"
                                )

                        else:
                            self.assertEqual(
                                1,
                                statistics_data.count(),
                                f"Month {current_month} without transactions don't have 1 row in statistics"
                            )
                            self.assertEqual(
                                WindowsRegistry.Messages.no_transactions.text(), 
                                statistics_data.item(0).text(),
                                "Month without transactions hasn't showed error text"
                            )

                WindowsRegistry.QuarterlyStatistics.done(1)
            
            QTimer.singleShot(200, self.catch_failure(_check_quarterly_statistics))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.quarterly_statistics)
        
        self.open_statistics_window(_open_quarterly_statistics_window)
        qsleep(2000)
                        

    def test_3_show_yearly_statistics(self) -> None:
        """Test showing yearly statistics."""

        app_core = AppCore.instance()
        month_without_transactions = 12 if app_core.current_month != 12 else 1

        for month in range(1, 13):
            if month not in (app_core.current_month, month_without_transactions):
                app_core.db.transaction_query.add_transaction(
                    self.income_category.id, date(app_core.current_year, month, 1), 1000, "Test income transaction"
                )
                app_core.db.transaction_query.add_transaction(
                    self.expenses_category.id, date(app_core.current_year, month, 1), 1000, "Test expenses transaction"
                )
        
        def _open_yearly_statistics_window() -> None:
            """Click button that show yearly statistics window."""

            def _check_yearly_statistics() -> None:
                """Check if yearly statistics are correct."""

                days_amount = 365 if app_core.current_year % 4 != 0 else 366

                total_income = 11000.0
                total_expense = 11000.0

                expected_yearly_statistics = [
                    f"{LanguageStructure.Statistics.get_translation(4)}{total_income}",
                    f"{LanguageStructure.Statistics.get_translation(25)}{round(total_income/12, 2)}",
                    f"{LanguageStructure.Statistics.get_translation(24)}{round(total_income/days_amount, 2)}<br/>",
                    f"{LanguageStructure.Statistics.get_translation(6)}{total_expense} (100%)",
                    f"{LanguageStructure.Statistics.get_translation(27)}{round(total_expense/12, 2)}",
                    f"{LanguageStructure.Statistics.get_translation(26)}{round(total_expense/days_amount, 2)}<br/>",
                    f"{LanguageStructure.Statistics.get_translation(8)}0.0 (0%)",
                    f"<br/><br/>{self.translated_incomes}",
                    f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name} ({total_income}) <br/>",
                    self.create_category_total_statistics(self.income_category.name, total_income, days_amount, 12, CategoryType.Income),
                    f"<br/><br/>{self.translated_expenses}",
                    f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name} ({total_expense}) <br/>",
                    self.create_category_total_statistics(self.expenses_category.name, total_expense, days_amount, 12, CategoryType.Expense)]

                statistics_data = WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data
                self.assertEqual(
                    len(expected_yearly_statistics), statistics_data.count(),
                    f"Yearly statistics have another amount of rows. Expected amount \
                    {len(expected_yearly_statistics)} found {statistics_data.count()} rows"
                    )

                for index, expected_row in enumerate(expected_yearly_statistics):
                    self.assertEqual(
                        html_to_text(expected_row), html_to_text(statistics_data.item(index).text()),
                        f"In total year statistics row {index} expected result \
                        {expected_row} not {html_to_text(statistics_data.item(index).text())}"
                    )

                for month in WindowsRegistry.YearlyStatistics.statistics.months:
                    statistics_data = month.data

                    _, month_days_amount = monthrange(app_core.current_year, month.month_number)
                    expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)
                    actual_statistics = self.get_plain_statistics(statistics_data)

                    if month.month_number != month_without_transactions:
                        for expected_row in expected_monthly_statistics:
                            self.assertRegex(
                                actual_statistics, expected_row,
                                f"In year statistics month {month.month_number} regex {expected_row} not found"
                            )

                    else:
                        self.assertEqual(1, statistics_data.count(), 
                            f"Month \
                            {month.month_number} without transactions don't have 1 row in statistics"
                        )
                        self.assertEqual(
                            WindowsRegistry.Messages.no_transactions.text(),
                            statistics_data.item(0).text(),
                            "Month without transactions hasn't showed error text"
                        )

                WindowsRegistry.YearlyStatistics.done(1)
            
            QTimer.singleShot(100, self.catch_failure(_check_yearly_statistics))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.yearly_statistics)
        
        self.open_statistics_window(_open_yearly_statistics_window)
        qsleep(2000)
    

    def test_4_show_custom_range_statistics(self) -> None:
        """Test showing custom range statistics."""

        app_core = AppCore.instance()
        day = random.randint(1, 28 + isleap(app_core.current_year))
        for month in range(1, 7):
            if month != app_core.current_month:
                year = app_core.current_year
                app_core.db.transaction_query.add_transaction(
                    self.income_category.id, date(year, month, day), 1000, "Test income transaction"
                )
                app_core.db.transaction_query.add_transaction(
                    self.expenses_category.id, date(year, month, day), 1000, "Test expenses transaction"
                )
            else:
                app_core.db.transaction_query.update_transaction(
                    self.income_transaction.id,
                    self.test_income_transaction_name,
                    day,
                    self.income_transaction.value,
                )
                app_core.db.transaction_query.update_transaction(
                    self.expenses_transaction.id,
                    self.test_expenses_transaction_name,
                    day,
                    self.expenses_transaction.value,
                )
        
        def _open_custom_range_statistics_window() -> None:
            """Click button that show custom range statistics window."""

            def _select_custom_range() -> None:
                """Select custom range and click show statistics button."""

                self.click_on_widget(WindowsRegistry.CustomRangeStatistics.categories_selection.add_all_incomes_categories)
                self.click_on_widget(WindowsRegistry.CustomRangeStatistics.categories_selection.add_all_expenses_categories)

                WindowsRegistry.CustomRangeStatistics.from_date.setDate(QDate(app_core.current_year, 1, day))
                WindowsRegistry.CustomRangeStatistics.to_date.setDate(QDate(app_core.current_year, 6, day))

                def _check_custom_range_statistics() -> None:
                    """Check if custom range statistics are correct."""

                    total_income = 6000.0
                    total_expense = 6000.0
                    date_difference = date(app_core.current_year, 6, 1) - date(app_core.current_year, 1, 1)
                    days_amount = date_difference.days

                    expected_custom_range_statistics = [
                        f"{LanguageStructure.Statistics.get_translation(4)}{total_income}",
                        f"{LanguageStructure.Statistics.get_translation(24)}{round(total_income/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(6)}{total_expense} (100%)",
                        f"{LanguageStructure.Statistics.get_translation(26)}{round(total_expense/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(8)}0.0 (0%)",
                        f"<br/><br/>{self.translated_incomes}",
                        f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name} ({total_income}) <br/>",
                        self.create_category_total_statistics(self.income_category.name, total_income, days_amount, 5, CategoryType.Income),
                        f"<br/><br/>{self.translated_expenses}",
                        f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name} ({total_expense}) <br/>",
                        self.create_category_total_statistics(self.expenses_category.name, total_expense, days_amount, 5, CategoryType.Expense)]

                    statistics_data = WindowsRegistry.CustomRangeStatisticsView.statistics_list
                    self.assertEqual(
                        len(expected_custom_range_statistics), statistics_data.count(),
                        f"Custom range statistics (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                        have another amount of rows. Expected amount \
                        {len(expected_custom_range_statistics)} found {statistics_data.count()} rows"
                    )

                    for index, expected_row in enumerate(expected_custom_range_statistics):
                        self.assertEqual(
                            html_to_text(expected_row), html_to_text(statistics_data.item(index).text()),
                            f"In Custom range statistics (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                            statistics row {index} expected result {expected_row} not \
                            {html_to_text(statistics_data.item(index).text())}"
                        )
                    
                    expected_transactions = [
                        f"{self.translated_incomes}<br/>",
                        f"<br/>{self.income_category.name}<br/>",
                        *self.generate_custom_range_statistics_transactions(1000.0, "Test income transaction", day),
                        f"<br/><br/>{self.translated_expenses}<br/>",
                        f"<br/>{self.expenses_category.name}<br/>",
                        *self.generate_custom_range_statistics_transactions(1000.0, "Test expenses transaction", day)
                    ]

                    statistics_data = WindowsRegistry.CustomRangeStatisticsView.transactions_list
                    self.assertEqual(
                        len(expected_transactions), statistics_data.count(),
                        f"Custom range transactions list (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                        have another amount of rows. Expected amount \
                        {len(expected_transactions)} found {statistics_data.count()} rows"
                    )
                    self.maxDiff = None
                    for index, expected_row in enumerate(expected_transactions):
                        self.assertEqual(
                            html_to_text(expected_row), html_to_text(statistics_data.item(index).text()),
                            f"In Custom range transactions list (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                            row {index} expected result {expected_row} not \
                            {html_to_text(statistics_data.item(index).text())}"
                        )
                    
                    WindowsRegistry.CustomRangeStatisticsView.done(1)
                    WindowsRegistry.CustomRangeStatistics.done(1)

                QTimer.singleShot(100, self.catch_failure(_check_custom_range_statistics))
                self.click_on_widget(WindowsRegistry.CustomRangeStatistics.show_statistics)

            QTimer.singleShot(100, self.catch_failure(_select_custom_range))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.custom_range_statistics)

        self.open_statistics_window(_open_custom_range_statistics_window)
        qsleep(500)


    def test_5_custom_range_statistics_single_month(self) -> None:
        """Test that a custom range within one month uses daily averages."""

        app_core = AppCore.instance()
        from_date = date(app_core.current_year, app_core.current_month, 1)
        to_date = date(app_core.current_year, app_core.current_month, 2)

        self.assertEqual(
            1,
            _get_custom_range_months_amount(from_date, to_date),
            "A custom range within one calendar month must have one month of averages",
        )


    def test_6_future_transactions_included(self) -> None:
        """Test that future-dated transactions are included in monthly, quarterly and yearly statistics."""

        app_core = AppCore.instance()
        today = date.today()
        future_year, future_month = shift_month(today.year, today.month, 1)
        app_core.db.transaction_query.add_transaction(
            self.expenses_category.id, date(future_year, future_month, 1), 250, "Future expense"
        )

        self.assertEqual(
            app_core.db.statistics_query.get_monthly_transactions_sum(self.expenses_category.id, future_year, future_month),
            250,
            "Future transaction isn't included in monthly statistics"
        )
        self.assertIn(
            250.0,
            app_core.db.statistics_query.get_categories_monthly_transactions_sum_by_months(
                [self.expenses_category.id], future_year, list(range(1, 13))
            )[self.expenses_category.id],
            "Future transaction isn't included in quarterly/yearly statistics"
        )

    def test_expense_and_net_percentages(self) -> None:
        """Warn for spending at or above income and for a negative net amount and defined share."""
        for income, expense, expense_share, net_text in (
            (1000, 750, "75%", "250 (25%)"),
            (1000, 999.99, "100%", "0.01 (0%)"),
            (1000, 1000, "<span style='color:red'>100%</span>", "0 (0%)"),
            (1000, 1250, "<span style='color:red'>125%</span>",
             "<span style='color:red'>-250</span> (<span style='color:red'>-25%</span>)"),
            (0, 50, "—", "<span style='color:red'>-50</span> (—)"),
            (0, 0, "—", "0 (—)"),
        ):
            with self.subTest(income=income, expense=expense):
                self.assertTrue(_expense_total_text(income, expense).endswith(f"({expense_share})"))
                self.assertEqual(
                    get_net_result_text(income, expense, None),
                    LanguageStructure.Statistics.get_translation(8) + net_text,
                )

    def test_zero_categories_are_not_ranked(self) -> None:
        """Rank the smallest active category, not an unused one; omit rankings when none qualify."""
        core: AppCore = AppCore.instance()
        totals: dict[int, float] = {self.expenses_category.id: 1000.0}
        for name, total in (("Unused", 0.0), ("Travel", 25.0)):
            core.db.category_query.create_category(name, CategoryType.Expense, len(totals))
            category = core.db.category_query.get_category(name, CategoryType.Expense)
            assert category is not None
            if total:
                core.db.transaction_query.add_transaction(category.id, self.expenses_transaction.date, total, name)
            core.categories[category.id] = load_category(category, core.db, core.current_year, core.current_month)
            totals[category.id] = total

        _, _, lowest, value, _ = get_min_and_max_categories(list(totals), core.current_month)
        self.assertEqual(([core.categories[key].name for key in lowest], value), (["Travel"], 25.0))

        rows: QListWidget = QListWidget()
        add_total_statistics(totals, [17, 20], rows, CategoryType.Expense, 1000, 1025, 90, 3)
        self.assertIn(LanguageStructure.Statistics.get_translation(20) + "Travel (25.0)", rows.item(1).text())
        self.assertTrue(any(rows.item(i).text().startswith("Unused - 0") for i in range(rows.count())))

        rows.clear()
        add_total_statistics(dict.fromkeys(totals, 0.0), [17, 20], rows, CategoryType.Expense, 0, 0, 90, 3)
        self.assertEqual(rows.count(), len(totals))  # Only the category breakdown remains.

    def test_category_shares_and_warning(self) -> None:
        """Check both denominators independently and highlight only a majority of expenses."""
        of_income: str = LanguageStructure.Statistics.get_translation(42)
        of_expenses: str = LanguageStructure.Statistics.get_translation(43)
        for value, income, expenses, income_share, expense_share in (
            (150, 1000, 500, "15%", "30%"),
            (250, 1000, 500, "25%", "50%"),
            (250.01, 1000, 500, "25%", "<span style='color:red'>50%</span>"),
            (1200, 1000, 2000, "120%", "<span style='color:red'>60%</span>"),
            (150, 0, 500, "—", "30%"),
            (0, 1000, 0, "0%", "—"),
        ):
            with self.subTest(value=value, income=income, expenses=expenses):
                row: str = _format_category_total_value(
                    "Products", value, CategoryType.Expense, income, expenses, 30, 1
                )
                self.assertIn(f"({income_share} {of_income}, {expense_share} {of_expenses})", row)

        salary: str = _format_category_total_value("Salary", 800, CategoryType.Income, 1000, 500, 30, 1)
        self.assertIn(f"(80% {of_income})", salary)
        self.assertNotIn(of_expenses, salary)

    def test_monthly_breakdown_keeps_zero_categories(self) -> None:
        """List a zero-total category in the monthly breakdown without ranking it as the cheapest."""
        core: AppCore = AppCore.instance()
        expense_ids: list[int] = [self.expenses_category.id]
        for name, total in (("Rent", 80.0), ("Travel", 0.0)):
            core.db.category_query.create_category(name, CategoryType.Expense, len(expense_ids))
            category = core.db.category_query.get_category(name, CategoryType.Expense)
            assert category is not None
            if total:
                core.db.transaction_query.add_transaction(category.id, self.expenses_transaction.date, total, name)
            core.categories[category.id] = load_category(category, core.db, core.current_year, core.current_month)
            expense_ids.append(category.id)

        rows: QListWidget = QListWidget()
        add_month_statistics([self.income_category.id], expense_ids, rows, core.current_month)
        texts: list[str] = [html_to_text(rows.item(i).text()) for i in range(rows.count())]

        cheapest: list[str] = [
            text.strip() for text in texts
            if text.strip().startswith(html_to_text(LanguageStructure.Statistics.get_translation(20)).strip())
        ]
        self.assertEqual(len(cheapest), 1, texts)
        self.assertIn("Rent (80.0)", cheapest[0])
        self.assertTrue(any(text.startswith("Travel - 0.0") for text in texts), texts)
        self.assertTrue(any(text.startswith("Rent - 80.0") for text in texts), texts)

    def test_custom_range_shares_use_selected_categories(self) -> None:
        """Compute custom-range shares from selected categories only, ignoring excluded transactions."""
        core: AppCore = AppCore.instance()
        transaction_date: date = self.expenses_transaction.date
        selection = WindowsRegistry.CustomRangeStatistics.categories_selection
        selected: dict[int, tuple[Category, str]] = {
            self.income_category.id: (core.categories[self.income_category.id], self.translated_incomes)
        }
        for position, (name, category_type, total, is_selected) in enumerate((
            ("Groceries", CategoryType.Expense, 150.0, True),
            ("Rent", CategoryType.Expense, 350.0, True),
            ("Excluded expense", CategoryType.Expense, 700.0, False),
            ("Excluded income", CategoryType.Income, 900.0, False),
        )):
            core.db.category_query.create_category(name, category_type, position + 1)
            category = core.db.category_query.get_category(name, category_type)
            assert category is not None
            core.db.transaction_query.add_transaction(category.id, transaction_date, total, name)
            core.categories[category.id] = load_category(
                category, core.db, core.current_year, core.current_month
            )
            if is_selected:
                selected[category.id] = (core.categories[category.id], self.translated_expenses)

        selection.clear_categories_selection()
        selection.selected_categories_data.update(selected)
        from_date: QDate = QDate(transaction_date.year, transaction_date.month, transaction_date.day)
        WindowsRegistry.CustomRangeStatistics.from_date.setDate(from_date.addDays(-10))
        WindowsRegistry.CustomRangeStatistics.to_date.setDate(from_date.addDays(10))

        def _check_shares() -> None:
            """Check totals and the share of the selected 150 expense row."""
            statistics_list: QListWidget = WindowsRegistry.CustomRangeStatisticsView.statistics_list
            texts: list[str] = [
                html_to_text(statistics_list.item(i).text()) for i in range(statistics_list.count())
            ]
            WindowsRegistry.CustomRangeStatisticsView.done(1)

            self.assertIn(html_to_text(_expense_total_text(1000.0, 500.0)), texts)
            groceries: list[str] = [text for text in texts if text.startswith("Groceries - 150.0")]
            self.assertEqual(len(groceries), 1, texts)
            self.assertIn(
                f"(15% {LanguageStructure.Statistics.get_translation(42)}, "
                f"30% {LanguageStructure.Statistics.get_translation(43)})",
                groceries[0],
            )

        QTimer.singleShot(100, self.catch_failure(_check_shares))
        show_custom_range_statistics_view()
        selection.clear_categories_selection()
        qsleep(300)

