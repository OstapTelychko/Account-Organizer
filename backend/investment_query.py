from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
from datetime import date
from math import inf

from project_configuration import InvestmentOperation

if TYPE_CHECKING:
    from collections.abc import Iterable
    from backend.models import Transaction
    from backend.transaction_query import TransactionQuery



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
    """This class is used to calculate values of Investments categories from their operations.
    Later operations don't change earlier timeline points, so the timeline of all operations is cut by date.
    """

    def __init__(self, transaction_query:TransactionQuery) -> None:
        self.transaction_query = transaction_query


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

        values:dict[int, float] = {}
        for category_id in categories_ids:
            points = [
                point for point in calculate_investment_timeline(
                    self.transaction_query.get_all_transactions(category_id)
                ) if point.date <= as_of
            ]
            values[category_id] = points[-1].value_after if points else 0.0
        return values


    def deposit_exists(self, categories_ids:list[int], period_start:date, period_end:date) -> bool:
        """Check if any of the Investments categories has a deposit in the period.

            Arguments
            ---------
                `categories_ids` : (list[int]) - IDs of Investments categories.
                `period_start` : (date) - First day of the period.
                `period_end` : (date) - Last day of the period.
            Returns
            -------
                `bool` - True if a deposit exists, False otherwise.
        """

        return any(
            transaction.operation_type == InvestmentOperation.Deposit
            and period_start <= transaction.date <= period_end
            for category_id in categories_ids
            for transaction in self.transaction_query.get_all_transactions(category_id)
        )


    def all_investments_revalued(self, categories_ids:list[int], period_start:date, period_end:date) -> bool:
        """Check if every Investments category that had value at the start of the period was revaluated in it.

            Arguments
            ---------
                `categories_ids` : (list[int]) - IDs of Investments categories.
                `period_start` : (date) - First day of the period.
                `period_end` : (date) - Last day of the period.
            Returns
            -------
                `bool` - True if all such categories were revaluated, False otherwise.
        """

        for category_id in categories_ids:
            timeline = calculate_investment_timeline(self.transaction_query.get_all_transactions(category_id))
            start_points = [point for point in timeline if point.date < period_start]
            if not start_points or start_points[-1].value_after <= 0:
                continue

            if not any(
                point.operation_type == InvestmentOperation.Revaluation
                and period_start <= point.date <= period_end
                for point in timeline
            ):
                return False
        return True


    def get_total_investments_value(self, categories_ids:list[int], as_of:date) -> float | None:
        """Get the summed value of Investments categories.

            Arguments
            ---------
                `categories_ids` : (list[int]) - IDs of Investments categories.
                `as_of` : (date) - Date to calculate the value for.
            Returns
            -------
                `float | None` - Total value or `None` if there are no Investments categories.
        """

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
        for category_id in categories_ids:
            for point in calculate_investment_timeline(self.transaction_query.get_all_transactions(category_id)):
                if not start_date <= point.date <= end_date:
                    continue
                if point.operation_type == InvestmentOperation.Deposit:
                    deposits += point.value
                elif point.operation_type == InvestmentOperation.Withdrawal:
                    withdrawals += point.value
                elif point.operation_type == InvestmentOperation.Revaluation:
                    value_change += point.value_change

        return InvestmentTotals(round(deposits, 2), round(withdrawals, 2), round(value_change, 2))
