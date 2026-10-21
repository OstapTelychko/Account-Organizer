# Implementation Plan: Delayed Payments & Monthly Reminders

This document outlines the architectural changes, database schema updates, GUI modifications, and the pragmatic TDD workflow required to implement Scheduled Delayed Payments and Monthly Reminders in the `Account-Organizer` repository.

## 1. Feature: Scheduler of Delayed Payments

### Concept
Allow users to create transactions with future dates. The application will calculate the sum of these future expenses and deduct them from the visually displayed account balance to show "available money" in parentheses. If the projected balance drops below zero, the text turns red. Future incomes are strictly excluded from this calculation to prevent false positive balances.

### 1.1. Database & Backend Changes
**No schema changes are required.** The `transactions` table already uses a unified `date` column with a database index (`ix_transactions_date`)[cite: 3].
*   **`backend/statistics_query.py`**[cite: 3]: Add a new method `get_future_expenses_sum(account_id, current_date)`.
    *   *Query logic:* `SELECT SUM(value) FROM transactions JOIN categories ON ... WHERE transactions.date > current_date AND categories.category_type = 'Expenses' AND categories.account_id = account_id`
*   **Logging Requirement (Point-In-Time Recovery):** Ensure structured logs are generated via the existing `logger.py`[cite: 3] when this state is calculated. Example format: `logger.debug('[ENTITY: DELAYED_PAYMENT] [ACTION: CALCULATED] sum=150.50')`.
*   **`AppObjects/app_core.py`**[cite: 3]: Add `projected_balance: float` and `future_expenses_total: float` to the `AppCore` state.

### 1.2. GUI & Logic Updates
*   **`AppManagement/balance.py`**[cite: 3]: 
    *   Update `calculate_current_balance` and `load_account_balance` to fetch the `future_expenses_total`.
    *   Calculate `projected_balance = current_balance - future_expenses_total`.
*   **`GUI/windows/main_window.py`**[cite: 3] **(Visuals)**:
    *   Update `account_current_balance` `QLabel` to display: `$CurrentBalance (- $FutureExpenses)`.
    *   Add color logic: `if projected_balance < 0: setStyleSheet("color: red;") else: setStyleSheet("color: default;")`
*   **Discoverability**:
    *   Wrap the balance label in a clickable widget (or use a `QToolButton`). Clicking it opens a new `DelayedPaymentsWindow` (`SubWindow`[cite: 3]) showing a `CustomTableWidget`[cite: 3] with all future transactions.

---

## 2. Feature: Monthly Payments Reminders

### Concept
A system to track recurring monthly payments. If a payment is not recorded by its due date, a popup appears on startup listing missing transactions. Users can mark them to be ignored for the current month via checkboxes, requiring final confirmation.

### 2.1. Database Schema Changes (Alembic)
Create a new migration via Alembic (e.g., `alembic revision -m "add_monthly_reminders_table"`)[cite: 3].
**New Table: `monthly_reminders`**
*   `id`: Integer, Primary Key, Autoincrement
*   `name`: String, Unique, Not Null (Validator: Min 3 chars)
*   `category_id`: Integer, ForeignKey(`categories.id`), Not Null (Mandatory)
*   `value`: Float, Nullable (Optional amount)
*   `day`: SmallInteger, Nullable (1-31, Optional day)
*   `next_due_date`: Date, Not Null. 
    *   *Logic Rule:* If `day` is specified, `next_due_date` is that day of the current month. If `day` is NULL, `next_due_date` is automatically set to the **1st day of the NEXT month** (acting as a post-factum reminder for the previous month).

### 2.2. Backend Queries & Human-Readable Logging
*   **`backend/models.py`**[cite: 3]: Add the `MonthlyReminder` model.
*   **`backend/reminder_query.py`** (New File):
    *   CRUD operations for reminders.
    *   `update_next_due_date(reminder_id, new_date)`: Shifts the date forward by 1 month.
*   **Logging Requirement (Point-In-Time Recovery):** All write and update operations MUST output structured, human-readable logs using `logger.info`[cite: 3].
    *   *Creation Example:* `logger.info('[ENTITY: REMINDER] [ACTION: CREATED] name="Rent" category_id=2 value=500 day=10')`
    *   *Skip Example:* `logger.info('[ENTITY: REMINDER] [ACTION: IGNORED] name="Rent" skipped_for_month=10-2026')`

### 2.3. Resolving Constraints
*   **Historical Scans:** The app only checks the month indicated by `next_due_date`. If `current_date >= next_due_date`, it checks the `transactions`[cite: 3] table using a **strict exact match** (`==`). If found, it silently increments `next_due_date`. If missing, it alerts the user.
*   **Name Changes:** Changing a reminder's name only affects future checks (from `next_due_date` forward). Past data is untouched.

