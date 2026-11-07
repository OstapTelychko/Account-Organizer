---
name: feature-dev-testing
description: "Use when developing, translating or testing an Account-Organizer feature: running only selected test suites, checking that English/Ukrainian/Polish texts fit fixed-size buttons, writing GUI tests with modal windows, adding DB columns with alembic migrations, or running mypy before finishing."
---

# Feature development and testing

Run every command from the repository root. Never run two test sessions at the same time (single-instance guard).

## Scripts

### Run selected test suites
```bash
.venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py --list
.venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py TestInvestments TestReminders
.venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py   # full suite, several minutes
```
Temporarily comments out other registrations in `tests/init_tests.py` and always restores them. Prints `Tests found`, `Ran`, `OK`/`FAILED` and tracebacks of failed tests; full output goes to `/tmp/account_organizer_tests.txt`. `ERROR` lines from `download_update` in the log are expected noise, not failures. Exit code 1 means failures.

### Check that translated texts fit a widget
```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=. .venv1/bin/python .github/skills/feature-dev-testing/check_text_fit.py \
    --width 190 Windows.Investments.13 --text "Literal text"
```
Measures each key of `languages.json` (path without the language) in every language with `BASIC_FONT`, keeping 20 px for padding (`--padding`). `TIGHT` rows need a wider widget or a shorter text. Use the size passed to `create_button(text, (width, height))`.

## Feature checklist
1. **Model change**: add the column to `backend/models.py` and a migration in `alembic/versions/` (set `down_revision` to the current head). Test it on a scratch copy of a DB: `create_alembic_config(...)` + `command.upgrade(config, "head")`, never `alembic` with `fileConfig`.
2. **Texts**: add keys for English, Українська and Polski, an accessor in `languages.py` and updates in `AppManagement/language.py` (`change_language_for_startup` for main window widgets, `change_language` for the rest). Append new `Messages` windows at the end of `GUI/windows/messages.py` and use the next index in all three languages. Then run `check_text_fit.py` for every new button text.
3. **Types**: `.venv1/bin/python -m mypy .` must report no issues.
4. **Tests**: add a `tests/app_tests/test_<feature>.py` suite and register it in `tests/init_tests.py`, run it alone with `run_selected_tests.py`, then run the full suite.

## Writing tests
- Inherit `DBTestCase, OutOfScopeTestCase`; set `TIMEOUT_SEC` if a test opens several windows.
- Modal windows block on `exec()`: schedule the next step first with `QTimer.singleShot(100, self.catch_failure(callback))`, then trigger the window. Close message windows with `message.ok_button.click()` and the parent with `done(1)`, then `qsleep(300)` before asserting the DB.
- Call app functions directly (`show_add_transaction_window(name)`, `remove_transaction(table, id)`) for extra categories instead of calling `activate_categories()` again.
- Use explicit dates and `current_date` arguments; use different dates when same-day ordering matters (Investments revaluations are applied after deposits/withdrawals of that day).
- In `tearDown` restore the viewed month (`set_month_and_year(today.month, today.year)`), call `super().tearDown()`, then `calculate_current_balance()`.
- Read table cells with `DesktopQtToolkit.Utils.get_table_widget_item` (mypy treats `item()` as optional).
