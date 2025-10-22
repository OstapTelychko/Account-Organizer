from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date
from sqlalchemy import and_

from backend.models import Transaction
from GeneralTools.Utils import generate_month_range

if TYPE_CHECKING:
    from sqlalchemy.orm import sessionmaker, Session as sql_Session



class TransactionQuery:
    """This class is used to manage transactions and related data in the database."""

    def __init__(self, session_factory:sessionmaker[sql_Session]) -> None:
        self.session_factory = session_factory
        self.account_id:int
    

    def delete_transaction(self, transaction_id:int) -> None:
        """Delete a transaction from the database.

            Arguments
            ---------
                `transaction_id` : (int) - ID of the transaction to delete.
        """

        with self.session_factory() as session:
            with session.begin():
                session.query(Transaction).filter_by(id=transaction_id).delete(False)
            

    def update_transaction(self, transaction_id:int, transaction_name:str, day:int, transaction_value:float) -> None:
        """Update a transaction in the database.

            Arguments
            ---------
                `transaction_id` : (int) - ID of the transaction to update.
                `transaction_name` : (str) - New name of the transaction.
                `transaction_day` : (int) - New day of the transaction.
                `transaction_value` : (float) - New value of the transaction.
        """

        with self.session_factory() as session:
            with session.begin():
                transaction = session.get(Transaction, transaction_id)

                if not transaction:
                    raise ValueError(f"Transaction with ID {transaction_id} does not exist.")
                
                transaction.name = transaction_name
                transaction.date = date(transaction.date.year, transaction.date.month, day)
                transaction.value = transaction_value


    def add_transaction(self, category_id:int, date:date, value:float, name:str) -> Transaction:
        """Add a new transaction to the database.

            Arguments
            ---------
                `category_id` : (int) - ID of the category for the transaction.
                `date` : (date) - Date of the transaction.
                `value` : (float) - Value of the transaction.
                `name` : (str) - Name of the transaction.
        """

        with self.session_factory() as session:
            with session.begin():
                transaction = Transaction(date=date, value=value, name=name, category_id=category_id)
                session.add(transaction)
                return transaction


    def get_transactions_by_month(self, category_id:int, year:int, month:int) -> list[Transaction]:
        """Get transactions for a specific category in a given month and year.

            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions.
            Returns
            -------
                `list[Transaction]` - List of transactions for the specified category, month, and year.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(Transaction).filter(
                    and_(
                        Transaction.date.between(*generate_month_range(year, month)),
                        Transaction.category_id == category_id
                    )
                ).all()

    
    
    def check_categories_have_transactions(self, categories_id:list[int], year:int, month:int) -> bool:
        """Check if any of the specified categories have transactions in a given month and year.

            Arguments
            ---------
                `categories_id` : (list[int]) - List of category IDs to check.
                `year` : (int) - Year to filter transactions.
                `month` : (int) - Month to filter transactions."""

        with self.session_factory() as session:
            with session.begin():
                row = session.query(Transaction).filter(and_(
                    Transaction.date.between(*generate_month_range(year, month)),
                    Transaction.category_id.in_(categories_id)
                )).limit(1).first()
                return row is not None


    def get_all_transactions(self, category_id:int) -> list[Transaction]:
        """Get all transactions for a specific category.

            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
            Returns
            -------
                `list[Transaction]` - List of all transactions for the specified category.
        """

        with self.session_factory() as session:
            with session.begin():
                return session.query(Transaction).filter_by(category_id=category_id).all()
    
 