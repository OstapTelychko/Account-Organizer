from __future__ import annotations
from typing import TYPE_CHECKING
from backend.models import Transaction

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session

class TransactionQuery:
    def __init__(self, session:sql_Session):
        self.session = session
        self.account_id:int = None
    

    def delete_transaction(self, transaction_id:int):
        self.session.query(Transaction).filter_by(id=transaction_id).delete(False)
        self.session.commit()
            

    def update_transaction(self, transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int):
        self.session.query(Transaction).filter_by(id=transaction_id).update({
            Transaction.name:transaction_name,
            Transaction.day:transaction_day,
            Transaction.value:transaction_value
        }, False)
        self.session.commit()


    def add_transaction(self, category_id:int, year:int, month:int, day:int, value:int|float, name:str) -> Transaction :
        transaction = Transaction(year, month, day, value, name, category_id)
        self.session.add(transaction)
        self.session.commit()
        return transaction


    def get_transactions_by_month(self, category_id:int, year:int, month:int) -> list[Transaction]:
        return self.session.query(Transaction).filter_by(year=year, month=month, category_id=category_id).all()


    def get_all_transactions(self, category_id:int) -> list[Transaction]:
        return self.session.query(Transaction).filter_by(category_id=category_id).all()
    
 