from __future__ import annotations
from typing import Callable
from PySide6.QtCore import QTimer
from tests.tests_toolkit import DBTestCase
from AppObjects.windows_registry import WindowsRegistry



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


    def test_01_search_transactions_with_value_above_one(self) -> None:
        """
        Tests searching for transactions with a value above '1'. Which should result in all transactions being found.
        """

        def perform_search() -> None:
            "Performs the search operation and validates the results."

            WindowsRegistry.SearchWindow.search_value.setText("1")
            WindowsRegistry.SearchWindow.value_operands.setCurrentText(">")
            self.click_on_widget(WindowsRegistry.SearchWindow.date_selection.select_month_range_button)
            self.click_on_widget(WindowsRegistry.SearchWindow.search)
            result = self.get_search_result()

            income_transaction_pattern = self.transaction_regex % (self.test_income_transaction_name, self.income_category.name)
            self.assertRegexpMatches(
                result, income_transaction_pattern,
                f"Income transaction with name {self.test_income_transaction_name} not found in search results"
                f" when attempting to search for transactions with value above 1")
            expenses_transaction_pattern = self.transaction_regex % (self.test_expenses_transaction_name, self.expenses_category.name)
            self.assertRegexpMatches(
                result, expenses_transaction_pattern,
                f"Expenses transaction with name {self.test_expenses_transaction_name} not found in search results"
                f" when attempting to search for transactions with value above 1")
            WindowsRegistry.SearchWindow.done(0)
            
        self.open_search_window(perform_search)

