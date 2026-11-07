# Implementation Plan: Investments (Third Category Type)

This document outlines the database, backend, GUI and test changes required to add an **Investments** category type to `Account-Organizer`. It follows the structure of `designs/delayed payments and reminders.md`.

## 1. Concept

An Investments category is one asset (e.g. `Government bonds`, `XTB fund A`). To track several funds separately, the user creates one category per fund.

Each Investments category has a timeline of **operations**, all stored as transactions with an `operation_type` (see 2):
*   **Deposit** – money moves from cash into the asset (also used for DCA monthly purchases).
*   **Withdrawal** – money moves from the asset back to cash (selling).
*   **Revaluation** – the user enters the asset's current market value (e.g. bonds +30%, fund −50%, failed fund = 0).

Effects:
*   **Cash balance** (existing `Balance` label) changes only by money movement: deposits decrease it, withdrawals increase it. Revaluations never touch cash.
*   **Investments value** (new label) = sum of current values of all Investments categories. Revaluations, deposits and withdrawals update it.
*   **Statistics** show deposits as money leaving (decrease), withdrawals as money coming back (income-like), and revaluation gains/losses on a separate "Value change" line that is not counted as income or expense.

Example: income 10000, deposit 4000 into bonds → main window shows `Balance: 6000 | Investments: 4000`; monthly statistics show `-4000` in Investments deposits and the net result decreases by 4000.

**Rules:**
*   Investment operations can't be dated in the future (`date > today` is rejected). They don't participate in delayed payments / projected balance.
*   Deposit and withdrawal values are `> 0`. A revaluation value is `>= 0`.
*   The value of an asset can never become negative at any point of its timeline (e.g. a withdrawal larger than the value at that date is rejected, also when editing/deleting earlier operations would cause it).

### 1.1. Asset value calculation
A revaluation stores the **absolute market value** entered by the user (not the delta). This keeps values correct when a forgotten deposit is added before an existing revaluation later.

Operations of one category are processed ordered by date, where on the same date deposits and withdrawals come before a revaluation. The entered market value already includes that day's deposits/withdrawals, e.g. old value 32756, the fund grew to 35000, the user deposits 4000 and enters 39000 → value change = 39000 − (32756 + 4000) = +2244.

Processing rules:
*   `value_after(deposit) = value_before + deposit`
*   `value_after(withdrawal) = value_before - withdrawal`
*   `value_after(revaluation) = revaluation.value`; its **value change** = `revaluation.value - value_before`.

Invariant (tested): `current_value = deposits - withdrawals + sum(value changes)`.

---

## 2. Database Changes (Alembic)

New migration `add_investments` (down revision `c3d4e5f6a7b8`).

*   **`transactions.operation_type`**: SmallInteger, Not Null, `server_default="0"`: `0` = Regular (Income / Expense categories), `1` = Deposit, `2` = Withdrawal, `3` = Revaluation.
    *   Added with plain `op.add_column` (no `batch_alter_table`): SQLite only updates the schema, the table isn't rewritten and the `transactions_fts` triggers stay.
    *   Cost: SQLite stores the integers 0 and 1 in the record header only, so about 1 byte per row; no index and no extra join. Income/Expense queries already filter by `categories.category_type`, so they don't need to read the column.
    *   Chosen over a separate revaluations table + negative withdrawal values: one CRUD path, one table widget loader, one timeline source, search finds all operations, and existing positive-value validation stays.
*   **`monthly_reminders`** (via `batch_alter_table`; this table has no FTS triggers):
    *   `account_id`: Integer, ForeignKey(`accounts.id`, `ondelete="CASCADE"`), Not Null, Indexed. Back-filled from the category's account. Reads filter by it directly.
    *   `category_id` becomes nullable (Investments reminders have no category, see 4.1).
    *   `reminder_type`: SmallInteger, Not Null, `server_default="0"`: `0` = Regular, `1` = Investment transfer, `2` = Investments revaluation.
    *   CHECK: `category_id IS NOT NULL` when `reminder_type = 0`, `category_id IS NULL` otherwise.
    *   `Account.reminders` relationship with `passive_deletes=True`.
