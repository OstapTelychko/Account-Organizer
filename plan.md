# Implementation Plan: Delayed Payments & Monthly Reminders

This document outlines the architectural changes, database schema updates, GUI modifications, and the pragmatic TDD workflow required to implement Scheduled Delayed Payments and Monthly Reminders in the `Account-Organizer` repository.

## 1. Feature: Scheduler of Delayed Payments

### Concept
Allow users to create transactions with future dates (`date > today`). The main window shows two values:
*   **Today's balance** = start balance + incomes dated today or earlier − expenses dated today or earlier.
*   **Projected balance** = today's balance − future expenses. Future incomes are strictly excluded to prevent false positive balances.

**Display format:** The label always shows today's balance. Only when delayed (future) expenses exist is the projected balance appended in parentheses:
*   No future expenses: `Balance: <today's balance>`, e.g. `Balance: 100.0`.
*   Future expenses exist: `Balance: <today's balance> (<projected balance>)`, e.g. `Balance: 100.0 (-50.0)`.
*   If `projected_balance < 0`, the projected part is rendered red.
*   The projected part is clickable and opens a window explaining the difference (list of future expenses).

### 1.1. Database & Backend Changes
**No schema changes are required.** The `transactions` table already uses a unified `date` column with a database index (`ix_transactions_date`).
*   **Stored account totals keep their current meaning.** `accounts.current_balance`, `current_total_income` and `current_total_expenses` continue to include all transactions (past and future), so the existing incremental update logic in `AppManagement/transaction.py` stays intact. Today's balance, projected balance and the displayed (past-only) totals are derived from them.
*   **`backend/statistics_query.py`**:
    *   Add `get_future_totals(current_date: date) -> tuple[float, float]` returning `(future_incomes_sum, future_expenses_sum)` for the current account (`self.account_id`).
    *   *Query logic:* `SELECT COALESCE(SUM(transactions.value), 0) FROM transactions JOIN categories ON transactions.category_id = categories.id WHERE transactions.date > :current_date AND categories.category_type = :type AND categories.account_id = :account_id` (once per category type, or a single grouped query).
    *   Add `get_future_expense_transactions(current_date: date)` returning future expense transactions with their category name, ordered by date (used by the details window).
*   **Logging Requirement (Point-In-Time Recovery):** Structured logs via the existing `logger.py` when this state is calculated, e.g. `logger.debug('[ENTITY: DELAYED_PAYMENT] [ACTION: CALCULATED] future_expenses=150.5 future_incomes=0.0')`.
*   **`AppObjects/app_core.py`**: Initialize in `__init__`: `today_balance: float = 0.0`, `projected_balance: float = 0.0`, `future_expenses_total: float = 0.0`, `future_incomes_total: float = 0.0`.

### 1.2. App Management Logic (`AppManagement/balance.py`)
*   Add pure, GUI-independent helpers (directly testable):
    *   `calculate_today_and_projected_balance(ledger_balance, future_incomes, future_expenses) -> tuple[float, float]`:
        *   `today_balance = round(ledger_balance - future_incomes + future_expenses, 2)`
        *   `projected_balance = round(today_balance - future_expenses, 2)`
    *   `format_balance_text(today_balance, projected_balance, has_future_expenses) -> str`: returns `"100.0 (-50.0)"` or `"100.0"` when there are no future expenses.
    *   `is_projected_balance_negative(projected_balance) -> bool`.
*   Add `refresh_balance_label()` as the single place that queries future totals, updates the `AppCore` fields, sets the label text (with the `LanguageStructure.MainWindow.get_translation(0)` prefix), the red styling and the clickable state.
*   Call `refresh_balance_label()` everywhere `account_current_balance` text is currently set:
    *   `calculate_current_balance()` (also used after category deletion).
    *   `load_account_balance()` (startup, account switch, backup restore).
    *   `update_account_balance()` — used by transaction add / edit / delete in `AppManagement/transaction.py`. **Future totals must be recomputed after every transaction modification**, including edits that move a transaction between past and future.
    *   `AppManagement/language.py`: `change_language_for_startup()` and `change_language()`.
