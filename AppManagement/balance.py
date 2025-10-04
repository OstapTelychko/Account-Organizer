from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from languages import LanguageStructure



logger = get_logger(__name__)

def calculate_current_balance() -> None:
    """Calculate current balance. It sums up all incomes and expenses and updates the account balance."""

    app_core = AppCore.instance()
    app_core.current_total_income = 0
    app_core.current_total_expenses = 0

    for category in app_core.db.category_query.get_all_categories():

        if category.category_type == "Incomes":
            for transaction in app_core.db.transaction_query.get_all_transactions(category.id):
                app_core.current_total_income += transaction.value

        elif category.category_type == "Expenses":
            for transaction in app_core.db.transaction_query.get_all_transactions(category.id):
                app_core.current_total_expenses += transaction.value
    
    app_core.current_total_income = round(app_core.current_total_income, 2)
    app_core.current_total_expenses = round(app_core.current_total_expenses, 2)

    start_balance = app_core.db.account_query.get_account().start_balance
    app_core.current_balance = start_balance + round(app_core.current_total_income - app_core.current_total_expenses, 2)

    app_core.db.account_query.update_account_balance(
        app_core.current_balance,
        app_core.current_total_income,
        app_core.current_total_expenses
    )
    WindowsRegistry.MainWindow.account_current_balance.setText(
        f"{LanguageStructure.MainWindow.get_translation(0)}{app_core.current_balance}"
    )
    WindowsRegistry.SettingsWindow.total_income.setText(
        f"{LanguageStructure.Statistics.get_translation(4)}{app_core.current_total_income}"
    )
    WindowsRegistry.SettingsWindow.total_expense.setText(
        f"{LanguageStructure.Statistics.get_translation(6)}{app_core.current_total_expenses}"
    )


def load_account_balance() -> None:
    """Load account balance from database. If total income and expenses are 0, recalculate the balance."""

    app_core = AppCore.instance()
    logger.info("Loading account balance")
    account = app_core.db.account_query.get_account()
    app_core.current_balance = account.current_balance
    app_core.current_total_income = account.current_total_income
    app_core.current_total_expenses = account.current_total_expenses

    if app_core.current_total_income == 0 and app_core.current_total_expenses == 0:
        logger.info("Recalculating account balance")
        calculate_current_balance()

    WindowsRegistry.MainWindow.account_current_balance.setText(
        f"{LanguageStructure.MainWindow.get_translation(0)}{app_core.current_balance}"
    )
    WindowsRegistry.SettingsWindow.total_income.setText(
        f"{LanguageStructure.Statistics.get_translation(4)}{app_core.current_total_income}"
    )
    WindowsRegistry.SettingsWindow.total_expense.setText(
        f"{LanguageStructure.Statistics.get_translation(6)}{app_core.current_total_expenses}"
    )
    logger.info(f"Current balance: {app_core.current_balance}\
                | Total income: {app_core.current_total_income}\
                | Total expenses: {app_core.current_total_expenses}")


def update_account_balance() -> None:
    """Update account balance. It updates balance in database and GUI."""

    app_core = AppCore.instance()
    app_core.db.account_query.update_account_balance(app_core.current_balance, app_core.current_total_income, app_core.current_total_expenses)

    WindowsRegistry.MainWindow.account_current_balance.setText(
        f"{LanguageStructure.MainWindow.get_translation(0)}{app_core.current_balance}"
    )
    WindowsRegistry.SettingsWindow.total_income.setText(
        f"{LanguageStructure.Statistics.get_translation(4)}{app_core.current_total_income}"
    )
    WindowsRegistry.SettingsWindow.total_expense.setText(
        f"{LanguageStructure.Statistics.get_translation(6)}{app_core.current_total_expenses}"
    )