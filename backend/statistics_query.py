from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.sql import func as sql_func
from sqlalchemy import and_

from backend.models import Transaction

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session



class StatisticsQuery:
    """This class is used to create statistics."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int
    

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
                total = session.query(sql_func.sum(Transaction.value)).filter_by(
                    category_id=category_id, year=year, month=month
                ).scalar()
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
                `list[float]` - List of total sums of transactions for each specified category, month, and year.
        """

        with self.session_factory() as session:
            with session.begin():
                sums = session.query(Transaction.category_id, Transaction.month, sql_func.sum(Transaction.value)).filter(
                    Transaction.year == year,
                    Transaction.month == month,
                    Transaction.category_id.in_(categories_id)
                ).group_by(Transaction.category_id).all()

                result = [0.0] * len(categories_id)
                for index, category_id in enumerate(categories_id):
                    for s in sums:
                        if s[0] == category_id:
                            result[index] = float(s[2]) if s[2] else 0.0
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
                sums = session.query(Transaction.category_id, Transaction.month, sql_func.sum(Transaction.value)).filter(
                    Transaction.year == year,
                    Transaction.month.in_(months),
                    Transaction.category_id.in_(categories_id)
                ).group_by(Transaction.category_id, Transaction.month).all()

                result = {}
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
                min_value = session.query(sql_func.min(Transaction.value)).filter_by(
                    category_id=category_id, year=year, month=month
                ).scalar()
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
                max_value = session.query(sql_func.max(Transaction.value)).filter_by(
                    category_id=category_id, year=year, month=month
                ).scalar()
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
                return session.query(Transaction).filter_by(category_id=category_id, year=year, month=month, value=value).all()
    

    def get_transactions_by_range(self, category_ids:list[int], from_date:int, to_date:int) -> list[Transaction]:
        """Get transactions for specific categories within a date range.
        
            Arguments
            ---------
                `category_ids` : (list[int]) - List of category IDs to filter transactions.
                `from_date` : (int) - Start date in YYYYMMDD format.
                `to_date` : (int) - End date in YYYYMMDD format.
            Returns
            -------
                `list[Transaction]` - List of transactions for the specified categories and date range.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(Transaction).filter(and_(
                    Transaction.category_id.in_(category_ids),
                    Transaction.year*1000 + Transaction.month*100 + Transaction.day >= from_date,
                    Transaction.year*1000 + Transaction.month*100 + Transaction.day <= to_date,)).all()