*   Add `show_delayed_payments()` that fills and opens `DelayedPaymentsWindow`.
*   Settings window `total_income` / `total_expense` represent the past only and must not change when future transactions are added: display `current_total_income - future_incomes_total` and `current_total_expenses - future_expenses_total`. They are refreshed in the same places as the balance label.

### 1.3. GUI Updates
*   **`GUI/windows/main_window.py`**:
    *   Keep `account_current_balance` as a `QLabel`, switch it to rich text. The projected part is a link (`linkActivated` signal) that opens `DelayedPaymentsWindow`. The projected part is red when `projected_balance < 0`, otherwise uses the default theme color.
    *   When there are no future expenses, the label shows only today's balance and has no link.
*   **`GUI/windows/delayed_payments.py`** (New File): `DelayedPaymentsWindow(SubWindow)` with a `CustomTableWidget` (columns: `Date | Category | Name | Value`) and a total of future expenses.
*   Register `DelayedPaymentsWindow` in `AppObjects/windows_registry.py`; connect `linkActivated` in `main.py` `post_show_setup()`.
*   **Translations:** new keys in `languages.json` for **English, Українська and Polski**, accessors in `languages.py`, window texts updated in `change_language()`.

### 1.4. Statistics
Future-dated transactions **are included** in statistics. Monthly / quarterly / yearly statistics use the full date range of the selected period (e.g. the whole month even on its first day). No code change required; covered by a test.

---

## 2. Feature: Monthly Payments Reminders

### Concept
A system to track recurring monthly payments, scoped to the current account. If a payment is not recorded by its due date, a popup appears (on startup and after account switch) listing missing transactions. Users can pay them directly from the popup or mark them to be ignored for the current month via checkboxes, requiring final confirmation.

### 2.1. Database Schema Changes (Alembic)
Create a new migration via Alembic (e.g., `alembic revision -m "add_monthly_reminders_table"`).
**New Table: `monthly_reminders`**
*   `id`: Integer, Primary Key, Autoincrement
*   `name`: String, Not Null (Validator: Min 3 chars)
*   `category_id`: Integer, ForeignKey(`categories.id`, `ondelete="CASCADE"`), Not Null, Indexed (Mandatory; the reminder's account is the category's account)
*   `value`: Float, Nullable (Optional amount)
*   `day`: SmallInteger, Nullable (1-31, Optional day)
*   `next_due_date`: Date, Not Null
*   Names are unique per account, case-insensitively. Enforced in `ReminderQuery` (join with `categories` on `account_id`, compare with `casefold()`), since a DB constraint cannot span the categories join.

**Due date rules:**
*   If `day` is specified, `next_due_date` is that day of the current month, **clamped to the last day of the month** (e.g. `day=31` in February → Feb 28/29).
*   If `day` is NULL, `next_due_date` is the **1st day of the NEXT month** (post-factum reminder for the previous month).
*   Advancing by one month always re-derives the day from the stored `day` (not from the previous clamped date): `day=31` → Jan 31 → Feb 28 → Mar 31.
*   **Covered month** (period searched for a matching transaction): the month of `next_due_date` if `day` is set; the month before `next_due_date` if `day` is NULL.

### 2.2. Foreign Keys Enforcement
*   Enable `PRAGMA foreign_keys=ON` in `set_sqlite_pragma()` in `backend/db_controller.py`.
*   `alembic/env.py` creates its own engine, so migrations (which use `batch_alter_table` and recreate tables) run **without** FK enforcement. This must stay so for future migrations.
*   Existing FKs (`categories.account_id`, `transactions.category_id`) have no `ON DELETE` clause; existing ORM cascades already delete children before parents, so current behavior is unchanged.
*   On startup run `PRAGMA foreign_key_check` once and log any orphan rows found in existing databases (warning only).
*   `backend/models.py`: add a `Category.reminders` relationship with `cascade="all, delete-orphan", passive_deletes=True`. Deleting a category removes its reminders; deleting an account removes its categories and therefore their reminders.

