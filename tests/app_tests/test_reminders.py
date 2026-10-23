from __future__ import annotations
from datetime import date
from functools import partial

from PySide6.QtCore import QTimer, Qt

from tests.tests_toolkit import DBTestCase, OutOfScopeTestCase, qsleep
from languages import LanguageStructure
from project_configuration import CategoryType
from backend.models import MonthlyReminder
from GeneralTools.Utils import shift_month
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.app_exceptions import ReminderValidationError
from AppManagement.account import load_account_data
from AppManagement.balance import calculate_current_balance
from AppManagement.date import set_month_and_year
from AppManagement.reminders_logic import create_reminder, check_pending_reminders, ignore_reminders,\
    show_pending_reminders, clear_pending_reminder_rows

REMINDERS_LOGGER = "AppManagement.reminders_logic"
SECOND_ACCOUNT_NAME = "Reminders second account"



class TestReminders(DBTestCase, OutOfScopeTestCase):
    """Test monthly payment reminders."""

    TIMEOUT_SEC = 15


    def setUp(self) -> None:
        self.today = date.today()
        self.previous_year, self.previous_month = shift_month(self.today.year, self.today.month, -1)
        # Reminders created on this date cover the previous month, so they are due today and not paid
        self.previous_month_start = date(self.previous_year, self.previous_month, 1)
        self.reminder_query = AppCore.instance().db.reminder_query
        self.submit_transaction_window = partial(self.click_on_widget, WindowsRegistry.TransactionManagementWindow.button)
        return super().setUp()


    def tearDown(self) -> None:
        clear_pending_reminder_rows()
        set_month_and_year(self.today.month, self.today.year)
        super().tearDown()
        # Sync in-memory and stored balance with the cleaned database so other tests start from zero
        calculate_current_balance()


    def test_01_due_date_day_specified(self) -> None:
        """Reminder with a day is due on that day of the current month."""

        reminder = create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))
        self.assertEqual(reminder.next_due_date, date(2026, 10, 20))


    def test_02_due_date_day_null(self) -> None:
        """Reminder without a day is due on the 1st day of the next month."""

        reminder = create_reminder("Internet", self.expenses_category.id, None, None, date(2026, 10, 15))
        self.assertEqual(reminder.next_due_date, date(2026, 11, 1))


    def test_03_month_rollover(self) -> None:
        """Due date rolls over from December to January of the next year."""

        app_core = AppCore.instance()
        reminder = create_reminder("Rent", self.expenses_category.id, 500, 15, date(2026, 12, 1))
        self.assertEqual(reminder.next_due_date, date(2026, 12, 15))
        self.assertEqual(app_core.db.reminder_query.update_next_due_date(reminder.id), date(2027, 1, 15))


    def test_04_short_month_clamp(self) -> None:
        """Day 31 is clamped in short months and restored afterwards."""

        app_core = AppCore.instance()
        reminder = create_reminder("Rent", self.expenses_category.id, None, 31, date(2027, 1, 10))
        self.assertEqual(reminder.next_due_date, date(2027, 1, 31))
        self.assertEqual(app_core.db.reminder_query.update_next_due_date(reminder.id), date(2027, 2, 28))
        self.assertEqual(app_core.db.reminder_query.update_next_due_date(reminder.id), date(2027, 3, 31))

        leap_reminder = create_reminder("Leap rent", self.expenses_category.id, None, 31, date(2028, 2, 1))
        self.assertEqual(leap_reminder.next_due_date, date(2028, 2, 29))


    def test_05_not_due_yet(self) -> None:
        """Reminder isn't pending before its due date."""

        create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))
        self.assertEqual(check_pending_reminders(date(2026, 10, 19)), [])


    def test_06_due_and_missing(self) -> None:
        """Due reminder without a matching transaction is pending."""

        reminder = create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))
        pending = check_pending_reminders(date(2026, 10, 20))
        self.assertEqual([pending_reminder.id for pending_reminder in pending], [reminder.id])


    def test_07_due_but_paid_case_insensitive(self) -> None:
        """Matching transaction with a different letter case resolves the reminder silently."""

        app_core = AppCore.instance()
        reminder = create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))
        app_core.db.transaction_query.add_transaction(self.expenses_category.id, date(2026, 10, 5), 500, "rent")

        unicode_reminder = create_reminder("Оренда", self.expenses_category.id, None, 20, date(2026, 10, 15))
        app_core.db.transaction_query.add_transaction(self.expenses_category.id, date(2026, 10, 6), 500, " оренда ")

        self.assertEqual(check_pending_reminders(date(2026, 10, 25)), [])
        self.assertEqual(self.reminder_query.get_reminder(reminder.id).next_due_date, date(2026, 11, 20))
        self.assertEqual(self.reminder_query.get_reminder(unicode_reminder.id).next_due_date, date(2026, 11, 20))


    def test_08_category_matching(self) -> None:
        """Same-name transaction in another category doesn't match the reminder."""

        app_core = AppCore.instance()
        reminder = create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))
        app_core.db.transaction_query.add_transaction(self.income_category.id, date(2026, 10, 5), 500, "Rent")

        pending = check_pending_reminders(date(2026, 10, 25))
        self.assertEqual([pending_reminder.id for pending_reminder in pending], [reminder.id])


    def test_09_covered_month_day_null(self) -> None:
        """Reminder without a day is resolved by a transaction in the previous month only."""

        app_core = AppCore.instance()
        reminder = create_reminder("Internet", self.expenses_category.id, None, None, date(2026, 10, 15))
        app_core.db.transaction_query.add_transaction(self.expenses_category.id, date(2026, 11, 5), 200, "Internet")
        self.assertEqual(len(check_pending_reminders(date(2026, 11, 10))), 1, "November transaction mustn't resolve October")

        app_core.db.transaction_query.add_transaction(self.expenses_category.id, date(2026, 10, 3), 200, "Internet")
        self.assertEqual(check_pending_reminders(date(2026, 11, 10)), [])
        self.assertEqual(self.reminder_query.get_reminder(reminder.id).next_due_date, date(2026, 12, 1))


    def test_10_ignore_action(self) -> None:
        """Ignoring a reminder moves it to the next month and logs the skip."""

        reminder = create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))

        with self.assertLogs(REMINDERS_LOGGER, level="INFO") as logs:
            ignore_reminders([reminder.id])

        self.assertEqual(self.reminder_query.get_reminder(reminder.id).next_due_date, date(2026, 11, 20))
        self.assertTrue(
            any('[ENTITY: REMINDER] [ACTION: IGNORED] name="Rent" skipped_for_month=10-2026' in line for line in logs.output),
            f"IGNORED log not found in {logs.output}"
        )


    def test_11_pay_action(self) -> None:
        """Paying switches to the covered month, adds a matching transaction and resolves the reminder."""

        app_core = AppCore.instance()
        reminder = create_reminder("Gym", self.expenses_category.id, 300, 5, self.previous_month_start)
        window = WindowsRegistry.PendingRemindersWindow

        def _check_pending_window() -> None:
            self.assertTrue(window.isVisible(), "Pending reminders window hasn't been shown")
            self.assertEqual(set(window.reminder_rows), {reminder.id})
            self.assertIn(
                f"<b>{LanguageStructure.Months.get_translation(self.previous_month)}</b>",
                window.description.text(),
                "Expired month isn't shown in bold"
            )

            def _check_transaction_window() -> None:
                transaction_window = WindowsRegistry.TransactionManagementWindow
                self.assertEqual(transaction_window.transaction_name.text(), "Gym")
                self.assertEqual(transaction_window.transaction_day.text(), "5")
                self.assertEqual(transaction_window.transaction_value.text(), "300.0")
                self.assertEqual(transaction_window.windowTitle(), self.expenses_category.name)
                self.assertEqual((app_core.current_year, app_core.current_month), (self.previous_year, self.previous_month))
                self.submit_transaction_window()

            QTimer.singleShot(200, self.catch_failure(_check_transaction_window))
            self.click_on_widget(window.reminder_rows[reminder.id].pay_button)

        QTimer.singleShot(200, self.catch_failure(_check_pending_window))
        show_pending_reminders(self.today)

        self.assertFalse(window.isVisible(), "Window must close automatically when no rows remain")
        self.assertEqual(
            self.reminder_query.get_reminder(reminder.id).next_due_date, date(self.today.year, self.today.month, 5)
        )
        self.assertTrue(
            app_core.db.reminder_query.matching_transaction_exists(
                "Gym", self.expenses_category.id,
                date(self.previous_year, self.previous_month, 1), date(self.previous_year, self.previous_month, 28)
            ),
            "Paid transaction hasn't been added to the covered month"
        )


    def test_12_mixed_skip_and_pay(self) -> None:
        """Ticking ignore on some rows and paying others doesn't close the window or apply marks early."""

        alpha = create_reminder("Alpha rent", self.expenses_category.id, 300, 5, self.previous_month_start)
        beta = create_reminder("Beta gym", self.expenses_category.id, 300, 5, self.previous_month_start)
        gamma = create_reminder("Gamma internet", self.expenses_category.id, 300, 5, self.previous_month_start)
        alpha_due_date = alpha.next_due_date
        window = WindowsRegistry.PendingRemindersWindow
        rows = window.reminder_rows

        def _mix_skip_and_pay() -> None:
            self.click_on_widget(rows[alpha.id].ignore_checkbox)

            QTimer.singleShot(200, self.catch_failure(self.submit_transaction_window))
            self.click_on_widget(rows[beta.id].pay_button)

            self.assertTrue(window.isVisible(), "Paying a reminder mustn't close the window")
            self.assertNotIn(beta.id, rows)
            self.assertTrue(rows[alpha.id].ignore_checkbox.isChecked(), "Ignore mark has been reset")
            self.assertEqual(
                self.reminder_query.get_reminder(alpha.id).next_due_date, alpha_due_date,
                "Ignore mark applied before confirmation"
            )
            self.assertTrue(rows[gamma.id].pay_button.isEnabled(), "Other reminders must stay payable")

            QTimer.singleShot(200, self.catch_failure(self.submit_transaction_window))
            self.click_on_widget(rows[alpha.id].pay_button)
            self.assertNotIn(alpha.id, rows)
            self.assertTrue(window.isVisible())

            self.click_on_widget(rows[gamma.id].ignore_checkbox)
            self.click_on_widget(window.confirm_button)

        QTimer.singleShot(200, self.catch_failure(_mix_skip_and_pay))
        with self.assertLogs(REMINDERS_LOGGER, level="INFO") as logs:
            show_pending_reminders(self.today)

        self.assertFalse(window.isVisible())
        ignored_logs = [line for line in logs.output if "[ACTION: IGNORED]" in line]
        resolved_logs = [line for line in logs.output if "[ACTION: RESOLVED]" in line]
        self.assertEqual(len(ignored_logs), 1, f"Only Gamma must be ignored: {ignored_logs}")
        self.assertIn('name="Gamma internet"', ignored_logs[0])
        self.assertTrue(any('name="Alpha rent"' in line for line in resolved_logs), "Alpha wasn't resolved")
        self.assertTrue(any('name="Beta gym"' in line for line in resolved_logs), "Beta wasn't resolved")
        for reminder in (alpha, beta, gamma):
            self.assertEqual(
                self.reminder_query.get_reminder(reminder.id).next_due_date, date(self.today.year, self.today.month, 5)
            )


    def test_13_auto_close_rules(self) -> None:
        """Window stays open while ticked rows remain, closes after the last row is paid and skips nothing without confirmation."""

        alpha = create_reminder("Alpha rent", self.expenses_category.id, 300, 5, self.previous_month_start)
        beta = create_reminder("Beta gym", self.expenses_category.id, 300, 5, self.previous_month_start)
        alpha_due_date = alpha.next_due_date
        window = WindowsRegistry.PendingRemindersWindow
        rows = window.reminder_rows

        def _pay_unticked_and_close() -> None:
            self.click_on_widget(rows[alpha.id].ignore_checkbox)
            QTimer.singleShot(200, self.catch_failure(self.submit_transaction_window))
            self.click_on_widget(rows[beta.id].pay_button)

            self.assertTrue(window.isVisible(), "Window must stay open while a ticked row remains")
            self.click_on_widget(window.close_window)

        QTimer.singleShot(200, self.catch_failure(_pay_unticked_and_close))
        show_pending_reminders(self.today)
        self.assertEqual(
            self.reminder_query.get_reminder(alpha.id).next_due_date, alpha_due_date,
            "Closing without confirmation mustn't skip"
        )

        def _pay_last_row() -> None:
            self.assertEqual(set(rows), {alpha.id})
            self.assertFalse(rows[alpha.id].ignore_checkbox.isChecked(), "Ignore marks must be discarded after closing")
            QTimer.singleShot(200, self.catch_failure(self.submit_transaction_window))
            self.click_on_widget(rows[alpha.id].pay_button)
            self.assertFalse(window.isVisible(), "Window must close after the last row is paid")

        # Paid Beta is due again on the 5th of the current month, so check before that day
        QTimer.singleShot(200, self.catch_failure(_pay_last_row))
        show_pending_reminders(date(self.today.year, self.today.month, 1))
        qsleep(200)


    def test_14_cascade_deletion(self) -> None:
        """Deleting a category or an account removes its reminders."""

        app_core = AppCore.instance()
        create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))
        create_reminder("Salary", self.income_category.id, 500, 20, date(2026, 10, 15))

        app_core.db.category_query.delete_category(self.expenses_category.id)
        self.assertEqual([reminder.name for reminder in app_core.db.reminder_query.get_all_reminders()], ["Salary"])

        app_core.db.create_account(SECOND_ACCOUNT_NAME, 0)
        app_core.db.category_query.create_category("Bills", CategoryType.Expense, 0)
        bills = app_core.db.category_query.get_category("Bills", CategoryType.Expense)
        create_reminder("Electricity", bills.id, None, 10, date(2026, 10, 15))
        app_core.db.account_query.delete_account()
        app_core.db.set_account_id("Test user")

        with app_core.db.session_factory() as session:
            remaining_names = [reminder.name for reminder in session.query(MonthlyReminder).all()]
        self.assertEqual(remaining_names, ["Salary"], "Reminders of the deleted account haven't been removed")


    def test_15_name_uniqueness(self) -> None:
        """Names are unique per account, case-insensitively."""

        app_core = AppCore.instance()
        create_reminder("Rent", self.expenses_category.id, 500, 20, date(2026, 10, 15))

        with self.assertRaises(ReminderValidationError) as error:
            create_reminder(" rENT ", self.income_category.id, None, None, date(2026, 10, 15))
        self.assertEqual(error.exception.reason, ReminderValidationError.NAME_EXISTS)

        app_core.db.create_account(SECOND_ACCOUNT_NAME, 0)
        app_core.db.category_query.create_category("Bills", CategoryType.Expense, 0)
        bills = app_core.db.category_query.get_category("Bills", CategoryType.Expense)
        create_reminder("Rent", bills.id, 500, 20, date(2026, 10, 15))
        app_core.db.set_account_id("Test user")


    def test_16_day_range_validation(self) -> None:
        """Day outside 1-31 is rejected."""

        for day in (0, 32):
            with self.subTest(day=day):
                with self.assertRaises(ReminderValidationError) as error:
                    create_reminder("Rent", self.expenses_category.id, None, day, date(2026, 10, 15))
                self.assertEqual(error.exception.reason, ReminderValidationError.DAY_OUT_OF_RANGE)


    def test_17_category_required(self) -> None:
        """Reminder without a category is rejected."""

        with self.assertRaises(ReminderValidationError) as error:
            create_reminder("Rent", None, None, 5, date(2026, 10, 15))
        self.assertEqual(error.exception.reason, ReminderValidationError.NO_CATEGORY)


    def test_18_account_switch(self) -> None:
        """After switching accounts only reminders of the new account are checked and shown."""

        app_core = AppCore.instance()
        create_reminder("Own rent", self.expenses_category.id, None, 5, date(2100, 1, 1))

        app_core.db.create_account(SECOND_ACCOUNT_NAME, 0)
        app_core.db.category_query.create_category("Bills", CategoryType.Expense, 0)
        bills = app_core.db.category_query.get_category("Bills", CategoryType.Expense)
        second_reminder = create_reminder("Second account rent", bills.id, None, 1, date(2020, 1, 1))
        app_core.db.set_account_id("Test user")
        self.assertEqual(check_pending_reminders(self.today), [], "Reminders of another account must not be checked")

        window = WindowsRegistry.PendingRemindersWindow
        shown_reminders:list[set[int]] = []

        def _check_window() -> None:
            self.assertTrue(window.isVisible(), "Pending reminders window hasn't been shown after account switch")
            shown_reminders.append(set(window.reminder_rows))
            window.done(1)

        QTimer.singleShot(500, self.catch_failure(_check_window))
        load_account_data(SECOND_ACCOUNT_NAME)
        qsleep(1000)
        self.assertEqual(shown_reminders, [{second_reminder.id}])

        load_account_data("Test user")
        qsleep(300)


    def test_19_management_category_selection(self) -> None:
        """Categories are grouped by type and the category is taken from the selection in the visible tab."""

        window = WindowsRegistry.RemindersManagementWindow

        def _check_management_window() -> None:
            self.assertEqual(
                [window.income_categories.item(row).text() for row in range(window.income_categories.count())],
                [self.income_category.name]
            )
            self.assertEqual(
                [window.expense_categories.item(row).text() for row in range(window.expense_categories.count())],
                [self.expenses_category.name]
            )

            # Nothing is selected after opening, so a category is required
            window.reminder_name.setText("Phone")
            QTimer.singleShot(100, self.catch_failure(
                lambda: self.click_on_widget(WindowsRegistry.Messages.reminder_no_category.ok_button)
            ))
            self.click_on_widget(window.add_reminder)
            self.assertEqual(self.reminder_query.get_all_reminders(), [], "Reminder created without a category")

            window.category_tabs.setCurrentIndex(1)
            window.expense_categories.setCurrentRow(0)
            window.reminder_day.setText("10")
            self.click_on_widget(window.add_reminder)
            reminders = self.reminder_query.get_all_reminders()
            self.assertEqual([(reminder.name, reminder.category_id) for reminder in reminders], [("Phone", self.expenses_category.id)])

            window.category_tabs.setCurrentIndex(0)
            window.reminders_table.selectRow(0)
            self.assertEqual(window.category_tabs.currentIndex(), 1, "Expense tab isn't shown for the selected reminder")
            self.assertEqual(
                [item.data(Qt.ItemDataRole.UserRole) for item in window.expense_categories.selectedItems()],
                [self.expenses_category.id]
            )
            window.done(1)

        def _open_management_window() -> None:
            QTimer.singleShot(200, self.catch_failure(_check_management_window))
            self.click_on_widget(WindowsRegistry.SettingsWindow.monthly_reminders)
            WindowsRegistry.SettingsWindow.done(1)

        QTimer.singleShot(200, self.catch_failure(_open_management_window))
        self.click_on_widget(WindowsRegistry.MainWindow.settings)
        qsleep(300)