*   No new account columns: `accounts.current_balance` keeps its meaning of the **cash** ledger (now also including deposits and withdrawals). The investments value is derived from operations.
*   `project_configuration.py`:
    *   `CategoryType.Investment = "Investments"`; `CategoryType.get(2)` / `get_index("Investments") == 2`.
    *   New `InvestmentOperation(IntEnum)`: `Regular = 0, Deposit = 1, Withdrawal = 2, Revaluation = 3`.
    *   New `ReminderType(IntEnum)`: `Regular = 0, InvestmentTransfer = 1, InvestmentsRevaluation = 2`.

## 3. Backend

*   **`backend/models.py`**: `Transaction.operation_type`; `MonthlyReminder.account_id`, nullable `category_id`, `reminder_type`.
*   **`backend/transaction_query.py`**: `add_transaction` / `update_transaction` accept `operation_type` (default `Regular`).
*   **`backend/investment_query.py`** (New File): `InvestmentQuery(session_factory)` with `account_id`, created in `DBController.__init__()` as `self.investment_query`, `account_id` set in `set_account_id()`.
    *   `calculate_investment_timeline(transactions) -> list[InvestmentTimelinePoint]` (module-level, pure; `InvestmentTimelinePoint` is a `NamedTuple(transaction_id, date, operation_type, value, value_after, value_change)`).
    *   `get_category_value(category_id, as_of: date) -> float`.
    *   `get_total_investments_value(as_of: date) -> float` (current account).
    *   `get_investment_totals(category_ids, start: date, end: date) -> InvestmentTotals` (`NamedTuple(deposits, withdrawals, value_change)`), used by statistics.
    *   `validate_category_timeline(category_id, changed_operation) -> bool`: simulates the add/edit/delete and returns `False` if any point becomes negative.
*   **`backend/statistics_query.py`**: existing Income/Expense sums already filter by category type; verify every query does, so investment transactions never leak into income/expense totals.
*   **Logging (Point-In-Time Recovery)** via `logger.info`:
    *   `[ENTITY: INVESTMENT] [ACTION: DEPOSIT] category="XTB" date=2026-11-07 value=4000 value_after=4000`
    *   `[ENTITY: INVESTMENT] [ACTION: WITHDRAWAL] ...`
    *   `[ENTITY: INVESTMENT] [ACTION: REVALUATED] category="XTB" date=2026-11-30 value=5200 change=1200`
    *   `[ACTION: UPDATED]` / `[ACTION: DELETED]` with old and new fields.

## 4. App Management

*   **`AppObjects/app_core.py`**: `investments_value: float = 0.0`; `get_income_and_expense_categories_as_ids()` stays, add the Investments ids getter (or extend into a `NamedTuple` of three lists).
*   **`AppManagement/balance.py`**:
    *   `calculate_current_balance()`: cash = start + incomes − expenses − deposits + withdrawals. Revaluations are ignored.
    *   `refresh_balance_label()`: also sets `app_core.investments_value = get_total_investments_value(today)` and the new label (see 5.1).
    *   Settings `total_income` / `total_expense` are unchanged (Income/Expense only).
*   **`AppManagement/transaction.py`**: for Investments categories (tab index 2):
    *   The window passes the selected operation as `operation_type`.
    *   Reject future dates, non-positive deposit/withdrawal, negative revaluation, and timeline-negative changes (new `Messages` windows).
    *   Skip the incremental income/expense updates; finish with `update_account_balance()`.
