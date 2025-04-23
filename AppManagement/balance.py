from AppObjects.session import Session
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from languages import LanguageStructure



logger = get_logger(__name__)

def calculate_current_balance() -> None:
    """Calculate current balance. It sums up all incomes and expenses and updates the account balance."""

    Session.current_total_income = 0
    Session.current_total_expenses = 0

    for category in Session.db.category_query.get_all_categories():

        if category.category_type == "Incomes":
            for transaction in Session.db.transaction_query.get_all_transactions(category.id):
                Session.current_total_income += transaction.value

        elif category.category_type == "Expenses":
            for transaction in Session.db.transaction_query.get_all_transactions(category.id):
                Session.current_total_expenses += transaction.value
    
    Session.current_total_income = round(Session.current_total_income, 2)
    Session.current_total_expenses = round(Session.current_total_expenses, 2)

    Session.current_balance = Session.db.account_query.get_account().start_balance + round(Session.current_total_income - Session.current_total_expenses, 2)

    Session.db.account_query.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)
    WindowsRegistry.MainWindow.account_current_balance.setText(LanguageStructure.MainWindow.get_translation(0)+str(Session.current_balance))
    WindowsRegistry.SettingsWindow.total_income.setText(LanguageStructure.Statistics.get_translation(4)+str(Session.current_total_income))
    WindowsRegistry.SettingsWindow.total_expense.setText(LanguageStructure.Statistics.get_translation(6)+str(Session.current_total_expenses))


def load_account_balance() -> None:
    """Load account balance from database. If total income and expenses are 0, recalculate the balance."""

    logger.info("Loading account balance")
    account = Session.db.account_query.get_account()
    Session.current_balance = account.current_balance
    Session.current_total_income = account.current_total_income
    Session.current_total_expenses = account.current_total_expenses

    if Session.current_total_income == 0 and Session.current_total_expenses == 0:
        logger.info("Recalculating account balance")
        calculate_current_balance()
    
    WindowsRegistry.MainWindow.account_current_balance.setText(LanguageStructure.MainWindow.get_translation(0)+str(Session.current_balance))
    WindowsRegistry.SettingsWindow.total_income.setText(LanguageStructure.Statistics.get_translation(4)+str(Session.current_total_income))
    WindowsRegistry.SettingsWindow.total_expense.setText(LanguageStructure.Statistics.get_translation(6)+str(Session.current_total_expenses))
    logger.info(f"Current balance: {Session.current_balance} | Total income: {Session.current_total_income} | Total expenses: {Session.current_total_expenses}")


def update_account_balance() -> None:
    """Update account balance. It updates balance in database and GUI."""

    Session.db.account_query.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)

    WindowsRegistry.MainWindow.account_current_balance.setText(LanguageStructure.MainWindow.get_translation(0)+str(Session.current_balance))
    WindowsRegistry.SettingsWindow.total_income.setText(LanguageStructure.Statistics.get_translation(4)+str(Session.current_total_income))
    WindowsRegistry.SettingsWindow.total_expense.setText(LanguageStructure.Statistics.get_translation(6)+str(Session.current_total_expenses))