# Geminis / AI Coding Assistant Instructions

These guidelines apply to Gemini and other AI coding assistants working in the **Account-Organizer** workspace.

## 1. Code Quality & Style Rules
- **PEP 8 Compliance**: All new and modified Python code must strictly follow PEP 8 style guidelines.
- **Type Annotations**: All functions, methods, and variables must include complete and accurate type annotations (using Python's `typing` module or modern built-in generic types where applicable).
- **Docstrings**: Every module, class, function, and method must include clear, comprehensive docstrings explaining its purpose, parameters, and return types.
- **Import Placement**: All imports **must** be placed at the very top of the file. Importing modules inside functions, methods, or in the middle of code blocks is strictly prohibited, except for intentional lazy imports in the application startup path (especially `main.py`) that reduce startup time before the first window is shown. Preserve those startup lazy imports; in all other files and code paths, keep imports at the top of the file.
- **Function Design**:
  - Create a helper function only to avoid duplicating logic. Code used in a single place must stay inline in its caller (Qt signal/`QTimer` slots and entry points are the exception).
  - Functions whose body is a single line or a thin wrapper around another call are not acceptable; call the wrapped code directly.
  - Don't add trivial predicates (e.g. `is_negative(value)`) and don't write tests that only check Python built-ins.
- **Return types**: return a `NamedTuple` or dataclass instead of a bare tuple of several values (e.g. `tuple[str, int|None, float|None]`), so callers use field names.

## 2. Workspace Constraints & Rules
- **DO NOT touch the `TODO` file**: The user maintains the `TODO` file manually. Never edit, append to, or modify the `TODO` file under any circumstances.
- **Project Structure**: 
  - Core app management and logic reside in `AppManagement/`.
  - Core state, database, and utilities reside in `AppObjects/` and `backend/`.
  - Desktop UI components (PySide6) reside in `DesktopQtToolkit/` and `GUI/`.
  - Database migrations are handled via `alembic/`.
  - Tests are located in `tests/`.

## 3. General Development Guidelines
- Always ensure changes are fully compatible with **Python 3.13+** and **PySide6**.
- Run type-checking or linting configurations (`mypy.ini`, `pyrightconfig.json`) when making structural changes.
- Keep answers concise and follow the exact instructions requested by the user.

## 4. Test Execution
- Run the application test suite through `main.py --test`; do not invoke the test modules directly.
- The test runner is assembled in `tests/init_tests.py`.
- To run only selected test suites, temporarily comment out the unwanted suite registrations in `tests/init_tests.py` before running `main.py --test`.
- Restore any temporarily commented suite registrations after selective testing.
- Do not run multiple application test sessions concurrently; the application uses a single-instance guard and concurrent runs conflict.
- The full suite takes several minutes; run it with output redirected to a file (`.venv1/bin/python main.py --test > /tmp/out.txt 2>&1`) and grep the file for `FAIL|ERROR|Ran `.
- Type checking: `.venv1/bin/python -m mypy .` (pyright isn't installed).

## 5. Workspace Safety
- Inspect the working tree and current file contents before editing; preserve user changes and do not overwrite unrelated modifications.
- Use the project virtual environment (`.venv1`) for Python commands and tests whenever it is available.
- Do not modify generated or runtime data such as `build/`, `Logs/`, `DB Backups/`, test databases, or temporary backup directories unless explicitly requested.
- Keep patches narrowly scoped and avoid broad reformatting of unrelated code.

## 6. Known Pitfalls and Their Solutions
### Database
- **Alembic configs**: always create them with `backend.db_controller.create_alembic_config`. Otherwise `alembic/env.py` runs `fileConfig`, which disables every existing app logger and replaces the app log handlers (logs silently stop).
- **Foreign keys are enforced** (`PRAGMA foreign_keys=ON` in `DBController`). Bulk deletes (`session.query(Model).delete()`) must delete children before parents (see `tests/tests_toolkit.py` `tearDown`). For DB-level `ON DELETE CASCADE` use an ORM relationship with `passive_deletes=True`. Migrations run on alembic's own engine without FK enforcement.
- **Detached ORM objects**: every query method opens and closes its own session (`expire_on_commit=False`), so lazy relationships fail after return. Use `joinedload(...)` for relationships the caller needs (e.g. `reminder.category`).
- **Unicode case-insensitive comparison**: compare with `strip().casefold()` in Python; SQLite `lower()` is ASCII-only.
- **Account balances**: `accounts.current_balance`, `current_total_income`, `current_total_expenses` (and the same `AppCore` fields) are ledger values that include future-dated transactions. Today's/projected balance and the Settings totals are derived in `AppManagement/balance.refresh_balance_label`. Code that changes transactions must end with `update_account_balance()` or `calculate_current_balance()`, which call `refresh_balance_label()`. Future incomes are never counted as available money.

### Dates
- `timedelta` can't add months. Use `GeneralTools.Utils.shift_month` and `get_due_date_for_covered_month` (clamps day 31 to short months and restores it later).
- `TransactionManagementWindow` builds the transaction date from the viewed month/year plus the entered day, and `transaction_data_handler` finds the category by window title and the current Income/Expense tab. To pre-fill a transaction for another month, call `AppManagement.date.set_month_and_year` and select the tab first.

### GUI and translations
- Every new text needs keys in `languages.json` for **English, Українська and Polski**, an accessor in `languages.py` and an update in `AppManagement/language.change_language()`. Polish (then Ukrainian) texts are the longest; check they fit fixed-size buttons (`create_button` sets min = max size).
- `Messages` windows are translated by creation order (`GUI/windows/messages.py` index = `Messages` key in `languages.json`); append new message windows at the end.
- `InformationMessage` must not use `Qt.WindowType.Popup`: popups grab input, which blocks shortcuts and clicks while the message is shown.
- Tables in sub windows use `setProperty("class", "category_data")` to get the category table background. qdarktheme paints `QHeaderView` black, so `GUI/theme.py` overrides `.category_data QHeaderView` for both themes.
- A plain `QWidget` subclass styled through a QSS class needs `setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)`.
- qdarktheme gives every `QWidget` a dark background, so containers such as `QTabWidget`/`QTabBar` placed in a `wrapper` need a `background-color:transparent` stylesheet. Group related controls in separate wrappers (`create_wrapper_widget`), like the date selector on the main window.
- qdarktheme doesn't mark the focused `QPushButton`; `GUI/theme.py` styles `QMessageBox QPushButton:focus` so keyboard users see which button Enter presses.
- Don't pass an alignment flag to `layout.addWidget` for a word-wrapped `QLabel` (its height gets cropped); use `label.setAlignment(...)` instead.
- Outside test mode `SubWindow.done` closes after a 200 ms animation; in test mode it closes immediately, so timing-dependent GUI behaviour can differ between tests and real use.

### Tests
- GUI flows: schedule the next step with `QTimer.singleShot(ms, self.catch_failure(callback))` before triggering a modal `exec()`, because `exec()` blocks.
- Date-dependent logic must accept an explicit `current_date` so tests are deterministic. `DBTestCase` creates one income and one expense transaction (1000 each) dated today.
- Tests that change the viewed month must restore it in `tearDown`; tests that change balances must call `calculate_current_balance()` after the database cleanup so later suites start from zero.
- `load_account_data` schedules a pending reminders check with `QTimer`; a due reminder opens a modal window in later steps of the test.