*   **`AppManagement/category.py`**: `create_category()` / `remove_category()` handle the third type (position counters per type). Deleting an Investments category removes its operations; cash returns to the state without them (same as deleting an expense category today).
### 4.1. Reminders (`AppManagement/reminders_logic.py`)
Investments reminders are attached to the **account**, not to one fund, because the monthly amount is split between funds and some months a fund gets nothing.
*   **Investment transfer** reminder (e.g. `Invest`, value 4000, day 10): resolved when **any** deposit into **any** Investments category of the account exists in the covered month. Name and value aren't compared (one fund getting money is enough).
*   **Investments revaluation** reminder: resolved when every Investments category with value `> 0` at the start of the covered month has a revaluation in that month.
*   Regular reminders can't use an Investments category (use the transfer reminder instead).
*   `pay_reminder()` for both Investments types switches to the covered month, selects tab 2 and opens `MonthlyInvestmentsWindow` (5.4); the transfer reminder pre-fills the total amount.
*   After saving, only that reminder is re-checked, as for regular reminders.

## 5. GUI

### 5.1. Main window (`GUI/windows/main_window.py`)
*   Third tab `Investments` in `Incomes_and_expenses` with `Investments_scroll` / `Investments_window_layout`, built like the existing two. `GUI/category.py` `load_category()` routes the third type there.
*   Balance label: `Balance: <today> (<projected>) | Investments: <value>`.
    *   The projected part and its link/red styling keep the delayed payments rules (cash only).
    *   The `| Investments: ...` part is shown only when the account has at least one Investments category.

### 5.2. Investments category widget (`GUI/category.py`)
*   The header label (where regular categories show `Total: <month sum>`) shows the asset value at the end of the viewed month (or today for the current month): `Value: 39000`.
*   Table columns: `Day | Operation | Name | Value | Value after`, for operations of the viewed month. Revaluation rows show the change in parentheses, green/red (e.g. `39000 (+2244)`).
*   Buttons: the existing add transaction button opens the operation window; edit/delete work as for transactions.

### 5.3. Operation window (`TransactionManagementWindow`)
*   On the Investments tab it shows an operation selector (Deposit / Withdrawal / Revaluation). For Revaluation the value field label becomes `Current value`, pre-filled with the value at the selected date.
*   Name is optional; the table shows the translated operation name when empty.
*   The add button is disabled when the viewed month is in the future.

### 5.4. `MonthlyInvestmentsWindow` (`GUI/windows/investments.py`, New File)
One place for the monthly routine; opened from a button on the Investments tab and by Investments reminders.
*   Day field (date = viewed month + day, not in the future), optional total amount with a `Remaining: X` label.
*   One row per Investments category: `Fund | Current value | Deposit | New value`.
    *   `Deposit` empty or 0 → no deposit for that fund (a skyrocketing fund can be skipped).
    *   `New value` empty → no revaluation; filled → revaluation including that day's deposit (39000 in the example).
*   Save validates all rows first and then writes all operations, so a single invalid row writes nothing.

### 5.5. Reminders management window
*   A type selector: Regular / Investment transfer / Investments revaluation. The category field is shown only for Regular and lists Income/Expense categories; value is hidden for revaluation.

### 5.6. Statistics (`Statistics/statistics.py`, `Statistics/copy_statistics.py`)
For monthly, quarterly, yearly and custom range statistics:
*   **Every category type is optional.** The current requirement of at least one Income and one Expense category (and transactions in both) is removed. The `no_category` / `no_transactions` messages are shown only when the account has no categories at all / the period has no operations at all.
*   Blocks for types without categories are hidden; a type with categories but no operations in the period shows zeros.
*   Net line (`Statistics` translation 8) = income − expenses − deposits + withdrawals.
*   New block `Investments`: total deposits, total withdrawals, value change, then per category: deposits, withdrawals, value change and value at the end of the period.
*   `copy_statistics.get_category_type()` supports tab index 2.

### 5.7. Translations
New keys in `languages.json` for **English, Українська and Polski** (tab name, `Investments:` label prefix, operation names, `Current value`, `Value after`, statistics lines, new error messages), accessors in `languages.py`, updates in `AppManagement/language.change_language()`. New `Messages` windows are appended at the end. Check Polish texts fit fixed-size buttons.

---

