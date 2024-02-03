import sqlite3
from project_configuration import ROOT_DIRECTORY


class Account():

    def __init__(self, user_name:str):
        self.connection = sqlite3.connect(f"{ROOT_DIRECTORY}/Accounts.sqlite") 
        self.cursor = self.connection.cursor()
        self.account_name = user_name


    def account_exists(self, name:str) -> bool:
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'Accounts' WHERE account_name=?",(name,)).fetchone()
            return bool(result)


    def get_all_accounts(self) -> list:
        with self.connection:
            accounts = self.cursor.execute("SELECT account_name FROM 'Accounts'").fetchall()
            return accounts


    def set_account_id(self):
        "Set account id"
        with self.connection:
            id = self.cursor.execute("SELECT id FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]
            self.account_id = id


    def create_account(self, balance:float|int=0):
        with self.connection:
            self.cursor.execute("INSERT INTO 'Accounts' ('account_name','current_balance','current_total_income','current_total_expenses') VALUES(?,?,0,0)",(self.account_name, balance,))
            self.set_account_id()


    def get_account_date(self)-> str:
        with self.connection:
            date = self.cursor.execute("SELECT date FROM 'Accounts' WHERE id=?",(self.account_id,)).fetchone()[0]
            return date


    def get_account_balance(self) -> list[int | float]:
        with self.connection:
            current_balance = self.cursor.execute("SELECT current_balance FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]
            current_total_income = self.cursor.execute("SELECT current_total_income FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]
            current_total_expenses = self.cursor.execute("SELECT current_total_expenses FROM 'Accounts' WHERE account_name=?",(self.account_name,)).fetchone()[0]

            return current_balance, current_total_income, current_total_expenses


    def update_account_balance(self, balance:float|int, total_income:int|float, total_expenses:int|float):
        with self.connection:
            self.cursor.execute("UPDATE 'Accounts' SET current_balance=?, current_total_income=?, current_total_expenses=? WHERE account_name=?",(balance, total_income, total_expenses,self.account_name,))


    def rename_account(self, new_account_name:str):
        with self.connection:
            self.cursor.execute("UPDATE 'Accounts' SET account_name=? WHERE account_name = ?",(new_account_name, self.account_name,))
            self.account_name = new_account_name
    

    def delete_account(self):
        with self.connection:
            self.cursor.execute("DELETE  FROM 'Accounts' WHERE account_name=?",(self.account_name,))
    

    def category_exists(self, category_name:str, category_type:str) -> bool:
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'Categories' WHERE category_name=? AND category_type=? AND account_id=?",(category_name, category_type, self.account_id,)).fetchone()
            return bool(result)


    def create_category(self, catagory_name:str, category_type:str):
        with self.connection:
            self.cursor.execute("INSERT INTO 'Categories' (category_type, category_name, account_id) VALUES (?,?,?)",(category_type, catagory_name, self.account_id,))
    

    def get_category_id(self, catagory_name:str, category_type:str) -> int:
        with self.connection:
            category_id = self.cursor.execute("SELECT id FROM 'Categories' WHERE category_name=? AND category_type=? AND account_id=?",(catagory_name, category_type, self.account_id,)).fetchone()[0]
            return category_id
    

    def get_all_categories(self) -> list:
        with self.connection:
            categories = self.cursor.execute("SELECT * FROM 'Categories' WHERE account_id=?",(self.account_id,)).fetchall()
            return categories


    def rename_category(self, category_id:int, new_name:str):
        with self.connection:
            self.cursor.execute("UPDATE Categories SET category_name=? WHERE id=?",(new_name, category_id))


    def delete_category(self, category_id:int):
        with self.connection:
            self.cursor.execute("DELETE FROM 'Categories' WHERE id=?",(category_id,))


    def delete_transaction(self, transaction_id:int):
        with self.connection:
            self.cursor.execute("DELETE  FROM 'Transactions' WHERE id=?",(transaction_id,))
            

    def update_transaction(self, transaction_id:int, transaction_name:str, transaction_day:int, transaction_value:int):
        with self.connection:
            self.cursor.execute("UPDATE Transactions SET name=?, day=?, value=? WHERE id=?",(transaction_name, transaction_day, transaction_value, transaction_id,))


    def add_transaction(self,category_id:int, year:int, month:int, day:int, value:int|float, name:str):
        with self.connection:
            self.cursor.execute("INSERT INTO 'Transactions' (category_id, year, month, day, value, name) VALUES(?,?,?,?,?,?)",(category_id, year, month, day, value, name,))
    

    def get_last_transaction_id(self) -> int:
        with self.connection:
            id = self.cursor.execute("SELECT id FROM 'Transactions' ORDER BY id DESC").fetchone()[0]
            return id
    
    def get_transactions_by_month(self, category_id:int, year:int, month:int) -> list:
        with self.connection:
            transactions = self.cursor.execute("SELECT * FROM 'Transactions' WHERE category_id=? AND year=? AND month=?",(category_id, year, month,)).fetchall()
            return transactions
        
    def get_all_transactions(self, category_id:int) -> list:

        with self.connection:
            transactions = self.cursor.execute("SELECT * FROM 'Transactions' WHERE category_id=?",(category_id,)).fetchall()
            return transactions
    


    

# account = Account("Accounts.sqlite","Hranutel3")
# # account.create_account()
# # account.create_category("Products","expenses")
# account.account_id = account.get_account_id()
# category_id = account.get_category_id("Products","expenses")
# account.create_transaction(category_id,2023,4,18,100,"Ковбаса")
# print(account.account_exists())
