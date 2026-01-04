from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date
from PySide6.QtCore import QTimer, QDate
from calendar import monthrange
from textwrap import dedent

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from languages import LanguageStructure
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry

if TYPE_CHECKING:
    from typing import Callable


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
            f"{LanguageStructure.Statistics.get_translation(5)}{round(1000/days_amount, 2)}<br/>",
            f"{LanguageStructure.Statistics.get_translation(6)}1000.0",
            f"{LanguageStructure.Statistics.get_translation(7)}{round(1000/days_amount, 2)}<br/>",
            f"{LanguageStructure.Statistics.get_translation(8)}0.0",
            f"<br/><br/>{self.translated_incomes}",
            f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name}  (1000.0)",
            f"<br/>{LanguageStructure.Statistics.get_translation(11)}",
            f"Test income transaction - 1000.0",
            f"<br/><br/>{self.translated_expenses}",
            f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name}  (1000.0)",
            f"<br/>{LanguageStructure.Statistics.get_translation(19)}",
            f"Test expenses transaction - 1000.0",]
    

    def generate_custom_range_statistics_transactions(self, transaction_value: float, transaction_name: str) -> list[str]:
        result = []
        for month in range(1, 7):
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

                self.assertEqual(
                    len(expected_monthly_statistics), WindowsRegistry.MonthlyStatistics.statistics.count(),
                    (
                        f"Month statistics have another amount of rows. Expected amount "
                        f"{len(expected_monthly_statistics)} found "
                        f"{WindowsRegistry.MonthlyStatistics.statistics.count()} rows"
                    )
                )

                for index, expected_row in enumerate(expected_monthly_statistics):
                    self.assertEqual(
                        expected_row, WindowsRegistry.MonthlyStatistics.statistics.item(index).text(),
                        f"In month statistics row {index} expected result {expected_row} not \
                        {WindowsRegistry.MonthlyStatistics.statistics.item(index).text()}"
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
                        f"{LanguageStructure.Statistics.get_translation(5)}{round(total_income/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(6)}{total_expense}",
                        f"{LanguageStructure.Statistics.get_translation(7)}{round(total_expense/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(8)}0.0",
                        f"<br/><br/>{self.translated_incomes}",
                        f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name} ({total_income}) <br/>",
                        f"{self.income_category.name} - {total_income}",
                        f"<br/><br/>{self.translated_expenses}",
                        f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name} ({total_expense}) <br/>",
                        f"{self.expenses_category.name} - {total_expense}",]

                    statistics_data = quarter.total_quarter_statistics.data
                    self.assertEqual(
                        len(expected_total_quarterly_statistics), statistics_data.count(),
                        f"Quarterly statistics have another amount of rows. Expected amount \
                        {len(expected_total_quarterly_statistics)} found {statistics_data.count()} rows"
                        )

                    for index, expected_row in enumerate(expected_total_quarterly_statistics):
                        self.assertEqual(
                            expected_row, statistics_data.item(index).text(),
                            f"In quarterly statistics row {index} expected result {expected_row} not \
                            {statistics_data.item(index).text()}"
                        )

                    for month in quarter.months:
                        statistics_data = month.data

                        current_month = month.month_number
                        _, month_days_amount = monthrange(app_core.current_year, current_month)
                        expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)

                        if current_month != month_without_transactions:
                            self.assertEqual(
                                len(expected_monthly_statistics), statistics_data.count(),
                                f"Month {current_month} statistics have another amount of rows. Expected amount \
                                {len(expected_monthly_statistics)} found {statistics_data.count()} rows"
                            )

                            for index, expected_row in enumerate(expected_monthly_statistics):
                                self.assertEqual(
                                    expected_row, statistics_data.item(index).text(),
                                    f"In quarter {quarter_number} month {current_month} statistics row \
                                    {index} expected result {expected_row} not {statistics_data.item(index).text()}"
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
            
            QTimer.singleShot(100, self.catch_failure(_check_quarterly_statistics))
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
                    f"{LanguageStructure.Statistics.get_translation(6)}{total_expense}",
                    f"{LanguageStructure.Statistics.get_translation(27)}{round(total_expense/12, 2)}",
                    f"{LanguageStructure.Statistics.get_translation(26)}{round(total_expense/days_amount, 2)}<br/>",
                    f"{LanguageStructure.Statistics.get_translation(8)}0.0",
                    f"<br/><br/>{self.translated_incomes}",
                    f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name} ({total_income}) <br/>",
                    f"{self.income_category.name} - {total_income}",
                    f"<br/><br/>{self.translated_expenses}",
                    f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name} ({total_expense}) <br/>",
                    f"{self.expenses_category.name} - {total_expense}"]

                statistics_data = WindowsRegistry.YearlyStatistics.statistics.total_year_statistics.data
                self.assertEqual(
                    len(expected_yearly_statistics), statistics_data.count(),
                    f"Yearly statistics have another amount of rows. Expected amount \
                    {len(expected_yearly_statistics)} found {statistics_data.count()} rows"
                    )

                for index, expected_row in enumerate(expected_yearly_statistics):
                    self.assertEqual(
                        expected_row, statistics_data.item(index).text(),
                        f"In total year statistics row {index} expected result \
                        {expected_row} not {statistics_data.item(index).text()}"
                    )

                for month in WindowsRegistry.YearlyStatistics.statistics.months:
                    statistics_data = month.data

                    _, month_days_amount = monthrange(app_core.current_year, month.month_number)
                    expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)

                    if month.month_number != month_without_transactions:
                        self.assertEqual(
                            len(expected_monthly_statistics), statistics_data.count(),
                            f"Month {month.month_number} statistics have another amount of rows. Expected amount \
                            {len(expected_monthly_statistics)} found {statistics_data.count()} rows"
                        )

                        for index, expected_row in enumerate(expected_monthly_statistics):
                            self.assertEqual(
                                expected_row, statistics_data.item(index).text(),
                                f"In month {month.month_number} statistics row {index} expected result \
                                {expected_row} not {statistics_data.item(index).text()}"
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
        day = date.today().day
        for month in range(1, 7):
            if month != app_core.current_month:
                year = app_core.current_year
                app_core.db.transaction_query.add_transaction(
                    self.income_category.id, date(year, month, day), 1000, "Test income transaction"
                )
                app_core.db.transaction_query.add_transaction(
                    self.expenses_category.id, date(year, month, day), 1000, "Test expenses transaction"
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
                        f"{LanguageStructure.Statistics.get_translation(6)}{total_expense}",
                        f"{LanguageStructure.Statistics.get_translation(26)}{round(total_expense/days_amount, 2)}<br/>",
                        f"{LanguageStructure.Statistics.get_translation(8)}0.0",
                        f"<br/><br/>{self.translated_incomes}",
                        f"{LanguageStructure.Statistics.get_translation(9)}{self.income_category.name} ({total_income}) <br/>",
                        f"{self.income_category.name} - {total_income}",
                        f"<br/><br/>{self.translated_expenses}",
                        f"{LanguageStructure.Statistics.get_translation(17)}{self.expenses_category.name} ({total_expense}) <br/>",
                        f"{self.expenses_category.name} - {total_expense}"]

                    statistics_data = WindowsRegistry.CustomRangeStatisticsView.statistics_list
                    self.assertEqual(
                        len(expected_custom_range_statistics), statistics_data.count(),
                        f"Custom range statistics (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                        have another amount of rows. Expected amount \
                        {len(expected_custom_range_statistics)} found {statistics_data.count()} rows"
                    )

                    for index, expected_row in enumerate(expected_custom_range_statistics):
                        self.assertEqual(
                            expected_row, statistics_data.item(index).text(),
                            f"In Custom range statistics (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                            statistics row {index} expected result {expected_row} not \
                            {statistics_data.item(index).text()}"
                        )
                    
                    expected_transactions = [
                        f"{self.translated_incomes}<br/>",
                        f"<br/>{self.income_category.name}<br/>",
                        *self.generate_custom_range_statistics_transactions(1000.0, "Test income transaction"),
                        f"<br/><br/>{self.translated_expenses}<br/>",
                        f"<br/>{self.expenses_category.name}<br/>",
                        *self.generate_custom_range_statistics_transactions(1000.0, "Test expenses transaction")
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
                            expected_row, statistics_data.item(index).text(),
                            f"In Custom range transactions list (01/01/{app_core.current_year} - 01/06/{app_core.current_year}) \
                            row {index} expected result {expected_row} not \
                            {statistics_data.item(index).text()}"
                        )
                    
                    WindowsRegistry.CustomRangeStatisticsView.done(1)
                    WindowsRegistry.CustomRangeStatistics.done(1)

                QTimer.singleShot(100, self.catch_failure(_check_custom_range_statistics))
                self.click_on_widget(WindowsRegistry.CustomRangeStatistics.show_statistics)

            QTimer.singleShot(100, self.catch_failure(_select_custom_range))
            self.click_on_widget(WindowsRegistry.StatisticsWindow.custom_range_statistics)

        self.open_statistics_window(_open_custom_range_statistics_window)
        qsleep(500)




