from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
from datetime import date
from PySide6.QtCore import Qt

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from GUI.gui_constants import ALIGNMENT

from languages import LanguageStructure
from project_configuration import CategoryType, DISPLAY_DATE_FORMAT

if TYPE_CHECKING:
    from backend.models import Account



logger = get_logger(__name__)

DELAYED_PAYMENTS_LINK = "delayed_payments"
PROJECTED_BALANCE_COLOR = "dodgerblue"
NEGATIVE_PROJECTED_BALANCE_COLOR = "red"

class BalanceProjection(NamedTuple):
    """Today's balance and projected balance (today's balance minus future expenses)."""

    today: float
    projected: float


def calculate_today_and_projected_balance(
        ledger_balance:float,
        future_incomes:float,
        future_expenses:float
    ) -> BalanceProjection:
    """Calculate today's and projected balance from the stored balance that includes future transactions.
    Future incomes are never counted: the stored balance already contains them, so they are subtracted out.

        Arguments
        ---------
            `ledger_balance` : (float) - Stored account balance (includes past and future transactions).
            `future_incomes` : (float) - Sum of income transactions dated after today.
            `future_expenses` : (float) - Sum of expense transactions dated after today.
        Returns
        -------
            `BalanceProjection` - Today's balance and projected balance.
    """

    today_balance = round(ledger_balance - future_incomes + future_expenses, 2)
    return BalanceProjection(today=today_balance, projected=round(today_balance - future_expenses, 2))


def get_account_today_balance(account:Account, current_date:date|None = None) -> float:
    """Get today's balance of any account.

        Arguments
        ---------
            `account` : (Account) - Account to calculate balance for.
            `current_date` : (date|None) - Date considered as today. Defaults to `date.today()`.
        Returns
        -------
            `float` - Today's balance of the account.
    """

    current_date = current_date or date.today()
    future_totals = AppCore.instance().db.statistics_query.get_future_totals(current_date, account.id)
    return calculate_today_and_projected_balance(
        account.current_balance, future_totals.incomes, future_totals.expenses
    ).today


def refresh_balance_label(current_date:date|None = None) -> None:
    """Recalculate future totals and update the balance label and Settings totals.

        Arguments
        ---------
            `current_date` : (date|None) - Date considered as today. Defaults to `date.today()`.
    """

    app_core = AppCore.instance()
    current_date = current_date or date.today()

    future_totals = app_core.db.statistics_query.get_future_totals(current_date)
    app_core.future_incomes_total = future_totals.incomes
    app_core.future_expenses_total = future_totals.expenses
    balance_projection = calculate_today_and_projected_balance(
        app_core.current_balance, future_totals.incomes, future_totals.expenses
    )
    app_core.today_balance = balance_projection.today
    app_core.projected_balance = balance_projection.projected
    logger.debug(
        f"[ENTITY: DELAYED_PAYMENT] [ACTION: CALCULATED] future_expenses={future_totals.expenses} "
        f"future_incomes={future_totals.incomes} today_balance={app_core.today_balance} "
        f"projected_balance={app_core.projected_balance}"
    )

    has_future_expenses = future_totals.expenses > 0
    balance_text = f"{LanguageStructure.MainWindow.get_translation(0)}{app_core.today_balance}"
    if has_future_expenses:
        color = NEGATIVE_PROJECTED_BALANCE_COLOR if app_core.projected_balance < 0 else PROJECTED_BALANCE_COLOR
        balance_text += (
            f" (<a href='{DELAYED_PAYMENTS_LINK}' style='color:{color}; text-decoration:none;'>"
            f"{app_core.projected_balance}</a>)"
        )

    balance_label = WindowsRegistry.MainWindow.account_current_balance
    balance_label.setText(balance_text)
    balance_label.setToolTip(LanguageStructure.DelayedPayments.get_translation(2) if has_future_expenses else "")

    # Settings totals represent the past only
    WindowsRegistry.SettingsWindow.total_income.setText(
        f"{LanguageStructure.Statistics.get_translation(4)}{round(app_core.current_total_income - future_totals.incomes, 2)}"
    )
    WindowsRegistry.SettingsWindow.total_expense.setText(
        f"{LanguageStructure.Statistics.get_translation(6)}{round(app_core.current_total_expenses - future_totals.expenses, 2)}"
    )


def show_delayed_payments(current_date:date|None = None) -> None:
    """Show the window with future expense transactions that explain the projected balance.

        Arguments
        ---------
            `current_date` : (date|None) - Date considered as today. Defaults to `date.today()`.
    """

    app_core = AppCore.instance()
    current_date = current_date or date.today()
    transactions = app_core.db.statistics_query.get_future_expense_transactions(current_date)

    table = WindowsRegistry.DelayedPaymentsWindow.transactions_table
    table.setRowCount(0)
    table.setRowCount(len(transactions))

    for row, transaction in enumerate(transactions):
        for column, text in enumerate((
            transaction.transaction_date.strftime(DISPLAY_DATE_FORMAT),
            transaction.category_name,
            transaction.name or "",
            str(transaction.value)
        )):
            item = CustomTableWidgetItem(text)
            item.setFlags(~ Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(ALIGNMENT.AlignCenter)
            table.setItem(row, column, item)

    total = round(sum(transaction.value for transaction in transactions), 2)
    WindowsRegistry.DelayedPaymentsWindow.total_label.setText(
        f"{LanguageStructure.DelayedPayments.get_translation(1)}{total}"
    )
    WindowsRegistry.DelayedPaymentsWindow.exec()

def calculate_current_balance() -> None:
    """Calculate current balance. It sums up all incomes and expenses and updates the account balance."""

    app_core = AppCore.instance()
    app_core.current_total_income = 0
    app_core.current_total_expenses = 0

    for category in app_core.db.category_query.get_all_categories():

        if category.category_type == CategoryType.Income:
            for transaction in app_core.db.transaction_query.get_all_transactions(category.id):
                app_core.current_total_income += transaction.value

        elif category.category_type == CategoryType.Expense:
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
    refresh_balance_label()


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

    refresh_balance_label()
    logger.info(f"Current balance: {app_core.current_balance}\
                | Total income: {app_core.current_total_income}\
                | Total expenses: {app_core.current_total_expenses}")


def update_account_balance() -> None:
    """Update account balance. It updates balance in database and GUI."""

    app_core = AppCore.instance()
    app_core.db.account_query.update_account_balance(app_core.current_balance, app_core.current_total_income, app_core.current_total_expenses)
    refresh_balance_label()