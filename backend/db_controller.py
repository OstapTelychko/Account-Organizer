import logging
import os
from sqlite3 import connect as sql_connect
from sqlalchemy import create_engine, desc, and_, event, text, Engine
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime import migration
from alembic import command

from project_configuration import DB_PATH, TEST_DB_PATH, APP_DIRECTORY
from .models import Account, Category, Transaction



class DBController():

    def __init__(self):
        # Init db connection 
        from AppObjects.session import Session

        self.alembic_config = Config(f"{APP_DIRECTORY}/alembic.ini")
        self.alembic_config.set_main_option("script_location", f"{APP_DIRECTORY}/alembic")
        self.alembic_config.set_main_option("sqlalchemy.url", DB_PATH)

        if Session.test_mode:
            self.engine = create_engine(TEST_DB_PATH)
            self.alembic_config = Session.test_alembic_config
        else:
            self.engine = create_engine(DB_PATH)

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=OFF")
            cursor.close()

        if not self.db_up_to_date(self.alembic_config, self.engine):
            print("Upgrading database")
            command.upgrade(self.alembic_config, "head")

        self.session = sessionmaker(bind=self.engine)()
        self.account_id = None


    def close_connection(self):
        try:
            self.session.commit()
        except:
            self.session.rollback()
        finally:
            self.session.expire_all()
            self.session.close()
            self.engine.dispose(close=True)


    @staticmethod
    def db_up_to_date(alembic_config:Config, engine:Engine) -> bool:
        directory = ScriptDirectory.from_config(alembic_config)

        with engine.begin() as connection:
            logging.getLogger("alembic.runtime.migration").setLevel(logging.WARN)
            context = migration.MigrationContext.configure(connection)
            logging.getLogger("alembic.runtime.migration").setLevel(logging.INFO)
            return set(context.get_current_heads()) == set(directory.get_heads())


    #Account
    def account_exists(self, name:str) -> bool:
        result = self.session.query(Account).filter(Account.name == name).first()
        return bool(result)


    def get_all_accounts(self) -> list[Account]:
        accounts = self.session.query(Account).all()
        return accounts


    def set_account_id(self, account_name:str):
        self.account_id = self.session.query(Account).filter(Account.name == account_name).first().id


    def create_account(self, account_name:str, balance:float|int=0):
        self.session.add(Account(name=account_name, start_balance=balance))
        self.session.commit()
        self.set_account_id(account_name)


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


    def change_category_position(self, new_position:int, old_position:int, category_id:int, category_type:str):
        if new_position < old_position:
            self.session.query(Category).filter(and_(Category.position < old_position, Category.position >= new_position, Category.category_type == category_type, Category.account_id == self.account_id)).update(
                {Category.position: Category.position + 1}, synchronize_session=False
            )
        else:
            self.session.query(Category).filter(and_(Category.position > old_position, Category.position <= new_position, Category.category_type == category_type, Category.account_id == self.account_id)).update(
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
        self.session.query(Category).filter_by(id=category_id).update({Category.name:new_name}, False)
        self.session.commit()


    def delete_category(self, category_id:int):
        self.remove_position(category_id)
        self.session.query(Category).filter_by(id=category_id).delete(False)
        self.session.commit()
        self.session.execute(text("VACUUM"))
        self.session.commit()



    #Transaction
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
    

    def get_transaction_by_range(self, category_id:int, from_date:int, to_date:int) -> list[Transaction]:
        return self.session.query(Transaction).filter(and_(
            Transaction.year*1000 + Transaction.month*100 + Transaction.day >= from_date,
            Transaction.year*1000 + Transaction.month*100 + Transaction.day <= to_date,
            Transaction.category_id == category_id
        )).all()
    

    #Backup
    def create_backup(self, backup_file_path:str ):
        db_file_path = self.engine.url.database.replace("sqlite:///", "")
        try:
            with sql_connect(db_file_path) as conn:
                conn.execute("PRAGMA VACUUM")

                with sql_connect(backup_file_path) as backup_conn:
                    conn.backup(backup_conn)
        finally:
            conn.close()
            backup_conn.close()


    def create_backup_based_on_external_db(self, external_db_path:str, backup_file_path:str):
        try:
            with sql_connect(external_db_path) as conn:
                with sql_connect(backup_file_path) as backup_conn:
                    conn.backup(backup_conn)
        finally:
            conn.close()
            backup_conn.close()