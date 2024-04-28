# import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from AppObjects.transaction import Transaction
# from project_configuration import ROOT_DIRECTORY
from backend.models import Account, Category, Transaction


class DBController():

    def __init__(self, user_name:str):
        # Init db connection 
        engine = create_engine("sqlite:///Accounts.sqlite")
        self.session = sessionmaker(bind=engine)()
        # self.session = sqlite3.connect(f"{ROOT_DIRECTORY}/Accounts.sqlite") 
        # self.cursor = self.session.cursor()
        self.account_name = user_name


    #Account
    def account_exists(self, name:str) -> bool:
        result = self.session.query(Account).filter(Account.name == name).first()
        # result = self.cursor.execute("SELECT * FROM 'Accounts' WHERE account_name=?",(name,)).fetchone()
        return bool(result)


    def get_all_accounts(self) -> list[Account]:
        # with self.session:
        # accounts = self.cursor.execute("SELECT account_name FROM 'Accounts'").fetchall()
        accounts = self.session.query(Account).all()
        return accounts


    def set_account_id(self):
        # with self.session:
        self.account_id = self.session.query(Account).filter(Account.name == self.account_name).first().id


    def create_account(self, balance:float|int=0):
        # self.cursor.execute("INSERT INTO 'Accounts' ('account_name','current_balance','current_total_income','current_total_expenses','start_balance') VALUES(?,0,0,0,?)",(self.account_name, balance,))
        self.session.add(Account(name=self.account_name, start_balance=balance))
        self.session.commit()
        self.set_account_id()


    def get_account(self) -> Account:
        # with self.session:
            # date = self.cursor.execute("SELECT date FROM 'Accounts' WHERE id=?",(self.account_id,)).fetchone()[0]
            return self.session.query(Account).filter_by(id=self.account_id).first()


    # def get_account(self) -> list[int | float]:
    #     with self.session:
    #         current_balance = self.cursor.execute("SELECT current_balance FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]
    #         current_total_income = self.cursor.execute("SELECT current_total_income FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]
    #         current_total_expenses = self.cursor.execute("SELECT current_total_expenses FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]

    #         return current_balance, current_total_income, current_total_expenses


    # def get_account(self) -> int | float:
    #     with self.session:
    #         start_balance = self.cursor.execute("SELECT start_balance FROM 'Accounts' WHERE account_name=?", (self.account_name,)).fetchone()[0]

    #         return start_balance


    def update_account_balance(self, balance:float|int, total_income:int|float, total_expenses:int|float):
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        account.current_balance = balance
        account.current_total_income = total_income
        account.current_total_expenses = total_expenses
        self.session.commit()
        # with self.session:
            # self.cursor.execute("UPDATE 'Accounts' SET current_balance=?, current_total_income=?, current_total_expenses=? WHERE account_name=?",(balance, total_income, total_expenses,self.account_name,))



    def rename_account(self, new_account_name:str):
        # with self.session:
            # self.cursor.execute("UPDATE 'Accounts' SET account_name=? WHERE account_name = ?",(new_account_name, self.account_name,))
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        account.name = new_account_name
        self.session.commit()
        self.account_name = new_account_name
    

    def delete_account(self):
        # with self.session:
            # self.cursor.execute("DELETE  FROM 'Accounts' WHERE account_name=?",(self.account_name,))
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        self.session.delete(account)
        self.session.commit()
    


    #Category
    def category_exists(self, name:str, category_type:str) -> bool:
        # with self.session:
        #     result = self.cursor.execute("SELECT * FROM 'Categories' WHERE category_name=? AND category_type=? AND account_id=?",(category_name, category_type, self.account_id,)).fetchone()
        result = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return bool(result)


    def create_category(self, name:str, category_type:str, position:int):
        # with self.session:
            # self.cursor.execute("INSERT INTO 'Categories' (category_type, category_name, account_id, position) VALUES (?,?,?,?)",(category_type, catagory_name, self.account_id, position,))
        self.session.add(Category(name, category_type, position, self.account_id))
        self.session.commit()


    def get_last_category_position(self, category_type:str) -> int:
        # with self.session:
        #     result = self.cursor.execute("SELECT position FROM 'Categories' WHERE category_type=? AND account_id=? ORDER BY position DESC LIMIT 1",(category_type, self.account_id)).fetchone()
            
        #     if result is None:
        #         return 0
        last_category = self.session.query(Category).filter_by(category_type=category_type, account_id=self.account_id).order_by(Category.position).first()

        if last_category is None:
            return 0
        
        return last_category.position


    def change_category_position(self, position:int, category_id:int):
        # with self.session:
            # self.cursor.execute("UPDATE Categories SET position=? WHERE id=?", (position, category_id,))
        category = self.session.query(Category).filter_by(id=category_id).first()
        category.position = position
        self.session.commit()


    def get_category_id(self, name:str, category_type:str) -> int:
        # with self.session:
            # category_id = self.cursor.execute("SELECT id FROM 'Categories' WHERE category_name=? AND category_type=? AND account_id=?",(category_name, category_type, self.account_id,)).fetchone()[0]
        category = self.session.query(Category).filter_by(name=name, category_type=category_type, account_id=self.account_id).first()
        return category.id
    

    def get_all_categories(self) -> list[Category]:
        # with self.session:
        #     categories = self.cursor.execute("SELECT * FROM 'Categories' WHERE account_id=? ORDER BY position",(self.account_id,)).fetchall()
        return self.session.query(Category).filter_by(account_id=self.account_id).all()


    def rename_category(self, category_id:int, new_name:str):
        # with self.session:
        #     self.cursor.execute("UPDATE Categories SET category_name=? WHERE id=?",(new_name, category_id))
        category = self.session.query(Category).filter_by(id=category_id).first()
        category.name = new_name
        self.session.commit()


    def delete_category(self, category_id:int):
        # with self.session:
        #     self.cursor.execute("DELETE FROM 'Categories' WHERE id=?",(category_id,))
        self.session.delete(self.session.query(Category).filter_by(id=category_id).first())
        self.session.commit()



    #Transaction
    def delete_transaction(self, transaction_id:int):
        # with self.session:
        #     self.cursor.execute("DELETE  FROM 'Transactions' WHERE id=?",(transaction_id,))
        self.session.delete(self.session.query(Transaction).filter_by(id=transaction_id).first())
        self.session.commit()
            

    def update_transaction(self, transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int):
        # with self.session:
        #     self.cursor.execute("UPDATE Transactions SET name=?, day=?, value=? WHERE id=?",(transaction_name, transaction_day, transaction_value, transaction_id,))
        transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
        transaction.name = transaction_name
        transaction.day = transaction_day
        transaction.value = transaction_value
        self.session.commit()


    def add_transaction(self, category_id:int, year:int, month:int, day:int, value:int|float, name:str) -> Transaction :
        # with self.session:
        #     self.cursor.execute("INSERT INTO 'Transactions' (category_id, year, month, day, value, name) VALUES(?,?,?,?,?,?)",(category_id, year, month, day, value, name,))
        transaction = Transaction(year, month, day, value, name, category_id)
        self.session.add(transaction)
        self.session.commit()
        return transaction
    

    # def get_last_transaction_id(self) -> int:
    #     with self.session:
    #         id = self.cursor.execute("SELECT id FROM 'Transactions' ORDER BY id DESC").fetchone()[0]
    #         return id
    

    def get_transactions_by_month(self, category_id:int, year:int, month:int) -> list[Transaction]:
        # with self.session:
        #     # transactions = self.cursor.execute("SELECT * FROM 'Transactions' WHERE category_id=? AND year=? AND month=?",(category_id, year, month,)).fetchall()
            
        #     return [
        #         Transaction(
        #         id=transaction[0],
        #         year=transaction[2],
        #         month=transaction[3],
        #         day=transaction[4],
        #         value=transaction[5],
        #         name=transaction[6]
        #         )

        #         for transaction in transactions]
        return self.session.query(Transaction).filter_by(year=year, month=month, category_id=category_id).all()


    def get_all_transactions(self, category_id:int) -> list[Transaction]:

        # with self.session:
        #     transactions = self.cursor.execute("SELECT * FROM 'Transactions' WHERE category_id=?",(category_id,)).fetchall()

        #     return [
        #         Transaction(
        #         id=transaction[0],
        #         year=transaction[2],
        #         month=transaction[3],
        #         day=transaction[4],
        #         value=transaction[5],
        #         name=transaction[6]
        #         )
                
        #         for transaction in transactions]
        return self.session.query(Transaction).filter_by(category_id=category_id).all()
    
