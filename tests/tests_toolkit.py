from __future__ import annotations
from typing import TYPE_CHECKING
from unittest import TestCase
from functools import wraps

from PySide6.QtCore import QEventLoop, QTimer

from backend.models import Category, Transaction, Account

from AppObjects.session import Session

from GUI.category import load_category
from GUI.windows.main_window import MainWindow

from project_configuration import CATEGORY_TYPE
from AppManagement.category import activate_categories, remove_categories_from_list

if TYPE_CHECKING:
    from AppObjects.category import Category as GUICategory
    
    

def qsleep(miliseconds:int):
    """Sleep for a given number of milliseconds. time.sleep() is not used because it blocks the main event loop.

        Arguments
        ---------
            `miliseconds` : (int) - Number of milliseconds to sleep.
    """

    loop = QEventLoop()
    QTimer.singleShot(miliseconds, loop.quit)
    loop.exec()


class DBTestCase(TestCase):
    """This class is used to create a test case that uses a database.
        It creates a test database and removes it after the test is finished."""

    def __init_subclass__(cls) -> None:
        if "setUp" in cls.__dict__:
            cls.setUp = DBTestCase.set_up_decorator(cls.setUp)
        else:
            cls.setUp = DBTestCase.set_up_decorator(super().setUp)

    

    def set_up_decorator(func):
        """This decorator is used to set up the test case. It creates first objects so you don't have to create them in every test case.

            Arguments
            ---------
                `func` : (function) - Function to decorate.
            Returns
            -------
                `function` - Decorated function.
        """

        @wraps(func)
        def wrapper(self:DBTestCase):
            Session.db.category_query.create_category("Test income category", "Incomes", 0)
            Session.db.category_query.create_category("Test expenses category", "Expenses", 0)
            
            self.income_category = Session.db.category_query.get_category("Test income category", "Incomes")
            self.expenses_category = Session.db.category_query.get_category("Test expenses category", "Expenses")

            Session.db.transaction_query.add_transaction(self.income_category.id, Session.current_year, Session.current_month, 1, 1000, "Test income transaction")
            Session.db.transaction_query.add_transaction(self.expenses_category.id, Session.current_year, Session.current_month, 1, 1000, "Test expenses transaction")

            Session.categories[self.income_category.id] = load_category(self.income_category.category_type, self.income_category.name, Session.db, self.income_category.id, 0, Session.current_year, Session.current_month, Session.language)
            Session.categories[self.expenses_category.id] = load_category(self.expenses_category.category_type, self.expenses_category.name, Session.db, self.expenses_category.id, 0, Session.current_year, Session.current_month, Session.language)
            activate_categories()

            return func(self)
        
        return wrapper
    

    def select_correct_tab(self, category:GUICategory):
        """This method is used to select the correct tab in the main window.

            Arguments
            ---------
                `category` : (GUICategory) - Category to select tab.
        """

        MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))


    @classmethod
    def setUpClass(cls):
        """This method is used to set up the test case. It just tells IDE that class have those variables (they are created dynamically in decorator).

            Arguments
            ---------
                `cls` : (DBTestCase) - Test case class.
        """

        cls.income_category:Category
        cls.expenses_category:Category
    

    def tearDown(self) -> None:
        """This method is used to remove the test database after the test is finished."""

        remove_categories_from_list()

        Session.db.session.expunge_all()
        Session.db.session.query(Category).delete()
        Session.db.session.query(Transaction).delete()
        Session.db.session.query(Account).filter(Account.id != 1).delete()
        
        Session.account_name = "Test user"
        Session.db.set_account_id(Session.account_name)



    