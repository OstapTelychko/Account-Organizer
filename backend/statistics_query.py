from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple
from sqlalchemy.sql import func as sql_func
from sqlalchemy import and_, extract
from datetime import date

from backend.models import Transaction, Category
from GeneralTools.Utils import generate_month_range
from project_configuration import CategoryType

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session
    from sqlalchemy.engine import Row
    from typing import Sequence



class FutureTotals(NamedTuple):
    """Sums of income and expense transactions dated after a given date."""

    incomes: float
    expenses: float


class FutureExpenseTransaction(NamedTuple):
    """Expense transaction dated after a given date, shown in the delayed payments window."""

    transaction_date: date
    category_name: str
    name: str | None
    value: float



class StatisticsQuery:
    """This class is used to create statistics."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int


    def get_future_totals(self, current_date:date, account_id:int|None = None) -> FutureTotals:
        """Get the sums of income and expense transactions dated after the given date.

            Arguments
            ---------
                `current_date` : (date) - Transactions dated after this date are future transactions.
                `account_id` : (int|None) - Account to calculate totals for. Defaults to the current account.
            Returns
            -------
                `FutureTotals` - Future incomes and expenses sums.
        """

        target_account_id = self.account_id if account_id is None else account_id
        with self.session_factory() as session:
            with session.begin():
                sums:Sequence[Row[tuple[str, float]]] = session.query(
                    Category.category_type,
                    sql_func.coalesce(sql_func.sum(Transaction.value), 0)
                ).join(Category, Transaction.category_id == Category.id).filter(and_(
                    Transaction.date > current_date,
                    Category.account_id == target_account_id
                )).group_by(Category.category_type).all()

        totals = {category_type: float(total) for category_type, total in sums}
        return FutureTotals(
            incomes=round(totals.get(CategoryType.Income, 0.0), 2),
            expenses=round(totals.get(CategoryType.Expense, 0.0), 2)
        )


    def get_future_expense_transactions(self, current_date:date) -> list[FutureExpenseTransaction]:
        """Get expense transactions of the current account dated after the given date.

            Arguments
            ---------
                `current_date` : (date) - Transactions dated after this date are future transactions.
            Returns
            -------
                `list[FutureExpenseTransaction]` - Transactions ordered by date.
        """

        with self.session_factory() as session:
            with session.begin():
                rows:Sequence[Row[tuple[date, str, str|None, float]]] = session.query(
                    Transaction.date, Category.name, Transaction.name, Transaction.value
                ).join(Category, Transaction.category_id == Category.id).filter(and_(
                    Transaction.date > current_date,
                    Category.account_id == self.account_id,
                    Category.category_type == CategoryType.Expense
                )).order_by(Transaction.date, Transaction.id).all()

        return [
            FutureExpenseTransaction(transaction_date=row[0], category_name=row[1], name=row[2], value=row[3])
            for row in rows
        ]
    

    def get_monthly_transactions_sum(self, category_id:int, year:int, month:int) -> float:
        """Get the sum of transactions for a specific category in a given month and year.
        
            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions.
            Returns
            -------
                `float` - Total sum of transactions for the specified category, month, and year.
        """

        with self.session_factory() as session:
            with session.begin():
                total = session.query(sql_func.sum(Transaction.value)).filter(and_(
                    Transaction.date.between(*generate_month_range(year, month)),
                    Transaction.category_id==category_id
                )).scalar()
                return float(total) if total else 0
    

    def get_categories_monthly_transactions_sum(self, categories_id: list[int], year:int, month:int) -> list[float]:
        """Get the sum of transactions for multiple categories in a given month and year.
        
            Arguments
            ---------
                `categories` : (list[int]) - List of category IDs to filter transactions.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions.
            Returns
            -------
                `list[float]` - List of total sums of transactions for each specified category, month and year.
        """

        with self.session_factory() as session:
            with session.begin():
                sums:Sequence[Row[tuple[int, float]]] = session.query(Transaction.category_id, sql_func.sum(Transaction.value)).filter(
                    Transaction.date.between(*generate_month_range(year, month)),
                    Transaction.category_id.in_(categories_id)
                ).group_by(Transaction.category_id).all()

                result = [0.0] * len(categories_id)
                for index, category_id in enumerate(categories_id):
                    for s in sums:
                        if s[0] == category_id:
                            result[index] = float(s[1]) if s[1] else 0.0
                return result


    def get_categories_monthly_transactions_sum_by_months(self, categories_id: list[int], year:int, months: list[int]) -> dict[int, list[float]]:
        """Get the sum of transactions for multiple categories over multiple months in a given year.
        
            Arguments
            ---------
                `categories` : (list[int]) - List of category IDs to filter transactions.
                `year` : (int) - Year to filter transactions.
                `months` : (list[int]) - List of months to filter transactions.
            Returns
            -------
                `dict[int, list[float]]` - Dictionary where keys are categories id and values are lists of total sums of transactions for each month.
        """

        with self.session_factory() as session:
            with session.begin():
                sums:Sequence[Row[tuple[int, int, float]]] = session.query(
                    Transaction.category_id,
                    extract('month', Transaction.date),
                    sql_func.sum(Transaction.value)).filter(and_(
                        extract('year', Transaction.date) == year,
                        extract('month', Transaction.date).in_(months),
                        Transaction.category_id.in_(categories_id))
                    ).group_by(Transaction.category_id, extract('month', Transaction.date)).all()

                result:dict[int, list[float]] = {}
                for category_id in categories_id:
                    result[category_id] = [0.0]
                    for s in sums:
                        if s[0] == category_id:
                            result[category_id].append(float(s[2]) if s[2] else 0)

                return result


    def get_monthly_transactions_min_value(self, category_id:int, year:int, month:int) -> float:
        """Get the minimum transaction value for a specific category in a given month and year.
        
            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions.
            Returns
            -------
                `float` - Minimum transaction value for the specified category, month, and year.
        """

        with self.session_factory() as session:
            with session.begin():
                min_value = session.query(sql_func.min(Transaction.value)).filter(and_(
                    Transaction.date.between(*generate_month_range(year, month)),
                    Transaction.category_id==category_id
                )).scalar()
                return float(min_value) if min_value else 0
    

    def get_monthly_transactions_max_value(self, category_id:int, year:int, month:int) -> float:
        """Get the maximum transaction value for a specific category in a given month and year.
        
            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions.
            Returns
            -------
                `float` - Maximum transaction value for the specified category, month, and year.
        """

        with self.session_factory() as session:
            with session.begin():
                max_value = session.query(sql_func.max(Transaction.value)).filter(and_(
                    Transaction.date.between(*generate_month_range(year, month)),
                    Transaction.category_id==category_id
                )).scalar()
                return float(max_value) if max_value else 0
    

    def get_monthly_transactions_by_value(self, category_id:int, year:int, month:int, value:float|int) -> list[Transaction]:
        """Get transactions for a specific category in a given month and year with a specific value.
        
            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions.
                `value` : (float|int) - Value to filter transactions.
            Returns
            -------
                `list[Transaction]` - List of transactions for the specified category, month, year, and value.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(Transaction).filter(and_(
                    Transaction.date.between(*generate_month_range(year, month)),
                    Transaction.value==value,
                    Transaction.category_id==category_id)
                ).all()


    def get_transactions_by_range(self, category_ids:list[int], from_date:date, to_date:date) -> list[Transaction]:
        """Get transactions for specific categories within a date range.
        
            Arguments
            ---------
                `category_ids` : (list[int]) - List of category IDs to filter transactions.
                `from_date` : (date) - Start date.
                `to_date` : (date) - End date.
            Returns
            -------
                `list[Transaction]` - List of transactions for the specified categories and date range.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(Transaction).filter(and_(
                    Transaction.category_id.in_(category_ids),
                    Transaction.date.between(from_date, to_date)
                )).all()
