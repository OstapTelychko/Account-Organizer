# Geminis / AI Coding Assistant Instructions

These guidelines apply to Gemini and other AI coding assistants working in the **Account-Organizer** workspace.

## 1. Code Quality & Style Rules
- **PEP 8 Compliance**: All new and modified Python code must strictly follow PEP 8 style guidelines.
- **Type Annotations**: All functions, methods, and variables must include complete and accurate type annotations (using Python's `typing` module or modern built-in generic types where applicable).
- **Docstrings**: Every module, class, function, and method must include clear, comprehensive docstrings explaining its purpose, parameters, and return types.
- **Import Placement**: All imports **must** be placed at the very top of the file. Importing modules inside functions, methods, or in the middle of code blocks is strictly prohibited, except for intentional lazy imports in the application startup path (especially `main.py`) that reduce startup time before the first window is shown. Preserve those startup lazy imports; in all other files and code paths, keep imports at the top of the file.

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

## 5. Workspace Safety
- Inspect the working tree and current file contents before editing; preserve user changes and do not overwrite unrelated modifications.
- Use the project virtual environment (`.venv1`) for Python commands and tests whenever it is available.
- Do not modify generated or runtime data such as `build/`, `Logs/`, `DB Backups/`, test databases, or temporary backup directories unless explicitly requested.
- Keep patches narrowly scoped and avoid broad reformatting of unrelated code.
