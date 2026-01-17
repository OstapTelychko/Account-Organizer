from __future__ import annotations
from typing import Callable, cast
from PySide6.QtCore import QTimer, QDate
from datetime import date
import random

from tests.tests_toolkit import DBTestCase
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_core import AppCore



class TestSearch(DBTestCase):
    """
    Performs tests on the search transactions functionality.
    """

    transaction_regex = r"%s[\s\S]+\(%s\)"    

    def get_search_result(self) -> str:
        """
        Returns the text representation of the search results.
        """

        result = ""
        for row in range(WindowsRegistry.SearchWindow.transactions_list.count()):
            result += WindowsRegistry.SearchWindow.transactions_list.item(row).text()
        return result


    def open_search_window(self, func:Callable[[], None]) -> None:
        """
        Opens the search window.
        """

        QTimer.singleShot(10, func)
        self.click_on_widget(WindowsRegistry.MainWindow.search)
    

    def fill_search_fields_and_perform_search(
            self,
            search_name:str="",
            search_value:str="",
            operand:str="=",
            date_range:str|tuple[QDate, QDate]="month"
        ) -> str:
        """
        Fills the search fields and performs the search.

        Arguments:
            search_name: The name to search for.
            search_value: The value to search for.
            operand: The operand to use for the value comparison.
            date_range: The date range to search within. Can be "month", "year", or a tuple of start and end dates.

        Returns the search results as a string.
        """

        WindowsRegistry.SearchWindow.search_name.setText(search_name)
        WindowsRegistry.SearchWindow.search_value.setText(search_value)
        WindowsRegistry.SearchWindow.value_operands.setCurrentText(operand)
        if isinstance(date_range, str):
            if date_range == "month":
                self.click_on_widget(WindowsRegistry.SearchWindow.date_selection.select_month_range_button)
            elif date_range == "year":
                self.click_on_widget(WindowsRegistry.SearchWindow.date_selection.select_year_range_button)
        else:
            WindowsRegistry.SearchWindow.date_selection.search_from_date.setDate(date_range[0])
            WindowsRegistry.SearchWindow.date_selection.search_to_date.setDate(date_range[1])
        self.click_on_widget(WindowsRegistry.SearchWindow.search)
        return self.get_search_result()
    

    def test_01_perform_search_where_transaction_expected_to_be_found(self) -> None:
        """
        Tests searching for transactions with a different values and operands where transactions are expected to be found.
        """

        #Two transaction are created before test execution with values 1000 each.
        params = [
            ("1", ">", "value is above 1"),
            ("1000", ">=", "value is above or equal to 1000"),
            ("1000", "=", "value is below 1000"),
            ("5000", "<=", "value is below or equal to 5000"),
            ("4000", "<", "value is below 4000"),
            ("999", "!=", "value is not equal to 999"),
        ]
        for search_value, operand, message in params:
            with self.subTest(search_value=search_value, operand=operand, message=message):
                def perform_search() -> None:
                    "Performs the search operation and validates the results."

                    result = self.fill_search_fields_and_perform_search(search_value=search_value, operand=operand)
                    income_transaction_pattern = self.transaction_regex % (self.test_income_transaction_name, self.income_category.name)

                    self.assertRegexpMatches(
                        result, income_transaction_pattern,
                        f"Income transaction with name {self.test_income_transaction_name} not found in search results"
                        f" when attempting to search for transactions where {message}")
                    expenses_transaction_pattern = self.transaction_regex % (self.test_expenses_transaction_name, self.expenses_category.name)
                    self.assertRegexpMatches(
                        result, expenses_transaction_pattern,
                        f"Expense transaction with name {self.test_expenses_transaction_name} not found in search results"
                        f" when attempting to search for transactions where {message}")
                    WindowsRegistry.SearchWindow.done(0)
                    
                self.open_search_window(perform_search)
    

    def test_02_perform_search_where_transaction_expected_not_to_be_found(self) -> None:
        """
        Tests searching for transactions with a different values and operands where transactions are not expected to be found.
        """

        #Two transaction are created before test execution with values 1000 each.
        params = [
            ("5000", ">", "value is above 5000"),
            ("1500", ">=", "value is above or equal to 1500"),
            ("500", "=", "value is equal to 500"),
            ("500", "<=", "value is below or equal to 500"),
            ("1", "<", "value is below 1"),
            ("1000", "!=", "value is not equal to 1000"),
        ]
        for search_value, operand, message in params:
            with self.subTest(search_value=search_value, operand=operand, message=message):
                def perform_search() -> None:
                    "Performs the search operation and validates the results."

                    result = self.fill_search_fields_and_perform_search(search_value=search_value, operand=operand)
                    income_transaction_pattern = self.transaction_regex % (self.test_income_transaction_name, self.income_category.name)

                    self.assertNotRegexpMatches(
                        result, income_transaction_pattern,
                        f"Income transaction with name {self.test_income_transaction_name} found in search results"
                        f" when attempting to search for transactions where {message}")
                    expenses_transaction_pattern = self.transaction_regex % (self.test_expenses_transaction_name, self.expenses_category.name)
                    self.assertNotRegexpMatches(
                        result, expenses_transaction_pattern,
                        f"Expense transaction with name {self.test_expenses_transaction_name} found in search results"
                        f" when attempting to search for transactions where {message}")
                    WindowsRegistry.SearchWindow.done(0)
                    
                self.open_search_window(perform_search)
    

    def test_03_perform_search_on_newly_added_transaction(self) -> None:
        """
        Tests searching for a newly added transaction.
        Executing conditions where the new transaction is expected to be found or not found.
        """

        new_transaction_name = "New Test Transaction"
        new_transaction_value = random.randint(1100, 10000)

     
        app_core = AppCore.instance()
        app_core.db.transaction_query.add_transaction(
            self.income_category.id,
            date.today(),
            new_transaction_value,
            new_transaction_name
        )

        #Conditions when new created transaction is expected to be found in search results.
        parm_list_for_expected_to_be_found = [
            ("", "=", str(new_transaction_value), "value equals to new transaction value"),
            (new_transaction_name[:4], "=", str(new_transaction_value), "name starts with first 4 characters of new transaction name"),
            (new_transaction_name, "=", str(new_transaction_value), "name equals to new transaction name"),
            (new_transaction_name[:-4], ">=", str(new_transaction_value), "name starts with last 4 characters of new transaction name"),
            (new_transaction_name, ">", "", "name equals to new transaction name and value is greater than empty string"),
            (new_transaction_name, "<", "", "name equals to new transaction name and value is less than empty string"),
            ("", ">", "1", "value is greater than 1"),
            ("", "<", str(new_transaction_value + 1000), "value is less than new transaction value plus 1000"),
        ]

        #Conditions when new created transaction is not expected to be found in search results.
        parm_list_for_expected_not_to_be_found = [
            ("", "!=", str(new_transaction_value), "value is not equal to new transaction value"),
            (new_transaction_name + "XYZ", "=", str(new_transaction_value), "name is different than new transaction name"),
            (
                new_transaction_name, "<=",
                str(new_transaction_value - 1),
                "name equals to new transaction name and value is less than or equal to new transaction value minus 1"
            ),
            (
                new_transaction_name,
                ">=",
                str(new_transaction_value + 1),
                "name equals to new transaction name and value is greater than or equal to new transaction value plus 1"
            ),
            ("", "<", "1", "value is less than 1"),
            ("", ">", str(new_transaction_value + 1000), "value is greater than new transaction value plus 1000"),
        ]
        new_transaction_pattern = self.transaction_regex % (new_transaction_name, self.income_category.name)

        def perform_search_sub_test(search_name:str, operand:str, search_value:str, message:str, expected_to_be_found:bool) -> None:
            def perform_search() -> None:
                    "Performs the search operation and validates the results."

                    result = self.fill_search_fields_and_perform_search(
                        search_name=search_name,
                        search_value=search_value,
                        operand=operand
                    )

                    if expected_to_be_found:
                        self.assertRegexpMatches(
                            result, new_transaction_pattern,
                            f"Newly added transaction with name {new_transaction_name} and value {new_transaction_value} "
                            f"not found in search results. Searched where {message}"
                        )
                    else:
                        self.assertNotRegexpMatches(
                            result, new_transaction_pattern,
                            f"Newly added transaction with name {new_transaction_name} and value {new_transaction_value} "
                            f"found in search results. Searched where {message}"
                        )
                    WindowsRegistry.SearchWindow.done(0)

            self.open_search_window(perform_search)

        for search_name, operand, search_value, message in parm_list_for_expected_to_be_found:
            with self.subTest(search_name=search_name, operand=operand, search_value=search_value, message=message):
                perform_search_sub_test(search_name, operand, search_value, message, True)

        for search_name, operand, search_value, message in parm_list_for_expected_not_to_be_found:
            with self.subTest(search_name=search_name, operand=operand, search_value=search_value, message=message):
                perform_search_sub_test(search_name, operand, search_value, message, False)
    

    def test_04_perform_search_with_different_categories_selected(self) -> None:
        """
        Tests searching for transactions with different categories selected.
        """

        #Conditions for different categories selected.
        #category_ids, category_name, transaction_name, expected_to_be_found, message
        params = [
            (
                [self.income_category.id],
                self.income_category.name,
                self.test_income_transaction_name,
                True,
                "only income category selected"
            ),
            (
                [self.expenses_category.id],
                self.expenses_category.name,
                self.test_expenses_transaction_name,
                True,
                "only expenses category selected"
            ),
            (
                [self.income_category.id],
                self.expenses_category.name,
                self.test_expenses_transaction_name,
                False,
                "only income category selected but searching for transaction in expenses category"
            ),
            (
                [self.expenses_category.id],
                self.income_category.name,
                self.test_income_transaction_name,
                False,
                "only expenses category selected but searching for transaction in income category"
            ),
        ]

        for category_ids, category_name, transaction_name, expected_to_be_found, message in params:
            with self.subTest(
                category_ids=category_ids,
                category_name=category_name,
                transaction_name=transaction_name,
                expected_to_be_found=expected_to_be_found,
                message=message
                ):
                def perform_search() -> None:
                    "Performs the search operation and validates the results."

                    self.click_on_widget(WindowsRegistry.SearchWindow.categories_selection_button)
                    self.click_on_widget(WindowsRegistry.SearchWindow.categories_selection.remove_all_expenses_categories)
                    self.click_on_widget(WindowsRegistry.SearchWindow.categories_selection.remove_all_incomes_categories)

                    for category_id in category_ids:
                        category_item = WindowsRegistry.SearchWindow.categories_selection.categories[category_id]
                        self.click_on_widget(category_item.add_category_button)
                    
                    result = self.fill_search_fields_and_perform_search(search_name=transaction_name)
                    transaction_pattern = self.transaction_regex % (transaction_name, category_name)
                    if expected_to_be_found:
                        self.assertRegexpMatches(
                            result, transaction_pattern,
                            f"Transaction with name {transaction_name} not found in search results"
                            f" when {message}"
                        )
                    else:
                        self.assertNotRegexpMatches(
                            result, transaction_pattern,
                            f"Transaction with name {transaction_name} found in search results"
                            f" when {message}"
                        )
                    WindowsRegistry.SearchWindow.done(0)
                self.open_search_window(perform_search)
    

    def test_05_perform_search_within_different_date_ranges(self) -> None:
        """
        Tests searching for transactions within different date ranges.
        """

        db = AppCore.instance().db

        ten_days_ago = QDate.currentDate().addDays(-10)
        ten_days_ago_transaction_name = "Transaction created Ten Days Ago"
        db.transaction_query.add_transaction(
            self.income_category.id, cast(date, ten_days_ago.toPython()), 1000,
            ten_days_ago_transaction_name
        )

        four_months_ago = QDate.currentDate().addMonths(-4)
        four_months_ago_transaction_name = "Transaction created Four Months Ago"
        db.transaction_query.add_transaction(
            self.expenses_category.id, cast(date, four_months_ago.toPython()), 500,
            four_months_ago_transaction_name
        )
        
        today = QDate.currentDate()
        eight_months_ago = QDate.currentDate().addMonths(-8)
        eight_months_ago_transaction_name = "Transaction created Eight Months Ago"
        db.transaction_query.add_transaction(
            self.income_category.id, cast(date, eight_months_ago.toPython()), 2000,
            eight_months_ago_transaction_name
        )


        #Conditions for different date ranges.
        #date_range, transaction_name, operand, search_value, expected_to_be_found, category_name, message
        params:list[tuple[str|tuple[QDate, QDate], str, str, int, bool, str, str]] = [
            (
                "month", self.test_income_transaction_name, ">=", 100, True, self.income_category.name,
                "selected current month range with value >= 100"
            ),
            (
                "month", self.test_income_transaction_name, "=", 1000, True, self.income_category.name,
                "selected current month range with value = 1000"
            ),
            (
                "year", self.test_income_transaction_name, ">=", 100, True, self.income_category.name,
                "selected year range with value >= 100"
            ),
            (
                "year", self.test_income_transaction_name, "=", 1000, True, self.income_category.name,
                "selected year range with value = 1000"
            ),
            (
                "month", "XYZ", ">=", 100, False, self.income_category.name,
                "selected current month range with value >= 100"
            ),
            (
                "month", "XYZ", "=", 1000, False, self.income_category.name,
                "selected current month range with value = 1000"
            ),
            (
                "year", "XYZ", ">=", 100, False, self.expenses_category.name,
                "selected year range with value >= 100"
            ),
            (
                "year", "XYZ", "=", 1000, False, self.expenses_category.name,
                "selected year range with value = 1000"
            ),
            (
                (ten_days_ago, today), ten_days_ago_transaction_name, "=", 1000, True, self.income_category.name,
                "selected date range covering last ten days with value = 1000"
            ),
            (
                (four_months_ago, today), four_months_ago_transaction_name, "=", 500, True, self.expenses_category.name,
                "selected date range covering last four months with value = 500"
            ),
            (
                (four_months_ago, today), ten_days_ago_transaction_name, "=", 1000, True, self.income_category.name,
                "selected date range covering last four months with value = 1000"
            ),
            (
                (eight_months_ago, today), eight_months_ago_transaction_name, "=", 2000, True, self.income_category.name,
                "selected date range covering last eight months with value = 2000"
            ),
            (
                (eight_months_ago, today), four_months_ago_transaction_name, "=", 500, True, self.expenses_category.name,
                "selected date range covering last eight months with value = 500"
            ),
            (
                (eight_months_ago, today), eight_months_ago_transaction_name, "=", 2000, True, self.income_category.name,
                "selected date range covering last eight months with value = 2000"
            ),
            (
                (four_months_ago, today), eight_months_ago_transaction_name, "=", 2000, False, self.income_category.name,
                "selected date range covering last four months with value = 2000"
            ),
            (
                (ten_days_ago, today), four_months_ago_transaction_name, "=", 500, False, self.expenses_category.name,
                "selected date range covering last ten days with value = 500"
            ),
            (
                "month", eight_months_ago_transaction_name, "=", 2000, False, self.income_category.name,
                "selected current month range with value = 2000"
            ),
        ]

        for date_range, transaction_name, operand, search_value, expected_to_be_found, category_name, message in params:
            with self.subTest(
                date_range=date_range,
                transaction_name=transaction_name,
                operand=operand,
                search_value=search_value,
                expected_to_be_found=expected_to_be_found,
                category_name=category_name,
                message=message
                ):
                def perform_search() -> None:
                    "Performs the search operation and validates the results."

                    result = self.fill_search_fields_and_perform_search(
                        search_name=transaction_name,
                        operand=operand,
                        search_value=str(search_value),
                        date_range=date_range
                    )
                    transaction_pattern = self.transaction_regex % (transaction_name, category_name)
                    if expected_to_be_found:
                        self.assertRegexpMatches(
                            result, transaction_pattern,
                            f"Transaction with name {transaction_name} not found in search results"
                            f" when {message}"
                        )
                    else:
                        self.assertNotRegexpMatches(
                            result, transaction_pattern,
                            f"Transaction with name {transaction_name} found in search results"
                            f" when {message}"
                        )
                    WindowsRegistry.SearchWindow.done(0)
                self.open_search_window(perform_search)
                        

