from sqlalchemy.orm import Session as sql_Session
from sqlalchemy.sql import func as sql_func
from sqlalchemy import and_

from backend.models import Transaction




class StatisticsQuery:
    def __init__(self, session:sql_Session):
        self.session = session
        self.account_id:int = None
    

    def get_monthly_transactions_sum(self, category_id:int, year:int, month:int) -> float:
        total = self.session.query(sql_func.sum(Transaction.value)).filter_by(category_id=category_id, year=year, month=month).scalar()
        return float(total) if total else 0
    

    def get_monthly_transactions_min_value(self, category_id:int, year:int, month:int) -> float:
        min_value = self.session.query(sql_func.min(Transaction.value)).filter_by(category_id=category_id, year=year, month=month).scalar()
        return float(min_value) if min_value else 0
    

    def get_monthly_transactions_max_value(self, category_id:int, year:int, month:int) -> float:
        max_value = self.session.query(sql_func.max(Transaction.value)).filter_by(category_id=category_id, year=year, month=month).scalar()
        return float(max_value) if max_value else 0
    

    def get_monthly_transactions_by_value(self, category_id:int, year:int, month:int, value:float|int) -> list[Transaction]:
        return self.session.query(Transaction).filter_by(category_id=category_id, year=year, month=month, value=value).all()
    

    def get_transaction_by_range(self, category_id:int, from_date:int, to_date:int) -> list[Transaction]:
        return self.session.query(Transaction).filter(and_(
            Transaction.year*1000 + Transaction.month*100 + Transaction.day >= from_date,
            Transaction.year*1000 + Transaction.month*100 + Transaction.day <= to_date,
            Transaction.category_id == category_id
        )).all()
