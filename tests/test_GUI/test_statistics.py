from PySide6.QtCore import QTimer
from tests.tests_toolkit import DBTestCase

from languages import LANGUAGES
from project_configuration import MONTHS_DAYS
from AppObjects.session import Session

from GUI.windows.main_window import MainWindow
from GUI.windows.errors import Errors
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistics, QuarterlyStatistics, YearlyStatistics


class TestStatistics(DBTestCase):

    def setUp(self):
        self.statistics_words = LANGUAGES[Session.language]["Account"]["Info"]["Statistics"]
        self.translated_incomes = LANGUAGES[Session.language]["Account"]["Info"][4]
        self.translated_expenses = LANGUAGES[Session.language]["Account"]["Info"][5]


    def open_statistics_window(self, func):
        QTimer.singleShot(100, func)
        MainWindow.statistics.click()
    

    def create_monthly_statistics(self, days_amount:int) -> list[str]:
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
            f"Test expenses transaction - 1000.0",
        ]


    def test_show_monthly_statistics(self):
        days_amount = MONTHS_DAYS[Session.current_month-1] + (Session.current_month == 2 and Session.current_year % 4 == 0)

        def open_monthly_statics_window():
            def check_monthly_statistics():
                expected_monthly_statistics = self.create_monthly_statistics(days_amount)

                self.assertEqual(
                    len(expected_monthly_statistics), MonthlyStatistics.statistics.count(),
                    f"Month statistics have another amount of rows. Expected amount {len(expected_monthly_statistics)} found {MonthlyStatistics.statistics.count()} rows"
                )

                for index, expected_row in enumerate(expected_monthly_statistics):
                    self.assertEqual(
                        expected_row, MonthlyStatistics.statistics.item(index).text(),
                        f"In month statistics row {index} expected result {expected_row} not {MonthlyStatistics.statistics.item(index).text()}"
                    )
                MonthlyStatistics.window.done(1)
                StatisticsWindow.window.done(1)
            
            QTimer.singleShot(100, check_monthly_statistics)
            StatisticsWindow.monthly_statistics.click()
        self.open_statistics_window(open_monthly_statics_window)
    

    def test_show_quarterly_statistics(self):
        month_without_transactions = 12 if Session.current_month != 12 else 1

        for month in range(1, 13):
            if month not in (Session.current_month, month_without_transactions):
                Session.db.add_transaction(self.income_category.id, Session.current_year, month, 1, 1000, "Test income transaction")
                Session.db.add_transaction(self.expenses_category.id, Session.current_year, month, 1, 1000, "Test expenses transaction")
        
        def open_quarterly_statistics_window():
            def check_quarterly_statistics():
                for quarter in range(1, 5):
                    days_amount = sum(MONTHS_DAYS[(quarter-1)*3:quarter*3]) 
                    days_amount += 1 if quarter == 1 and Session.current_year % 4 == 0 else 0

                    for statistic_list in range(4):
                        statistics_data = QuarterlyStatistics.statistics[quarter][statistic_list]["Statistic Data"]

                        if statistic_list == 0:
                            if quarter != 4:
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
                                f"{self.expenses_category.name} - {total_expense}",
                            ]

                            self.assertEqual(
                                len(expected_total_quarterly_statistics), statistics_data.count(),
                                f"Quarterly statistics have another amount of rows. Expected amount {len(expected_total_quarterly_statistics)} found {statistics_data.count()} rows"
                            )

                            for index, expected_row in enumerate(expected_total_quarterly_statistics):
                                self.assertEqual(
                                    expected_row, statistics_data.item(index).text(),
                                    f"In quarterly statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}"
                                )

                        else:
                            current_month = (quarter -1)*3 + statistic_list
                            month_days_amount = MONTHS_DAYS[current_month-1] + (current_month == 2 and Session.current_year % 4 == 0)
                            expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)

                            if current_month != month_without_transactions:
                                self.assertEqual(
                                    len(expected_monthly_statistics), statistics_data.count(),
                                    f"Month {current_month} statistics have another amount of rows. Expected amount {len(expected_monthly_statistics)} found {statistics_data.count()} rows"
                                )

                                for index, expected_row in enumerate(expected_monthly_statistics):
                                    self.assertEqual(
                                        expected_row, statistics_data.item(index).text(),
                                        f"In quarter {quarter} month {statistic_list} statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}"
                                    )

                            else:
                                self.assertEqual(1, statistics_data.count(), f"Month {current_month} without transactions don't have 1 row in statistics")
                                self.assertEqual(Errors.no_transactions.text(), statistics_data.item(0).text(), "Month without transactions hasn't showed error text")

                QuarterlyStatistics.window.done(1)
                StatisticsWindow.window.done(1)
            
            QTimer.singleShot(100, check_quarterly_statistics)
            StatisticsWindow.quarterly_statistics.click()
        
        self.open_statistics_window(open_quarterly_statistics_window)
                        

    def test_show_yearly_statistics(self):
        month_without_transactions = 12 if Session.current_month != 12 else 1

        for month in range(1, 13):
            if month not in (Session.current_month, month_without_transactions):
                Session.db.add_transaction(self.income_category.id, Session.current_year, month, 1, 1000, "Test income transaction")
                Session.db.add_transaction(self.expenses_category.id, Session.current_year, month, 1, 1000, "Test expenses transaction")
        
        def open_yearly_statistics_window():
            def check_yearly_statistics():
                days_amount = 365 if Session.current_year % 4 != 0 else 366

                for statistic_list in range(13):
                    statistics_data = YearlyStatistics.statistics[statistic_list]["Statistic Data"]

                    if statistic_list == 0:
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
                            f"{self.expenses_category.name} - {total_expense}"
                        ]

                        self.assertEqual(
                            len(expected_yearly_statistics), statistics_data.count(),
                            f"Yearly statistics have another amount of rows. Expected amount {len(expected_yearly_statistics)} found {statistics_data.count()} rows"
                        )

                        for index, expected_row in enumerate(expected_yearly_statistics):
                            self.assertEqual(
                                expected_row, statistics_data.item(index).text(),
                                f"In quarterly statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}"
                            )
                    else:
                        month_days_amount = MONTHS_DAYS[statistic_list-1] + (statistic_list == 2 and Session.current_year % 4 == 0)
                        expected_monthly_statistics = self.create_monthly_statistics(month_days_amount)

                        if statistic_list != month_without_transactions:
                            self.assertEqual(
                                len(expected_monthly_statistics), statistics_data.count(),
                                f"Month {statistic_list} statistics have another amount of rows. Expected amount {len(expected_monthly_statistics)} found {statistics_data.count()} rows"
                            )

                            for index, expected_row in enumerate(expected_monthly_statistics):
                                self.assertEqual(
                                    expected_row, statistics_data.item(index).text(),
                                    f"In month {statistic_list} statistics row {index} expected result {expected_row} not {statistics_data.item(index).text()}"
                                )

                        else:
                            self.assertEqual(1, statistics_data.count(), f"Month {statistic_list} without transactions don't have 1 row in statistics")
                            self.assertEqual(Errors.no_transactions.text(), statistics_data.item(0).text(), "Month without transactions hasn't showed error text")

                
                YearlyStatistics.window.done(1)
                StatisticsWindow.window.done(1)
            
            QTimer.singleShot(100, check_yearly_statistics)
            StatisticsWindow.yearly_statistics.click()
        
        self.open_statistics_window(open_yearly_statistics_window)