## 6. Development & Testing Workflow (Pragmatic TDD)
1.  **Scaffolding:** `CategoryType` / `InvestmentOperation` / `ReminderType`, models, migration, `InvestmentQuery` signatures, third tab layout, `MonthlyInvestmentsWindow` skeleton.
2.  **Tests:** write the tests below.
3.  **Refinement:** implement until all tests pass; run `.venv1/bin/python -m mypy .`.

**Test infrastructure:**
*   `DBTestCase` gets a helper to create an Investments category (not created by default, so existing suites are unaffected); `tearDown` cleanup already deletes transactions before categories.
*   New `TestInvestments` in `tests/app_tests/test_investments.py`, registered in `tests/init_tests.py`.
*   Date-dependent functions accept an explicit `current_date` / `as_of`.

### 6.1. Value calculation (`test_investments.py`)
1.  **Deposit:** deposit 4000 → value 4000, cash decreases by 4000, settings totals unchanged.
2.  **Withdrawal:** deposit 4000, withdraw 1000 → value 3000, cash +1000.
3.  **Revaluation up/down/zero:** value 4000, revalue 5200 → change +1200, investments label 5200; revalue 0 → change −5200, value 0. Cash unchanged in all cases.
4.  **DCA after revaluation:** deposit 1000, revalue 1300, deposit 1000 → value 2300.
5.  **Forgotten earlier deposit:** deposit 1000 (Jan 5), revalue 1300 (Jan 31), then add deposit 500 (Jan 10) → value stays 1300, change becomes −200.
6.  **Same-day order:** value 32756, deposit 4000 and revaluation 39000 on the same day → value 39000, change +2244.
7.  **Invariant:** `value == deposits - withdrawals + sum(changes)` for a mixed timeline.
8.  **Several assets:** total investments value is the sum of categories; another account's investments are excluded.

### 6.2. Validation
1.  Future-dated operation is rejected.
2.  Deposit/withdrawal `<= 0` and revaluation `< 0` are rejected.
3.  Withdrawal larger than the value at its date is rejected.
4.  Editing/deleting an earlier deposit that makes a later withdrawal exceed the value is rejected.

### 6.3. Balance & labels (`test_balance.py`)
1.  Label shows `| Investments: 4000` only when an Investments category exists.
2.  With a future expense the label shows `Balance: 6000 (5500) | Investments: 4000`.
3.  Deleting an Investments category restores cash and removes the investments part.
4.  The Investments category header shows the value at the end of the viewed month (a later month shows the later value).

### 6.4. Monthly investments window
1.  Total 4000 split into 2500 / 1500 / empty → two deposits, the third fund untouched, cash −4000.
2.  `New value` filled → revaluation including the same-day deposit; empty → no revaluation.
3.  One invalid row (e.g. future day, negative value) → nothing is written.

### 6.5. Statistics (`test_statistics.py`)
1.  Monthly: deposit 4000 decreases the net line by 4000; withdrawal increases it; revaluation doesn't change it but appears as value change.
2.  Income/expense totals don't include investment transactions.
3.  Quarterly / yearly / custom range include the Investments block with correct per-category end-of-period values.
4.  Only expenses, only incomes, or only investments → statistics are shown with the other blocks hidden.
5.  No categories / no operations in the period → the existing messages are shown.

### 6.6. Reminders (`test_reminders.py`)
1.  Transfer reminder is resolved by a deposit into any one Investments category in the covered month; a withdrawal or revaluation doesn't resolve it.
2.  Revaluation reminder stays pending until every fund with value `> 0` has a revaluation in the covered month; funds with value 0 are skipped.
3.  Pay of an Investments reminder switches to the covered month, selects the Investments tab and opens `MonthlyInvestmentsWindow` (transfer pre-fills the total).
4.  Regular reminder with an Investments category, and Investments reminder with a category, are rejected.
5.  Deleting an account removes its Investments reminders.

### 6.7. Migration
1.  Existing reminders get `account_id` from their category and `reminder_type = 0`; they keep working.
2.  Existing transactions get `operation_type = 0`; FTS search still finds transactions added after the migration (triggers kept).
