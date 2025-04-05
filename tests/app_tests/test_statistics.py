from datetime import date
from PySide6.QtCore import QTimer, QDate
from tests.tests_toolkit import DBTestCase, qsleep

from languages import LANGUAGES
from project_configuration import MONTHS_DAYS
from AppObjects.session import Session

from GUI.windows.main_window import MainWindow
from GUI.windows.messages import Messages
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics, CustomRangeStatistics, CustomRangeStatisticsView


class TestStatistics(DBTestCase):

    def setUp(self):
        """Set up the test case. It creates translations so you don't have to create them in every test case."""

        self.statistics_words = LANGUAGES[Session.language]["Windows"]["Statistics"]
        self.translated_incomes = LANGUAGES[Session.language]["Windows"]["Main"][1]
        self.translated_expenses = LANGUAGES[Session.language]["Windows"]["Main"][2]


    def open_statistics_window(self, func):
        """Open statistics window and call function after some delay."""

        QTimer.singleShot(100, func)
        MainWindow.statistics.click()
    

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
            f"{self.statistics_words[4]}1000.0",
            f"{self.statistics_words[5]}{round(1000/days_amount, 2)}\n",
            f"{self.statistics_words[6]}1000.0",
            f"{self.statistics_words[7]}{round(1000/days_amount, 2)}\n",
            f"{self.statistics_words[8]}0.0",
            f"\n\n{self.translated_incomes}",
            f"{self.statistics_words[9]}{self.income_category.name}  (1000.0)",
            f"\n{self.statistics_words[11]}",
            f"Test income transaction - 1000.0",
            f"\n\n{self.translated_expenses}",
            f"{self.statistics_words[17]}{self.expenses_category.name}  (1000.0)",
            f"\n{self.statistics_words[19]}",
            f"Test expenses transaction - 1000.0",]


    def test_1_show_monthly_statistics(self):
        """Test showing monthly statistics."""

        days_amount = MONTHS_DAYS[Session.current_month-1] + (Session.current_month == 2 and Session.current_year % 4 == 0)

        def _open_monthly_statics_window():
            """Click button that show monthly statistics window."""

            def _check_monthly_statistics():
                """Check if monthly statistics are correct."""

                expected_monthly_statistics = self.create_monthly_statistics(days_amount)

                self.assertEqual(
                    len(expected_monthly_statistics), MonthlyStatistics.statistics.count(),
                    f"Month statistics have another amount of rows. Expected amount {len(expected_monthly_statistics)} found {MonthlyStatistics.statistics.count()} rows")

                for index, expected_row in enumerate(expected_monthly_statistics):
                    self.assertEqual(
                        expected_row, MonthlyStatistics.statistics.item(index).text(),
                        f"In month statistics row {index} expected result {expected_row} not {MonthlyStatistics.statistics.item(index).text()}")
                    
                MonthlyStatistics.window.done(1)
            
            QTimer.singleShot(100, _check_monthly_statistics)
            StatisticsWindow.monthly_statistics.click()
        self.open_statistics_window(_open_monthly_statics_window)
        qsleep(500)
    

    def test_2_show_quarterly_statistics(self):
        """Test showing quarterly statistics."""

        month_without_transactions = 12 if Session.current_month != 12 else 1
        quarter_without_transaction = 4 if Session.current_month != 12 else 1

        for month in range(1, 13):
            if month not in (Session.current_month, month_without_transactions):
                Session.db.transaction_query.add_transaction(self.income_category.id, Session.current_year, month, 1, 1000, "Test income transaction")
                Session.db.transaction_query.add_transaction(self.expenses_category.id, Session.current_year, month, 1, 1000, "Test expenses transaction")
        
        def _open_quarterly_statistics_window():
            """Click button that show quarterly statistics window."""

            def _check_quarterly_statistics():
                """Check if quarterly statistics are correct."""

                for quarter in QuarterlyStatistics.statistics.quarters:
                    quarter_number = quarter.quarter_number
                    days_amount = sum(MONTHS_DAYS[(quarter_number-1)*3:quarter_number*3]) + (quarter_number == 1 and Session.current_year % 4 == 0)

                    if quarter_number != quarter_without_transaction:
                        total_income = 3000.0
                        total_expense = 3000.0
                    else:
                        total_income = 2000.0
                        total_expense = 2000.0

                    expected_total_quarterly_statistics = [
                        f"{self.statistics_words[4]}{total_income}",
                        f"{self.statistics_words[5]}{round(total_income/days_amount, 2)}\n",
                        f"{self.statistics_words[6]}{total_expense}",
                        f"{self.statistics_words[7]}{round(total_expense/days_amount, 2)}\n",
                        f"{self.statistics_words[8]}0.0",
                        f"\n\n{self.translated_incomes}",
                        f"{self.statistics_words[9]}{self.income_category.name} ({total_income}) \n",
                        f"{self.income_category.name} - {total_income}",
                        f"\n\n{self.translated_expenses}",
                        f"{self.statistics_words[17]}{self.expenses_category.name} ({total_expense}) \n",
                        f"{self.expenses_category.name} - {total_expense}",]

                    statistics_data = quarter.total_quarter_statistics.data
                    self.assertEqual(
                        len(expected_total_quarterly_statistics), statistics_data.count(),
                        f"Quarterly statistics have another amount of rows. Expected amount {len(expected_total_quarterly_statistics)} found {statistics_data.count()} rows")

                    for index, expected_row in enumerate(expected_total_quarterly_statistics):
                        self.assertEqual(
                            expected_row, statistics_data.item(index).text(),
                            f"In quarterly statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}")

                    for month in quarter.months:
                        statistics_data = month.data

                        current_month = month.month_number
                        month_days_amount = MONTHS_DAYS[current_month-1] + (current_month == 2 and Session.current_year % 4 == 0)
                        expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)

                        if current_month != month_without_transactions:
                            self.assertEqual(
                                len(expected_monthly_statistics), statistics_data.count(),
                                f"Month {current_month} statistics have another amount of rows. Expected amount {len(expected_monthly_statistics)} found {statistics_data.count()} rows")

                            for index, expected_row in enumerate(expected_monthly_statistics):
                                self.assertEqual(
                                    expected_row, statistics_data.item(index).text(),
                                    f"In quarter {quarter_number} month {current_month} statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}")

                        else:
                            self.assertEqual(1, statistics_data.count(), f"Month {current_month} without transactions don't have 1 row in statistics")
                            self.assertEqual(Messages.no_transactions.text(), statistics_data.item(0).text(), "Month without transactions hasn't showed error text")

                QuarterlyStatistics.window.done(1)
            
            QTimer.singleShot(100, _check_quarterly_statistics)
            StatisticsWindow.quarterly_statistics.click()
        
        self.open_statistics_window(_open_quarterly_statistics_window)
        qsleep(2000)
                        

    def test_3_show_yearly_statistics(self):
        """Test showing yearly statistics."""

        month_without_transactions = 12 if Session.current_month != 12 else 1

        for month in range(1, 13):
            if month not in (Session.current_month, month_without_transactions):
                Session.db.transaction_query.add_transaction(self.income_category.id, Session.current_year, month, 1, 1000, "Test income transaction")
                Session.db.transaction_query.add_transaction(self.expenses_category.id, Session.current_year, month, 1, 1000, "Test expenses transaction")
        
        def _open_yearly_statistics_window():
            """Click button that show yearly statistics window."""

            def _check_yearly_statistics():
                """Check if yearly statistics are correct."""

                days_amount = 365 if Session.current_year % 4 != 0 else 366

                total_income = 11000.0
                total_expense = 11000.0

                expected_yearly_statistics = [
                    f"{self.statistics_words[4]}{total_income}",
                    f"{self.statistics_words[25]}{round(total_income/12, 2)}",
                    f"{self.statistics_words[24]}{round(total_income/days_amount, 2)}\n",
                    f"{self.statistics_words[6]}{total_expense}",
                    f"{self.statistics_words[27]}{round(total_expense/12, 2)}",
                    f"{self.statistics_words[26]}{round(total_expense/days_amount, 2)}\n",
                    f"{self.statistics_words[8]}0.0",
                    f"\n\n{self.translated_incomes}",
                    f"{self.statistics_words[9]}{self.income_category.name} ({total_income}) \n",
                    f"{self.income_category.name} - {total_income}",
                    f"\n\n{self.translated_expenses}",
                    f"{self.statistics_words[17]}{self.expenses_category.name} ({total_expense}) \n",
                    f"{self.expenses_category.name} - {total_expense}"]

                statistics_data = YearlyStatistics.statistics.total_year_statistics.data
                self.assertEqual(
                    len(expected_yearly_statistics), statistics_data.count(),
                    f"Yearly statistics have another amount of rows. Expected amount {len(expected_yearly_statistics)} found {statistics_data.count()} rows")

                for index, expected_row in enumerate(expected_yearly_statistics):
                    self.assertEqual(
                        expected_row, statistics_data.item(index).text(),
                        f"In total year statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}")

                for month in YearlyStatistics.statistics.months:
                    statistics_data = month.data

                    month_days_amount = MONTHS_DAYS[month.month_number-1] + (month.month_number == 2 and Session.current_year % 4 == 0)
                    expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)

                    if month.month_number != month_without_transactions:
                        self.assertEqual(
                            len(expected_monthly_statistics), statistics_data.count(),
                            f"Month {month.month_number} statistics have another amount of rows. Expected amount {len(expected_monthly_statistics)} found {statistics_data.count()} rows")

                        for index, expected_row in enumerate(expected_monthly_statistics):
                            self.assertEqual(
                                expected_row, statistics_data.item(index).text(),
                                f"In month {month.month_number} statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}")

                    else:
                        self.assertEqual(1, statistics_data.count(), f"Month {month.month_number} without transactions don't have 1 row in statistics")
                        self.assertEqual(Messages.no_transactions.text(), statistics_data.item(0).text(), "Month without transactions hasn't showed error text")

                YearlyStatistics.window.done(1)
            
            QTimer.singleShot(100, _check_yearly_statistics)
            StatisticsWindow.yearly_statistics.click()
        
        self.open_statistics_window(_open_yearly_statistics_window)
        qsleep(2000)
    

    def test_4_show_custom_range_statistics(self):
        """Test showing custom range statistics."""

        for month in range(1, 7):
            if month != Session.current_month:
                Session.db.transaction_query.add_transaction(self.income_category.id, Session.current_year, month, 1, 1000, "Test income transaction")
                Session.db.transaction_query.add_transaction(self.expenses_category.id, Session.current_year, month, 1, 1000, "Test expenses transaction")
        
        def _open_custom_range_statistics_window():
            """Click button that show custom range statistics window."""

            def _select_custom_range():
                """Select custom range and click show statistics button."""

                CustomRangeStatistics.add_all_incomes_categories.click()
                CustomRangeStatistics.add_all_expenses_categories.click()
                
                CustomRangeStatistics.from_date.setDate(QDate(Session.current_year, 1, 1))
                CustomRangeStatistics.to_date.setDate(QDate(Session.current_year, 6, 1))

                def _check_custom_range_statistics():
                    """Check if custom range statistics are correct."""

                    total_income = 6000.0
                    total_expense = 6000.0
                    date_difference = date(Session.current_year, 6, 1) - date(Session.current_year, 1, 1)
                    days_amount = date_difference.days

                    expected_custom_range_statistics = [
                        f"{self.statistics_words[4]}{total_income}",
                        f"{self.statistics_words[24]}{round(total_income/days_amount, 2)}\n",
                        f"{self.statistics_words[6]}{total_expense}",
                        f"{self.statistics_words[26]}{round(total_expense/days_amount, 2)}\n",
                        f"{self.statistics_words[8]}0.0",
                        f"\n\n{self.translated_incomes}",
                        f"{self.statistics_words[9]}{self.income_category.name} ({total_income}) \n",
                        f"{self.income_category.name} - {total_income}",
                        f"\n\n{self.translated_expenses}",
                        f"{self.statistics_words[17]}{self.expenses_category.name} ({total_expense}) \n",
                        f"{self.expenses_category.name} - {total_expense}"]

                    statistics_data = CustomRangeStatisticsView.statistics_list
                    self.assertEqual(
                        len(expected_custom_range_statistics), statistics_data.count(),
                        f"Custom range statistics (1, 1, {Session.current_year} - 1, 6, {Session.current_year}) have another amount of rows. Expected amount {len(expected_custom_range_statistics)} found {statistics_data.count()} rows")

                    for index, expected_row in enumerate(expected_custom_range_statistics):
                        self.assertEqual(
                            expected_row, statistics_data.item(index).text(),
                            f"In Custom range statistics (1, 1, {Session.current_year} - 1, 6, {Session.current_year}) statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}")
                    
                    expected_transactions = [
                        f"{self.translated_incomes}\n\n",
                        f"\n{self.income_category.name}\n",
                        f"01/01/{Session.current_year}\t1000.0\tTest income transaction",
                        f"01/02/{Session.current_year}\t1000.0\tTest income transaction",
                        f"01/03/{Session.current_year}\t1000.0\tTest income transaction",
                        f"01/04/{Session.current_year}\t1000.0\tTest income transaction",
                        f"01/05/{Session.current_year}\t1000.0\tTest income transaction",
                        f"01/06/{Session.current_year}\t1000.0\tTest income transaction",
                        f"\n\n\n{self.translated_expenses}\n\n",
                        f"\n{self.expenses_category.name}\n",
                        f"01/01/{Session.current_year}\t1000.0\tTest expenses transaction",
                        f"01/02/{Session.current_year}\t1000.0\tTest expenses transaction",
                        f"01/03/{Session.current_year}\t1000.0\tTest expenses transaction",
                        f"01/04/{Session.current_year}\t1000.0\tTest expenses transaction",
                        f"01/05/{Session.current_year}\t1000.0\tTest expenses transaction",
                        f"01/06/{Session.current_year}\t1000.0\tTest expenses transaction",]

                    statistics_data = CustomRangeStatisticsView.transactions_list
                    self.assertEqual(
                        len(expected_transactions), statistics_data.count(),
                        f"Custom range transactions list (1, 1, {Session.current_year} - 1, 6, {Session.current_year}) have another amount of rows. Expected amount {len(expected_transactions)} found {statistics_data.count()} rows")

                    for index, expected_row in enumerate(expected_transactions):
                        self.assertEqual(
                            expected_row, statistics_data.item(index).text(),
                            f"In Custom range transactions list (1, 1, {Session.current_year} - 1, 6, {Session.current_year}) row {index} expected result {expected_row} not {statistics_data.item(index).text()}")
                    
                    CustomRangeStatisticsView.window.done(1)
                    CustomRangeStatistics.window.done(1)

                QTimer.singleShot(100, _check_custom_range_statistics)
                CustomRangeStatistics.show_statistics.click()

            QTimer.singleShot(100, _select_custom_range)
            StatisticsWindow.custom_range_statistics.click()

        self.open_statistics_window(_open_custom_range_statistics_window)
        qsleep(500)