### 2.3. Backend Queries & Human-Readable Logging
*   **`backend/models.py`**: Add the `MonthlyReminder` model.
*   **`backend/reminder_query.py`** (New File): `ReminderQuery(session_factory)` with an `account_id` attribute, following the same pattern as the other query classes.
    *   Instantiate as `self.reminder_query` in `DBController.__init__()` and set its `account_id` in `DBController.set_account_id()`.
    *   All reads filter by the current account through `categories.account_id`.
    *   CRUD: `create_reminder`, `update_reminder`, `delete_reminder`, `get_all_reminders`, `get_reminder`, `reminder_name_exists(name)` (case-insensitive).
    *   `update_next_due_date(reminder_id)`: shifts the date forward by 1 month using the due date rules above.
    *   `matching_transaction_exists(name, category_id, period_start, period_end) -> bool`: see matching rules.
*   **Logging Requirement (Point-In-Time Recovery):** All write and update operations MUST output structured, human-readable logs using `logger.info`.
    *   *Creation:* `logger.info('[ENTITY: REMINDER] [ACTION: CREATED] name="Rent" category_id=2 value=500 day=10')`
    *   *Update / Delete:* `[ACTION: UPDATED]`, `[ACTION: DELETED]` with changed fields.
    *   *Auto-resolve:* `logger.info('[ENTITY: REMINDER] [ACTION: RESOLVED] name="Rent" month=10-2026 next_due_date=2026-11-10')`
    *   *Skip:* `logger.info('[ENTITY: REMINDER] [ACTION: IGNORED] name="Rent" skipped_for_month=10-2026')`

### 2.4. Matching Rules
*   Only the covered month of `next_due_date` is checked (no historical scans).
*   A transaction matches when all of these hold:
    *   It belongs to the current account.
    *   Its date is within the covered month.
    *   Its name equals the reminder name **case-insensitively** (`casefold()` + `strip()` in Python; SQLite `lower()` is ASCII-only).
    *   Its `category_id` equals the reminder's `category_id`.
*   Value is not compared.
*   **Name Changes:** Changing a reminder's name only affects future checks (from `next_due_date` forward). Past data is untouched.

### 2.5. App Management & Startup Flow
*   **`AppManagement/reminders_logic.py`** (New File):
    *   Pure helpers: `get_initial_due_date(day, current_date)`, `get_next_due_date(current_due_date, day)`, `get_covered_period(next_due_date, day)`.
    *   `check_pending_reminders(current_date: date | None = None) -> list[MonthlyReminder]` (defaults to `date.today()`): for each reminder, while `current_date >= next_due_date`: if a matching transaction exists, silently call `update_next_due_date` (logged as RESOLVED) and continue; otherwise add it to the pending list and stop.
    *   `show_pending_reminders()`: fills and opens `PendingRemindersWindow` when the pending list is not empty.
    *   `ignore_reminders(reminder_ids)`, `pay_reminder(reminder_id)`.
*   **Trigger points:**
    *   `main.py` `post_show_setup()` after account and balance loading.
    *   After account switch (`AppManagement/account.py`, after `load_account_balance()`).
    *   After backup restore (`AppManagement/backup_management.py`).

### 2.6. GUI Updates
*   **`PendingRemindersWindow`** (`GUI/windows/reminders.py`, inherits `SubWindow`):
    *   Displays all unpaid reminders using `CustomListWidget`.
    *   Each row: `Reminder Name | Category | Expected Value (if any) | [Pay] | [ ] Ignore this month`.
    *   **Pay workflow:** Clicking `Pay` (or double-clicking a row) switches the main window to the covered month via `set_month_and_year()` (see 2.7; required because `TransactionManagementWindow` builds the date from the viewed month + day), then opens `TransactionManagementWindow` pre-filled with the reminder `name`, category, `value` (if any) and `day` (if any).
    *   After the transaction is saved, only that reminder is re-checked → resolved, `next_due_date` moves to the next month, and its row is removed. The list is not rebuilt, so other rows keep their state.
    *   A single **"Confirm & Close"** button at the bottom: increments `next_due_date` ONLY for rows with "Ignore this month" ticked, logs the IGNORED event, and leaves unchecked rows to reappear on the next check.
    *   **Mixing skip and pay must be safe:**
        *   Ticking "Ignore this month" only marks the row; nothing is written until "Confirm & Close". Ticked rows can still be paid (paying removes the row and drops its ignore mark).
        *   Paying a row never closes the window, never applies ignore marks of other rows, and never resets their checkbox state.
        *   After `TransactionManagementWindow` closes (saved or cancelled), the user returns to `PendingRemindersWindow` with all remaining rows and checkbox states intact.
        *   The window closes automatically only when no rows remain at all. If only ticked rows remain, it stays open until the user confirms.
        *   Closing the window without "Confirm & Close" discards ignore marks (nothing is skipped).
