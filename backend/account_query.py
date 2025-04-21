from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.sql import text
from backend.models import Account
from AppObjects.logger import get_logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as sql_Session



logger = get_logger(__name__)

class AccountQuery:
    """This class is used to manage accounts and related to accounts data in the database."""

    def __init__(self, session:sql_Session):
        self.session = session
        self.account_id:int
    

    def account_exists(self, name:str) -> bool:
        """Check if an account with the given name exists in the database.

            Arguments
            ---------
                `name` : (str) - Name of the account to check.
            Returns
            -------
                `bool` - True if the account exists, False otherwise.
        """

        result = self.session.query(Account).filter(Account.name == name).first()
        return bool(result)


    def get_all_accounts(self) -> list[Account]:
        """Get all accounts from the database.

            Returns
            -------
                `list[Account]` - List of all accounts in the database.
        """

        accounts = self.session.query(Account).all()
        return accounts


    def create_account(self, account_name:str, balance:float|int=0):
        """Create a new account in the database.

            Arguments
            ---------
                `account_name` : (str) - Name of the account to create.
                `balance` : (float|int) - Initial balance of the account. Default is 0.
        """

        self.session.add(Account(name=account_name, start_balance=balance))
        self.session.commit()


    def get_account(self) -> Account:
        """Get the account object from the database.

            Returns
            -------
                `Account` - The account object.
        """

        account = self.session.query(Account).filter_by(id=self.account_id).first()
        if account:
            return account
        else:
            logger.error(f"Account with ID {self.account_id} not found.")
            raise ValueError(f"Account with ID {self.account_id} not found.")


    def update_account_balance(self, balance:float|int, total_income:int|float, total_expenses:int|float):
        """Update the account balance in the database.

            Arguments
            ---------
                `balance` : (float|int) - New balance of the account.
                `total_income` : (int|float) - Total income of the account.
                `total_expenses` : (int|float) - Total expenses of the account.
        """

        self.session.query(Account).filter_by(id=self.account_id).update({
            Account.current_balance:balance,
            Account.current_total_income:total_income,
            Account.current_total_expenses:total_expenses
        }, False)
        self.session.commit()


    def rename_account(self, new_account_name:str):
        """Rename the account in the database.

            Arguments
            ---------
                `new_account_name` : (str) - New name of the account.
        """

        account = self.session.query(Account).filter_by(id=self.account_id).first()

        if account:
            account.name = new_account_name
            self.session.commit()
        else:
            logger.error(f"Account with ID {self.account_id} not found.")
    

    def delete_account(self):
        """Delete the account from the database."""
        
        account = self.session.query(Account).filter_by(id=self.account_id).first()
        self.session.delete(account)
        self.session.commit()
        self.session.execute(text("VACUUM"))
        self.session.commit()
  