from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.sql import text
from backend.models import Account

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session



class AccountQuery:
    def __init__(self, session:sql_Session):
        self.session = session
        self.account_id:int = None
    

    def account_exists(self, name:str) -> bool:
        result = self.session.query(Account).filter(Account.name == name).first()
        return bool(result)


    def get_all_accounts(self) -> list[Account]:
        accounts = self.session.query(Account).all()
        return accounts


    def create_account(self, account_name:str, balance:float|int=0):
        self.session.add(Account(name=account_name, start_balance=balance))
        self.session.commit()


    def get_account(self) -> Account:
        return self.session.query(Account).filter_by(id=self.account_id).first()


    def update_account_balance(self, balance:float|int, total_income:int|float, total_expenses:int|float):
        self.session.query(Account).filter_by(id=self.account_id).update({
            Account.current_balance:balance,
            Account.current_total_income:total_income,
            Account.current_total_expenses:total_expenses
        }, False)
        self.session.commit()


    def rename_account(self, new_account_name:str):
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        account.name = new_account_name
        self.session.commit()
    

    def delete_account(self):
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        self.session.delete(account)
        self.session.commit()
        self.session.execute(text("VACUUM"))
        self.session.commit()
  