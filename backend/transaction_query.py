from __future__ import annotations
from typing import TYPE_CHECKING
from backend.models import Transaction

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session



class TransactionQuery:
    """This class is used to manage transactions and related data in the database."""

    def __init__(self, session:sql_Session):
        self.session = session
        self.account_id:int = None
    

    def delete_transaction(self, transaction_id:int):
        """Delete a transaction from the database.

            Arguments
            ---------
                `transaction_id` : (int) - ID of the transaction to delete.
        """

        self.session.query(Transaction).filter_by(id=transaction_id).delete(False)
        self.session.commit()
            

    def update_transaction(self, transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int):
        """Update a transaction in the database.

            Arguments
            ---------
                `transaction_id` : (int) - ID of the transaction to update.
                `transaction_name` : (str) - New name of the transaction.
                `transaction_day` : (int) - New day of the transaction.
                `transaction_value` : (int|float) - New value of the transaction.
        """

        self.session.query(Transaction).filter_by(id=transaction_id).update({
            Transaction.name:transaction_name,
            Transaction.day:transaction_day,
            Transaction.value:transaction_value
        }, False)
        self.session.commit()


    def add_transaction(self, category_id:int, year:int, month:int, day:int, value:int|float, name:str) -> Transaction:
        """Add a new transaction to the database.

            Arguments
            ---------
                `category_id` : (int) - ID of the category for the transaction.
                `year` : (int) - Year of the transaction.
                `month` : (int) - Month of the transaction.
                `day` : (int) - Day of the transaction.
                `value` : (int|float) - Value of the transaction.
                `name` : (str) - Name of the transaction.
        """

        transaction = Transaction(year, month, day, value, name, category_id)
        self.session.add(transaction)
        self.session.commit()
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

        return self.session.query(Transaction).filter_by(year=year, month=month, category_id=category_id).all()


    def get_all_transactions(self, category_id:int) -> list[Transaction]:
        """Get all transactions for a specific category.

            Arguments
            ---------
                `category_id` : (int) - ID of the category to filter transactions.
            Returns
            -------
                `list[Transaction]` - List of all transactions for the specified category.
        """

        return self.session.query(Transaction).filter_by(category_id=category_id).all()
    
 