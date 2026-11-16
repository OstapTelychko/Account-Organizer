---
name: code-review
description: "Use when reviewing Account-Organizer code: reviewing a branch/merge/PR that implements a design plan from designs/ (e.g. investments, delayed payments and reminders), reviewing uncommitted changes or a single commit for a simpler task, checking a diff against the design, project rules, translations, migrations, tests and mypy."
---

# Code review

Review only; don't edit code unless the user asks to fix the findings. Run commands from the repository root. Don't edit the `TODO` file.

## 1. Collect the change
- Uncommitted work: `git status` and `git --no-pager diff HEAD`.
- Branch / merge: `git --no-pager log --oneline <base>..<branch>` and `git --no-pager diff <base>...<branch>` (for a merge commit: `git --no-pager diff <merge>^1 <merge>`).
- Single commit: `git --no-pager show <commit>`.
- Read the full changed functions and their callers, not just the diff hunks.

## 2. Find the requirements
- **Designed task**: read the matching plan in `designs/` and build a checklist from every numbered section (DB, backend, app management, GUI, statistics, translations, tests, migration). Mark each item as done, partly done, or missing, and note deliberate deviations.
- **Simpler task**: take the requirements from the user's request, the commit messages, or the `TODO` entry (read-only) and check that the change does exactly that, with no unrelated edits.

## 3. Check correctness
- Logic errors, edge cases (empty tables, `None`, the first/last month, day 31, leap years), off-by-one and date math (use `shift_month` / `get_due_date_for_covered_month`, never `timedelta` for months).
- Balances: every path that changes transactions ends with `update_account_balance()` or `calculate_current_balance()`; future incomes aren't counted as available money; Investments deposits/withdrawals go through `calculate_current_balance()`.
- DB: new columns have an alembic migration with the correct `down_revision` (single head), a working `downgrade`; FK-safe delete order; `joinedload` for relationships used after the session closes; `casefold()` for Unicode comparisons; alembic configs made via `create_alembic_config`.
- Investments: `reminder.category is None` handled; `CategoryType.get(...)` and `AppCore.focused_categories` used instead of income/expense-only code; `prepare_operation_type()` before `TransactionManagementWindow.exec()`.
- Qt: signals connected once (no duplicate `connect` on reload), `clicked` passes `checked`, `isHidden()` vs `isVisible()`, no `Qt.WindowType.Popup` for messages, modal flows don't block.
- Security: no SQL built from strings (use SQLAlchemy parameters), no secrets in code or logs, safe file paths.

## 4. Check project rules (`.github/copilot-instructions.md`)
- PEP 8, full type annotations, docstrings on new modules/classes/functions.
- Imports at the top of the file (except startup lazy imports in `main.py`).
- No single-use helpers, no thin one-line wrappers, no trivial predicates; `NamedTuple`/dataclass instead of multi-value tuples.
- Comments are short and say what the code can't.
- New texts exist in English, Українська and Polski, have a `languages.py` accessor and are updated in `AppManagement/language.py`; new `Messages` windows are appended at the end. Check button fit:
  `QT_QPA_PLATFORM=offscreen PYTHONPATH=. .venv1/bin/python .github/skills/feature-dev-testing/check_text_fit.py --width <w> <key>`
- No changes to `build/`, `Logs/`, `DB Backups/` or test databases.

## 5. Check tests
- New behaviour has tests in `tests/app_tests/`, new suites are registered in `tests/init_tests.py`, and the tests listed in the design exist.
- Tests are deterministic (explicit `current_date`), restore the viewed month and call `calculate_current_balance()` in `tearDown`, and don't call `activate_categories()` again.
- Run (one session at a time):
  ```bash
  .venv1/bin/python -m mypy .
  .venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py <ChangedSuites>
  ```
  Run the full suite for a designed task before approving.

## 6. Report
Give each finding a severity, a file link with line numbers and a concrete fix. Group findings by severity:
1. **Critical** (blocks merge) – the change breaks existing project logic: regressions in features that worked before, wrong balances or totals, data loss, broken or non-reversible migrations, failing old tests, crashes on startup or in existing windows.
2. **Warning** (blocks merge) – a mistake in the new feature: wrong or missing behaviour, unimplemented design items, unhandled edge cases, missing translations or tests, mypy errors, violations of the project rules from section 4.
3. **Nit** (merge allowed) – an optional improvement: readability, naming, simplification, shorter comments, extra test coverage.

End with the design checklist status (designed tasks), mypy and test results, and a verdict:
- **Blocked** if there is any Critical or Warning finding; list what must be fixed first.
- **Ready to merge** if there are only Nits (or no findings).

Don't list things that are fine.
