from __future__ import annotations
from typing import TYPE_CHECKING
from unittest import TestCase, TextTestRunner, TextTestResult
import shutil
from functools import wraps

from colorama import init as colorama_init, Fore, Style
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

from traceback import format_exception

from PySide6.QtCore import QEventLoop, QTimer

from backend.models import Category, Transaction, Account
from project_configuration import CATEGORY_TYPE
from AppManagement.category import activate_categories, remove_categories_from_list
from AppObjects.session import Session

from GUI.category import load_category
from GUI.windows.main_window import MainWindow

if TYPE_CHECKING:
    from AppObjects.category import Category as GUICategory



LEXER = get_lexer_by_name("py3tb")
FORMATTER = TerminalFormatter()
colorama_init(autoreset=True)

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



class CustomTextTestResult(TextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _print_separator(self):
        """Print a separator line with dynamic length (based on console width)."""
        width = shutil.get_terminal_size().columns-1
        print("\n"+"=" * width)


    def startTest(self, test):
        """Override startTest to print separators and the test name."""
        self._print_separator()
        print(f"Running test: {test}")

        super().startTest(test)


    def stopTest(self, test):
        """Override stopTest to print a separator at the end of the test."""
        super().stopTest(test)


    def addSuccess(self, test):
        """Override to print success message in green."""
        print(Fore.GREEN + f"SUCCESS: {test}", end=" ")
        super().addSuccess(test)


    def addFailure(self, test, err):
        """Override to print failure message in red."""
        print(Fore.RED + f"FAILURE: {test}")

        exception_type, exception_value, traceback_obj = err
        formatted_exception = "".join(format_exception(exception_type, exception_value, traceback_obj))
        colored_exception = highlight(formatted_exception, LEXER, FORMATTER)

        self.failures.append((test, colored_exception))
        self._mirrorOutput = True#This is an protected attribute, it's used (if you use self.buffer = True) to mirror output to stdout/stderr
        #I don't use super method because it will print extra traceback message


    def addError(self, test, err):
        """Override to print error message in yellow."""
        print(Fore.YELLOW + f"ERROR: {test}")

        exception_type, exception_value, traceback_obj = err
        formatted_exception = "".join(format_exception(exception_type, exception_value, traceback_obj))
        colored_exception = highlight(formatted_exception, LEXER, FORMATTER)

        self.errors.append((test, colored_exception))
        self._mirrorOutput = True
        #I don't use super method because it will print extra traceback message
        