*   **`RemindersManagementWindow`** (`GUI/windows/reminders.py`):
    *   Create, edit, delete reminders of the current account.
    *   Fields: name (min 3 chars), category (mandatory), value (optional), day (optional, 1–31).
    *   Validation errors use the existing message window.
*   **Settings window, General section** (`GUI/windows/settings.py`):
    *   Put `switch_themes_button` and `languages` in one horizontal row (`QHBoxLayout`).
    *   Below it, vertically: `shortcuts_management` and the new `monthly_reminders` button opening `RemindersManagementWindow`.
*   Register `PendingRemindersWindow` and `RemindersManagementWindow` in `AppObjects/windows_registry.py`; connect signals in `main.py` `post_show_setup()`.
*   **Translations:** new keys in `languages.json` for **English, Українська and Polski**, accessors in `languages.py`, texts updated in `change_language()`.

### 2.7. Month / Year Change Notification (`AppManagement/date.py`)
*   Every change of the viewed month or year shows an information message via `show_information_message()` (`AppManagement/information_message.py`):
    *   Month change: `Month updated to {month name}` (month name from `LanguageStructure.Months`).
    *   Year change: `Year updated to {year}`.
    *   Both changed at once: both lines in one message.
*   Applies to `next_month()`, `previous_month()`, `next_year()`, `previous_year()`.
*   Add `set_month_and_year(month, year)` used by the Pay workflow: sets `app_core.current_month` / `current_year`, updates the main window labels, calls `load_categories_data()` and shows the message only for the parts that actually changed.
*   **Translations:** both message templates in `languages.json` for English, Українська and Polski.

---

## 3. Development & Testing Workflow (Pragmatic TDD)
Because existing tests directly import from the product code (e.g., `tests/app_tests/test_statistics.py`), the agent MUST follow this exact order to avoid `ImportError` exceptions:
1.  **Scaffolding:** Create the DB models (`backend/models.py`), Alembic migrations, necessary UI file structures in `GUI/windows/`, and basic function signatures in `backend/` and `AppManagement/`.
2.  **Test Implementation:** Write the tests described below in `tests/app_tests/`.
3.  **Refinement:** Implement and polish the core logic until all tests pass.

**Test infrastructure:**
*   Tests inherit `DBTestCase` from `tests/tests_toolkit.py` and create transactions with any date via `app_core.db.transaction_query.add_transaction(category_id, date, value, name)`.
*   Date-dependent logic accepts an explicit `current_date` parameter, so tests are deterministic.
*   Register the new `TestBalance` (`tests/app_tests/test_balance.py`, New File) and `TestReminders` (`tests/app_tests/test_reminders.py`, New File) in `tests/init_tests.py`.
*   Log assertions use `self.assertLogs(...)`.
*   Run via `main.py --test`.

