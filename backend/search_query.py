from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import and_
from datetime import date

from backend.models import Transaction

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session




class SearchQuery:
    """This class is used to manage search queries."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int

        self.values_operands = {
            "=": lambda field, value: field == value,
            "!=": lambda field, value: field != value,
            "<": lambda field, value: field < value,
            ">": lambda field, value: field > value,
            "<=": lambda field, value: field <= value,
            ">=": lambda field, value: field >= value,
        }
    

    def search_transactions(
            self,
            name_substring:str,
            value:float|None,
            value_operand:str,
            from_date:date,
            to_date:date,
            categories_id:list[int]
        ) -> list[Transaction]:
        """Search for transactions based on name, value, date range, and categories.

            Arguments
            ---------
                `name_substring` : (str) - Substring to search in transaction names.
                `value` : (float) - Value to search in transaction values.
                `value_operand` : (str) - Operand to use for value comparison.
                `from_date` : (date) - Start date of the date range.
                `to_date` : (date) - End date of the date range.
                `categories_id` : (list[int]) - List of category IDs to filter transactions.
        """
        filters = [
            Transaction.date.between(from_date, to_date),
            Transaction.category_id.in_(categories_id)
        ]

        if name_substring:
            filters.append(Transaction.name.ilike(f"%{name_substring}%"))
        
        if value:
            operand_func = self.values_operands[value_operand]
            filters.append(operand_func(Transaction.value, value))

        with self.session_factory() as session:
            with session.begin():
                query = session.query(Transaction).filter(*filters)
                return query.all()
