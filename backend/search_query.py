from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import func
from datetime import date

from backend.models import Transaction

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session
    from sqlalchemy.sql.elements import BinaryExpression, ColumnElement
    from typing import Any, Callable




class SearchQuery:
    """This class is used to manage search queries."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int

        self.values_operands: dict[str, Callable[[Any, Any], BinaryExpression[Any]]] = {
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

        order_by:list[ColumnElement[Any]] = []
        if value:
            operand_func = self.values_operands[value_operand]
            filters.append(operand_func(Transaction.value, value))
            if value_operand in (">=", ">"):
                order_by.append(Transaction.value.asc())
            elif value_operand in ("<=", "<", "!="):
                order_by.append(Transaction.value.desc())

        if name_substring:
            filters.append(Transaction.name.ilike(f"%{name_substring}%"))
            name_substring = name_substring.lower()
            order_by.extend([
                func.instr(func.lower(Transaction.name), name_substring),
                Transaction.name#type:ignore[list-item] #just name is valid here for ordering
            ])       

        with self.session_factory() as session:
            with session.begin():
                query = session.query(Transaction).filter(*filters).order_by(*order_by)
                return query.all()
