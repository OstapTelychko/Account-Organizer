# import sqlite3
from sqlalchemy import create_engine, desc, and_
from sqlalchemy.orm import sessionmaker
from datetime import date

from project_configuration import ROOT_DIRECTORY
from .models import Account, Category, Transaction


class DBController():

    def __init__(self, user_name:str):
        # Init db connection 
        engine = create_engine(f"sqlite:///{ROOT_DIRECTORY}/Accounts.sqlite")
        self.session = sessionmaker(bind=engine)()
        self.account_name = user_name


    #Account
    def account_exists(self, name:str) -> bool:
        result = self.session.query(Account).filter(Account.name == name).first()
        return bool(result)


    def get_all_accounts(self) -> list[Account]:
        accounts = self.session.query(Account).all()
        return accounts


    def set_account_id(self):
        self.account_id = self.session.query(Account).filter(Account.name == self.account_name).first().id


    def create_account(self, balance:float|int=0):
        self.session.add(Account(name=self.account_name, start_balance=balance))
        self.session.commit()
        self.set_account_id()


    def get_account(self) -> Account:
            return self.session.query(Account).filter_by(id=self.account_id).first()


    def update_account_balance(self, balance:float|int, total_income:int|float, total_expenses:int|float):
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        account.current_balance = balance
        account.current_total_income = total_income
        account.current_total_expenses = total_expenses
        self.session.commit()


    def rename_account(self, new_account_name:str):
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        account.name = new_account_name
        self.session.commit()
        self.account_name = new_account_name
    

    def delete_account(self):
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        self.session.delete(account)
        self.session.commit()
    


    #Category
    def category_exists(self, name:str, category_type:str) -> bool:
        result = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return bool(result)


    def create_category(self, name:str, category_type:str, position:int):
        self.session.add(Category(name, category_type, position, self.account_id))
        self.session.commit()


    def get_available_position(self, category_type:str) -> int:
        last_category = self.session.query(Category).filter_by(category_type=category_type, account_id=self.account_id).order_by(desc(Category.position)).first()

        if last_category is None:
            return 0
        
        return last_category.position + 1


    def change_category_position(self, new_position:int, old_position:int, category_id:int):
        if new_position < old_position:
            self.session.query(Category).filter(and_(Category.position < old_position, Category.position >= new_position)).update(
                {Category.position: Category.position + 1}, synchronize_session=False
            )
        else:
            self.session.query(Category).filter(and_(Category.position > old_position, Category.position <= new_position)).update(
                {Category.position: Category.position - 1}, synchronize_session=False
            )
        self.session.query(Category).filter_by(id=category_id).update({Category.position: new_position}, synchronize_session=False)
        self.session.commit()


    def remove_position(self, category_id:int):
        position = self.session.query(Category).filter_by(id=category_id).first().position
        self.session.query(Category).filter(Category.position > position).update(
            {Category.position: Category.position - 1}, synchronize_session=False
        )
        self.session.commit()


    def get_category(self, name:str, category_type:str) -> Category:
        category = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return category
    

    def get_all_categories(self) -> list[Category]:
        return self.session.query(Category).filter_by(account_id=self.account_id).order_by(Category.position).all()


    def rename_category(self, category_id:int, new_name:str):
        category = self.session.query(Category).filter_by(id=category_id).first()
        category.name = new_name
        self.session.commit()


    def delete_category(self, category_id:int):
        self.remove_position(category_id)
        self.session.delete(self.session.query(Category).filter_by(id=category_id).first())
        self.session.commit()



    #Transaction
    def delete_transaction(self, transaction_id:int):
        self.session.delete(self.session.query(Transaction).filter_by(id=transaction_id).first())
        self.session.commit()
            

    def update_transaction(self, transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int):
        transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
        transaction.name = transaction_name
        transaction.day = transaction_day
        transaction.value = transaction_value
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
    

    def get_transaction_by_range(self, category_id:int, from_date:int, to_date:int) -> list[Transaction]:
        return self.session.query(Transaction).filter(and_(
            Transaction.year*1000 + Transaction.month*100 + Transaction.day >= from_date,
            Transaction.year*1000 + Transaction.month*100 + Transaction.day <= to_date,
            Transaction.category_id == category_id
        )).all()