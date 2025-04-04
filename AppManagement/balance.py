from AppObjects.session import Session
from AppObjects.logger import get_logger
from languages import LANGUAGES

from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow


logger = get_logger(__name__)

def calculate_current_balance():
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
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Windows"]["Main"][0]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Windows"]["Statistics"][4]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Windows"]["Statistics"][6]+str(Session.current_total_expenses))


def load_account_balance():
    """Load account balance from database. If total income and expenses are 0, recalculate the balance."""

    logger.info("Loading account balance")
    account = Session.db.account_query.get_account()
    Session.current_balance = account.current_balance
    Session.current_total_income = account.current_total_income
    Session.current_total_expenses = account.current_total_expenses

    if Session.current_total_income == 0 and Session.current_total_expenses == 0:
        logger.info("Recalculating account balance")
        calculate_current_balance()
    
    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Windows"]["Main"][0]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Windows"]["Statistics"][4]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Windows"]["Statistics"][6]+str(Session.current_total_expenses))
    logger.info(f"Current balance: {Session.current_balance} | Total income: {Session.current_total_income} | Total expenses: {Session.current_total_expenses}")


def update_account_balance():
    """Update account balance. It updates balance in database and GUI."""

    Session.db.account_query.update_account_balance(Session.current_balance, Session.current_total_income, Session.current_total_expenses)

    MainWindow.account_current_balance.setText(LANGUAGES[Session.language]["Windows"]["Main"][0]+str(Session.current_balance))
    SettingsWindow.total_income.setText(LANGUAGES[Session.language]["Windows"]["Statistics"][4]+str(Session.current_total_income))
    SettingsWindow.total_expense.setText(LANGUAGES[Session.language]["Windows"]["Statistics"][6]+str(Session.current_total_expenses))