from __future__ import annotations
from datetime import date, timedelta
from calendar import monthrange

from PySide6.QtCore import QTimer

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from languages import LanguageStructure
from GeneralTools.Utils import shift_month
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppManagement.balance import calculate_current_balance, refresh_balance_label, DELAYED_PAYMENTS_LINK
from AppManagement.date import set_month_and_year



class TestBalance(DBTestCase, OutOfScopeTestCase):
    """Test delayed payments (future transactions) influence on the displayed balance."""

    TIMEOUT_SEC = 10


    def setUp(self) -> None:
        self.today = date.today()
        self.balance_prefix = LanguageStructure.MainWindow.get_translation(0)
        return super().setUp()


    def tearDown(self) -> None:
        set_month_and_year(self.today.month, self.today.year)
        super().tearDown()
        # Sync in-memory and stored balance with the cleaned database so other tests start from zero
        calculate_current_balance()


    def test_1_empty_future(self) -> None:
        """Without future transactions the future total is 0 and only today's balance is shown."""

        app_core = AppCore.instance()
        calculate_current_balance()
        refresh_balance_label(self.today)

        self.assertEqual(app_core.future_expenses_total, 0.0, "Future expenses total must be 0 without future transactions")
        self.assertEqual(
            WindowsRegistry.MainWindow.account_current_balance.text(),
            f"{self.balance_prefix}{app_core.today_balance}",
            "Balance label must show only today's balance without future expenses"
        )


    def test_2_income_exclusion(self) -> None:
        """Future incomes are excluded from future expenses, today's and projected balance."""

        app_core = AppCore.instance()
        app_core.db.transaction_query.add_transaction(
            self.income_category.id, self.today + timedelta(days=10), 500, "Future income"
        )
        calculate_current_balance()
        refresh_balance_label(self.today)

        self.assertEqual(app_core.future_expenses_total, 0.0, "Future income must not be counted as future expense")
        self.assertEqual(app_core.future_incomes_total, 500.0, "Future income total is wrong")
        self.assertEqual(app_core.today_balance, 0.0, "Today's balance must exclude future income")
        self.assertEqual(app_core.projected_balance, app_core.today_balance, "Projected balance must exclude future income")
        self.assertNotIn(DELAYED_PAYMENTS_LINK, WindowsRegistry.MainWindow.account_current_balance.text())


    def test_3_mixed_dates(self) -> None:
        """Only transactions dated after today are summed as future expenses."""

        app_core = AppCore.instance()
        for days_offset, value in ((-5, 100), (0, 200), (3, 300), (40, 400)):
            app_core.db.transaction_query.add_transaction(
                self.expenses_category.id, self.today + timedelta(days=days_offset), value, "Mixed date expense"
            )

        future_totals = app_core.db.statistics_query.get_future_totals(self.today)
        self.assertEqual(future_totals.incomes, 0.0, "There are no future incomes")
        self.assertEqual(future_totals.expenses, 700.0, "Only future expenses (300 + 400) must be summed")


    def test_4_projected_balance_math_and_label(self) -> None:
        """Today's balance stays unchanged, projected balance subtracts future expenses and is red when negative."""

        app_core = AppCore.instance()
        app_core.db.transaction_query.add_transaction(self.income_category.id, self.today, 100, "Today income")
        app_core.db.transaction_query.add_transaction(
            self.expenses_category.id, self.today + timedelta(days=3), 150, "Future expense"
        )
        calculate_current_balance()
        refresh_balance_label(self.today)

        self.assertEqual(app_core.today_balance, 100.0, "Today's balance must not include future expenses")
        self.assertEqual(app_core.projected_balance, -50.0, "Projected balance is wrong")

        label_text = WindowsRegistry.MainWindow.account_current_balance.text()
        self.assertTrue(label_text.startswith(f"{self.balance_prefix}100.0 ("), f"Wrong balance label {label_text}")
        self.assertIn(">-50.0</a>)", label_text, f"Projected balance missing in {label_text}")
        self.assertIn("color:red", label_text, "Negative projected balance must be red")


    def test_5_transaction_modifications(self) -> None:
        """Adding, editing and deleting transactions refreshes future totals and the label."""

        app_core = AppCore.instance()
        calculate_current_balance()
        expenses_category = app_core.categories[self.expenses_category.id]

        # Edit today's expense into the future and back (same month)
        _, last_day = monthrange(self.today.year, self.today.month)
        if self.today.day < last_day:
            for new_day, expected_future in ((last_day, 1000.0), (self.today.day, 0.0)):
                self.select_correct_tab(expenses_category)
                expenses_category.table_data.selectRow(0)

                def _edit_transaction() -> None:
                    WindowsRegistry.TransactionManagementWindow.transaction_day.setText(str(new_day))
                    self.click_on_widget(WindowsRegistry.TransactionManagementWindow.button)

                QTimer.singleShot(100, self.catch_failure(_edit_transaction))
                self.click_on_widget(expenses_category.edit_transaction)
                self.assertEqual(
                    app_core.future_expenses_total, expected_future,
                    f"Future expenses must be {expected_future} after moving transaction to day {new_day}"
                )

        # Add a future expense in the next month and delete it
        next_year, next_month = shift_month(self.today.year, self.today.month, 1)
        set_month_and_year(next_month, next_year)
        self.select_correct_tab(expenses_category)

        def _add_transaction() -> None:
            WindowsRegistry.TransactionManagementWindow.transaction_name.setText("Delayed expense")
            WindowsRegistry.TransactionManagementWindow.transaction_day.setText("1")
            WindowsRegistry.TransactionManagementWindow.transaction_value.setText("250")
            self.click_on_widget(WindowsRegistry.TransactionManagementWindow.button)

        QTimer.singleShot(100, self.catch_failure(_add_transaction))
        self.click_on_widget(expenses_category.add_transaction)

        self.assertEqual(app_core.future_expenses_total, 250.0, "Added future expense isn't counted")
        self.assertIn(DELAYED_PAYMENTS_LINK, WindowsRegistry.MainWindow.account_current_balance.text())
        self.assertIn(f"{app_core.today_balance} (", WindowsRegistry.MainWindow.account_current_balance.text())

        expenses_category.table_data.selectRow(0)
        QTimer.singleShot(100, self.catch_failure(
            lambda: self.click_on_widget(WindowsRegistry.Messages.delete_transaction_confirmation.ok_button)
        ))
        self.click_on_widget(expenses_category.delete_transaction)

        self.assertEqual(app_core.future_expenses_total, 0.0, "Deleted future expense is still counted")
        self.assertNotIn(DELAYED_PAYMENTS_LINK, WindowsRegistry.MainWindow.account_current_balance.text())
        qsleep(300)


    def test_6_settings_totals_exclude_future(self) -> None:
        """Settings totals represent the past and don't change when future transactions are added."""

        app_core = AppCore.instance()
        calculate_current_balance()
        income_text = WindowsRegistry.SettingsWindow.total_income.text()
        expense_text = WindowsRegistry.SettingsWindow.total_expense.text()

        app_core.db.transaction_query.add_transaction(
            self.income_category.id, self.today + timedelta(days=5), 300, "Future income"
        )
        app_core.db.transaction_query.add_transaction(
            self.expenses_category.id, self.today + timedelta(days=5), 400, "Future expense"
        )
        calculate_current_balance()
        refresh_balance_label(self.today)

        self.assertEqual(WindowsRegistry.SettingsWindow.total_income.text(), income_text, "Total income includes future income")
        self.assertEqual(WindowsRegistry.SettingsWindow.total_expense.text(), expense_text, "Total expense includes future expense")
        self.assertEqual(
            WindowsRegistry.SettingsWindow.total_income.text(),
            f"{LanguageStructure.Statistics.get_translation(4)}1000.0"
        )


    def test_7_delayed_payments_window(self) -> None:
        """Clicking the projected balance shows the list of future expenses."""

        app_core = AppCore.instance()
        app_core.db.transaction_query.add_transaction(
            self.expenses_category.id, self.today + timedelta(days=2), 120, "First delayed"
        )
        app_core.db.transaction_query.add_transaction(
            self.expenses_category.id, self.today + timedelta(days=35), 80, "Second delayed"
        )
        app_core.db.transaction_query.add_transaction(
            self.income_category.id, self.today + timedelta(days=3), 999, "Future income"
        )
        calculate_current_balance()

        def _check_window() -> None:
            window = WindowsRegistry.DelayedPaymentsWindow
            self.assertTrue(window.isVisible(), "Delayed payments window hasn't been shown")
            self.assertEqual(window.transactions_table.rowCount(), 2, "Only future expenses must be listed")
            self.assertTrue(window.total_label.text().endswith("200.0"), "Wrong delayed expenses total")
            window.done(1)

        QTimer.singleShot(200, self.catch_failure(_check_window))
        WindowsRegistry.MainWindow.account_current_balance.linkActivated.emit(DELAYED_PAYMENTS_LINK)
        qsleep(300)