### 2.4. App Management & Startup Flow
*   **`AppManagement/reminders_logic.py`** (New File):
    *   `check_pending_reminders()`: Loops through reminders. If `current_date >= next_due_date` and no exactly matching transaction exists, adds it to `pending_reminders_list`.
*   **`main.py`**[cite: 3]: Call `check_pending_reminders()` in `post_show_setup()`. If the list has items, execute the UI window.

### 2.5. GUI Updates
*   **`PendingRemindersWindow`** (Startup Popup - inherits `SubWindow`[cite: 3]):
    *   Displays a list of all unpaid reminders using `CustomListWidget`[cite: 3].
    *   Each row shows: `Reminder Name | Category | Expected Value (if any) | [ ] Ignore this month (Checkbox)`.
    *   **UX workflow:** Clicking "Pay" (or double-clicking a row) opens `TransactionManagementWindow`[cite: 3]. Crucially, the window must be pre-filled with the exact `name` and `category_id` to guarantee the strict match logic passes automatically.
    *   A single **"Confirm & Close"** button at the bottom. 
    *   *Action:* Clicking "Confirm" increments the `next_due_date` ONLY for items where the "Ignore this month" checkbox was ticked, logs the skip event, and leaves unchecked items to reappear on the next app launch.
*   **`RemindersManagementWindow`**:
    *   Accessible via Settings to create, edit, or delete reminders. Enforces mandatory category selection.

---

## 3. Development & Testing Workflow (Pragmatic TDD)
Because existing tests directly import from the product code (e.g., `tests/app_tests/test_statistics.py`[cite: 3]), the agent MUST follow this exact order to avoid `ImportError` exceptions:
1.  **Scaffolding:** Create the DB models (`backend/models.py`[cite: 3]), Alembic migrations[cite: 3], necessary UI file structures in `GUI/windows/`[cite: 3], and basic function signatures in `backend/`[cite: 3] and `AppManagement/`[cite: 3].
2.  **Test Implementation:** Write the tests described below in `tests/app_tests/`[cite: 3].
3.  **Refinement:** Implement and polish the core logic until all tests pass.

### 3.1. Delayed Payments Scheduler Tests (`tests/app_tests/test_statistics.py`[cite: 3] & `test_balance.py`)
1.  **Test Empty Future:** If there are no transactions with `date > current_date`, `future_expenses_total` must equal `0.0`.
2.  **Test Income Exclusion:** Add future transactions in an "Incomes" category. Verify `future_expenses_total` remains `0.0`.
3.  **Test Mixed Dates:** Add transactions with dates in the past, today, and future. Verify `get_future_expenses_sum` strictly sums only future dates.
4.  **Test Projected Balance Math & UI String:** If `current_balance` is `100.0` and `future_expenses_total` is `150.0`, verify `projected_balance` equals `-50.0`, ensure `current_balance` strictly remains `100.0` (unmodified), and verify the resulting visual summary string is formatted correctly as `100.0 (-50.0)`.
5.  **Test Visual Flag Trigger:** Verify the logic flag that triggers the red stylesheet returns `True` when `projected_balance < 0` and `False` otherwise.

### 3.2. Monthly Reminders Logic Tests (`tests/app_tests/test_reminders.py` - New File)
1.  **Test Due Date Generation (Day specified):** Create a reminder on October 15th with `day=20`. Verify `next_due_date` is October 20th.
2.  **Test Due Date Generation (Day NULL):** Create a reminder on October 15th with `day=None`. Verify `next_due_date` is exactly November 1st.
3.  **Test Month Rollover Logic:** Call `update_next_due_date` on a reminder due December 15th, 2026. Verify the new date correctly rolls over to January 15th, 2027.
4.  **Test Detection (Not Due Yet):** Run `check_pending_reminders` when `current_date < next_due_date`. Verify the pending list is empty.
5.  **Test Detection (Due and Missing):** Run `check_pending_reminders` when `current_date >= next_due_date` and no matching transaction exists in the database. Verify the reminder is added to the pending list.
6.  **Test Detection (Due but Paid):** Run `check_pending_reminders` when `current_date >= next_due_date` and an exact matching transaction exists. Verify the pending list is empty AND the `next_due_date` was silently incremented by 1 month.
7.  **Test Ignore Action:** Trigger the "Ignore this month" logic. Verify the reminder's `next_due_date` increments by 1 month and the correct structured log is emitted to the logger output.