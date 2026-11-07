from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
from collections import defaultdict
from datetime import date
from math import inf

from backend.models import Transaction, Category
from project_configuration import CategoryType, InvestmentOperation

if TYPE_CHECKING:
    from collections.abc import Iterable
    from sqlalchemy.orm import sessionmaker, Session as sql_Session



class InvestmentTimelinePoint(NamedTuple):
    """State of an Investments category right after one of its operations."""

    transaction_id: int | None
    date: date
    operation_type: int
    value: float
    value_after: float
    value_change: float


class InvestmentTotals(NamedTuple):
    """Sums of Investments operations in a period. `value_change` is the market change from revaluations."""

    deposits: float
    withdrawals: float
    value_change: float


def calculate_investment_timeline(transactions:Iterable[Transaction]) -> list[InvestmentTimelinePoint]:
    """Calculate the value of one Investments category after each of its operations.
    On the same date deposits and withdrawals are applied before revaluations.

        Arguments
        ---------
            `transactions` : (Iterable[Transaction]) - All operations of one Investments category.
                Transactions that aren't saved yet (without ID) are applied after saved ones of the same date and type.
        Returns
        -------
            `list[InvestmentTimelinePoint]` - Points in chronological order.
    """

    ordered_transactions = sorted(transactions, key=lambda transaction: (
        transaction.date,
        transaction.operation_type == InvestmentOperation.Revaluation,
        inf if transaction.id is None else transaction.id
    ))

    timeline:list[InvestmentTimelinePoint] = []
    value = 0.0
    for transaction in ordered_transactions:
        if transaction.operation_type == InvestmentOperation.Revaluation:
            value_change = round(transaction.value - value, 2)
        elif transaction.operation_type == InvestmentOperation.Withdrawal:
            value_change = -transaction.value
        else:
            value_change = transaction.value

        value = round(value + value_change, 2)
        timeline.append(InvestmentTimelinePoint(
            transaction.id, transaction.date, transaction.operation_type, transaction.value, value, value_change
        ))
    return timeline



class InvestmentQuery:
    """This class is used to calculate values of Investments categories."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int


    def get_categories_transactions(
            self, categories_ids:Iterable[int], end_date:date|None = None
        ) -> defaultdict[int, list[Transaction]]:
        """Get operations of Investments categories grouped by category.

            Arguments
            ---------
                `categories_ids` : (Iterable[int]) - IDs of Investments categories.
                `end_date` : (date|None) - Include only operations dated on or before this date. Defaults to all.
            Returns
            -------
                `defaultdict[int, list[Transaction]]` - Operations of each category.
        """

        with self.session_factory() as session:
            with session.begin():
                query = session.query(Transaction).filter(Transaction.category_id.in_(list(categories_ids)))
                if end_date is not None:
                    query = query.filter(Transaction.date <= end_date)
                transactions = query.all()

        categories_transactions:defaultdict[int, list[Transaction]] = defaultdict(list)
        for transaction in transactions:
            categories_transactions[transaction.category_id].append(transaction)
        return categories_transactions


    def get_categories_values(self, categories_ids:list[int], as_of:date) -> dict[int, float]:
        """Get the value of each Investments category at the end of the given date.

            Arguments
            ---------
                `categories_ids` : (list[int]) - IDs of Investments categories.
                `as_of` : (date) - Date to calculate values for.
            Returns
            -------
                `dict[int, float]` - Value of each category.
        """

        categories_transactions = self.get_categories_transactions(categories_ids, as_of)
        values:dict[int, float] = {}
        for category_id in categories_ids:
            timeline = calculate_investment_timeline(categories_transactions[category_id])
            values[category_id] = timeline[-1].value_after if timeline else 0.0
        return values


    def get_investment_categories_ids(self, account_id:int|None = None) -> list[int]:
        """Get IDs of Investments categories of an account.

            Arguments
            ---------
                `account_id` : (int|None) - Account to get categories of. Defaults to the current account.
            Returns
            -------
                `list[int]` - IDs of Investments categories.
        """

        target_account_id = self.account_id if account_id is None else account_id
        with self.session_factory() as session:
            with session.begin():
                return [category_id for (category_id,) in session.query(Category.id).filter(
                    Category.account_id == target_account_id,
                    Category.category_type == CategoryType.Investment
                ).all()]


    def deposit_exists(self, period_start:date, period_end:date) -> bool:
        """Check if any Investments category of the current account has a deposit in the period.

            Arguments
            ---------
                `period_start` : (date) - First day of the period.
                `period_end` : (date) - Last day of the period.
            Returns
            -------
                `bool` - True if a deposit exists, False otherwise.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(Transaction.id).join(Category).filter(
                    Category.account_id == self.account_id,
                    Category.category_type == CategoryType.Investment,
                    Transaction.operation_type == InvestmentOperation.Deposit,
                    Transaction.date.between(period_start, period_end)
                ).first() is not None


    def all_investments_revalued(self, period_start:date, period_end:date) -> bool:
        """Check if every Investments category that had value at the start of the period was revaluated in it.

            Arguments
            ---------
                `period_start` : (date) - First day of the period.
                `period_end` : (date) - Last day of the period.
            Returns
            -------
                `bool` - True if all such categories were revaluated, False otherwise.
        """

        categories_ids = self.get_investment_categories_ids()
        for category_id, transactions in self.get_categories_transactions(categories_ids, period_end).items():
            timeline = calculate_investment_timeline(transactions)
            start_points = [point for point in timeline if point.date < period_start]
            if not start_points or start_points[-1].value_after <= 0:
                continue

            if not any(
                point.operation_type == InvestmentOperation.Revaluation and point.date >= period_start
                for point in timeline
            ):
                return False
        return True


    def get_total_investments_value(self, as_of:date, account_id:int|None = None) -> float | None:
        """Get the summed value of all Investments categories of an account.

            Arguments
            ---------
                `as_of` : (date) - Date to calculate the value for.
                `account_id` : (int|None) - Account to calculate the value for. Defaults to the current account.
            Returns
            -------
                `float | None` - Total value or `None` if the account has no Investments categories.
        """

        categories_ids = self.get_investment_categories_ids(account_id)
        if not categories_ids:
            return None
        return round(sum(self.get_categories_values(categories_ids, as_of).values()), 2)


    def get_investment_totals(self, categories_ids:list[int], start_date:date, end_date:date) -> InvestmentTotals:
        """Get sums of deposits, withdrawals and value changes of Investments categories in a period.

            Arguments
            ---------
                `categories_ids` : (list[int]) - IDs of Investments categories.
                `start_date` : (date) - First day of the period.
                `end_date` : (date) - Last day of the period.
            Returns
            -------
                `InvestmentTotals` - Sums of the period.
        """

        deposits = withdrawals = value_change = 0.0
        for transactions in self.get_categories_transactions(categories_ids, end_date).values():
            for point in calculate_investment_timeline(transactions):
                if point.date < start_date:
                    continue
                if point.operation_type == InvestmentOperation.Deposit:
                    deposits += point.value
                elif point.operation_type == InvestmentOperation.Withdrawal:
                    withdrawals += point.value
                elif point.operation_type == InvestmentOperation.Revaluation:
                    value_change += point.value_change

        return InvestmentTotals(round(deposits, 2), round(withdrawals, 2), round(value_change, 2))