### 3.1. Delayed Payments Scheduler Tests (`tests/app_tests/test_balance.py` & `tests/app_tests/test_statistics.py`)
1.  **Test Empty Future:** If there are no transactions with `date > current_date`, `future_expenses_total` must equal `0.0` and the label shows only today's balance.
2.  **Test Income Exclusion:** Add future transactions in an Income category. Verify `future_expenses_total` remains `0.0`, `projected_balance == today_balance`, and today's balance excludes the future income.
3.  **Test Mixed Dates:** Add transactions dated in the past, today and the future. Verify `get_future_totals` strictly sums only future dates (today is not future).
4.  **Test Projected Balance Math & UI String:** If today's balance is `100.0` and `future_expenses_total` is `150.0`, verify `projected_balance == -50.0`, today's balance remains `100.0`, and `format_balance_text` returns `100.0 (-50.0)`.
5.  **Test Visual Flag Trigger:** `is_projected_balance_negative` returns `True` when `projected_balance < 0` and `False` otherwise.
6.  **Test Transaction Modifications:** Adding a future expense, editing a transaction from past to future (and back), and deleting a future expense each refresh `future_expenses_total` and the label text.
7.  **Test Statistics Include Future Transactions** (`test_statistics.py`): A future-dated transaction in the selected month / quarter / year is included in the corresponding statistics.
8.  **Test Settings Totals Exclude Future:** Adding a future income / expense does not change the displayed Settings `total_income` / `total_expense`.

### 3.2. Monthly Reminders Logic Tests (`tests/app_tests/test_reminders.py` - New File)
1.  **Test Due Date Generation (Day specified):** Create a reminder on October 15th with `day=20`. Verify `next_due_date` is October 20th.
2.  **Test Due Date Generation (Day NULL):** Create a reminder on October 15th with `day=None`. Verify `next_due_date` is exactly November 1st.
3.  **Test Month Rollover Logic:** Call `update_next_due_date` on a reminder due December 15th, 2026. Verify the new date correctly rolls over to January 15th, 2027.
4.  **Test Short Month Clamp:** A reminder with `day=31` advances Jan 31 → Feb 28 (Feb 29 in a leap year) → Mar 31.
5.  **Test Detection (Not Due Yet):** Run `check_pending_reminders` when `current_date < next_due_date`. Verify the pending list is empty.
6.  **Test Detection (Due and Missing):** Run `check_pending_reminders` when `current_date >= next_due_date` and no matching transaction exists. Verify the reminder is added to the pending list.
7.  **Test Detection (Due but Paid, case-insensitive):** A matching transaction exists with different letter case (e.g. `"rent"` vs `"Rent"`). Verify the pending list is empty AND `next_due_date` was silently incremented by 1 month.
8.  **Test Category Matching:** A same-name transaction in another category does not match.
9.  **Test Covered Month (Day NULL):** A reminder with `day=None` and `next_due_date` = November 1st is resolved by a transaction in October, not by one in November.
10. **Test Ignore Action:** Trigger the "Ignore this month" logic. Verify `next_due_date` increments by 1 month and the IGNORED structured log is emitted.
11. **Test Pay Action:** Paying a pending reminder switches the viewed month/year to the covered month, creates a matching transaction, resolves the reminder, and increments `next_due_date`.
12. **Test Cascade Deletion:** Deleting a category removes its reminders; deleting an account removes all its reminders.
13. **Test Name Uniqueness:** A duplicate name (case-insensitive) in the same account is rejected; the same name in another account is allowed.
14. **Test Day Range Validation:** `day` outside 1–31 is rejected.
15. **Test Category Required:** Creating a reminder without a category is rejected.
16. **Test Account Switch:** After switching accounts, `check_pending_reminders` runs and returns only reminders of the new account.
17. **Test Mixed Skip & Pay:** With three pending reminders A, B, C: tick "Ignore" on A, pay B. Verify the window stays open, A is still ticked and not yet skipped, C is still payable; then pay A (removes its ignore mark), tick C and confirm. Verify only C is logged as IGNORED and A, B are RESOLVED.
18. **Test Auto-Close Rules:** Paying the last unticked row while a ticked row remains keeps the window open. Paying the last remaining row closes it. Closing without confirming leaves ignored rows unchanged in the DB.

### 3.3. Month / Year Notification Tests (`tests/app_tests/test_main_window.py`, extend `test_2_date_change`)
1.  **Test Month Change Message:** `next_month()` / `previous_month()` show `Month updated to {month name}` (including December ↔ January wrap).
2.  **Test Year Change Message:** `next_year()` / `previous_year()` show `Year updated to {year}`.
3.  **Test Combined Change:** `set_month_and_year()` changing both shows both lines; changing only one shows only that line.