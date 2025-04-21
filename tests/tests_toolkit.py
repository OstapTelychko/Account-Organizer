from __future__ import annotations
from typing import TYPE_CHECKING, Callable
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
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger

from GUI.category import load_category

if TYPE_CHECKING:
    from AppObjects.category import Category as GUICategory



LEXER = get_lexer_by_name("py3tb")
FORMATTER = TerminalFormatter()
colorama_init(autoreset=True)

ERROR = "ERROR"
ERROR_COLOR = Fore.YELLOW
FAIL = "FAIL"
FAIL_COLOR = Fore.RED
SUCCESS = "SUCCESS"
SUCCESS_COLOR = Fore.GREEN

SEPARATOR1 = "=" 
SEPARATOR2 = "-"

logger = get_logger(__name__)

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

    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        self.income_category:Category
        self.expenses_category:Category


    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        original_setUp = cls.__dict__.get("setUp", super().setUp)
        wrapped_setUp = cls.set_up_decorator(original_setUp)
        setattr(cls, "setUp", wrapped_setUp)

    
    @staticmethod
    def set_up_decorator(func:Callable[[DBTestCase], None]) -> Callable[[DBTestCase], None]:
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
            
            new_income_category = Session.db.category_query.get_category("Test income category", "Incomes")
            new_expenses_category = Session.db.category_query.get_category("Test expenses category", "Expenses")

            if new_income_category is None or new_expenses_category is None:
                logger.error("Just created categories not found in the database")
                raise ValueError("Just created categories not found in the database")
            
            self.income_category = new_income_category
            self.expenses_category = new_expenses_category

            Session.db.transaction_query.add_transaction(self.income_category.id, Session.current_year, Session.current_month, 1, 1000, "Test income transaction")
            Session.db.transaction_query.add_transaction(self.expenses_category.id, Session.current_year, Session.current_month, 1, 1000, "Test expenses transaction")

            Session.categories[self.income_category.id] = load_category(self.income_category.category_type, self.income_category.name, Session.db, self.income_category.id, 0, Session.current_year, Session.current_month, Session.config.language)
            Session.categories[self.expenses_category.id] = load_category(self.expenses_category.category_type, self.expenses_category.name, Session.db, self.expenses_category.id, 0, Session.current_year, Session.current_month, Session.config.language)
            activate_categories()

            return func(self)#Looks like it should be self.func but since we are outside of the class, we have to do func(self)
        
        return wrapper
    

    def select_correct_tab(self, category:GUICategory):
        """This method is used to select the correct tab in the main window.

            Arguments
            ---------
                `category` : (GUICategory) - Category to select tab.
        """

        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
    

    def tearDown(self) -> None:
        """This method is used to remove the test database after the test is finished."""

        remove_categories_from_list()

        Session.db.session.expunge_all()
        Session.db.session.query(Category).delete()
        Session.db.session.query(Transaction).delete()
        Session.db.session.query(Account).filter(Account.id != 1).delete()
        
        Session.config.account_name = "Test user"
        Session.db.set_account_id(Session.config.account_name)



class ColoredTextTestResult(TextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _print_separator(self, separator: str = SEPARATOR1):
        """Print a separator line with dynamic length (based on console width)."""
        width = shutil.get_terminal_size().columns-1
        self.stream.writeln("\n"+separator * width)


    def startTest(self, test):
        """Override startTest to print separators and the test name."""
        self._print_separator()
        self.stream.writeln(f"Running test: {test}")

        super().startTest(test)


    def stopTest(self, test):
        """Override stopTest to print a separator at the end of the test."""
        super().stopTest(test)


    def addSuccess(self, test):
        """Override to print success message in green."""
        self.stream.write(SUCCESS_COLOR + f"{SUCCESS}: {test}")
        super().addSuccess(test)


    def addFailure(self, test, err):
        """Override to print failure message in red."""
        self.stream.write(FAIL_COLOR + f"{FAIL}: {test}")

        exception_type, exception_value, traceback_obj = err
        formatted_exception = "".join(format_exception(exception_type, exception_value, traceback_obj))
        colored_exception = highlight(formatted_exception, LEXER, FORMATTER)

        self.failures.append((test, colored_exception))
        self._mirrorOutput = True#This is an protected attribute, it's used (if you use self.buffer = True) to mirror output to stdout/stderr
        #I don't use super method because it will print extra traceback message


    def addError(self, test, err):
        """Override to print error message in yellow."""
        self.stream.write(ERROR_COLOR + f"{ERROR}: {test}")

        exception_type, exception_value, traceback_obj = err
        formatted_exception = "".join(format_exception(exception_type, exception_value, traceback_obj))
        colored_exception = highlight(formatted_exception, LEXER, FORMATTER)

        self.errors.append((test, colored_exception))
        self._mirrorOutput = True
        #I don't use super method because it will print extra traceback message
    

    def printErrorList(self, flavour, errors):
        """Override to print errors in colored format."""
        for test, err in errors:
            self._print_separator()

            if flavour == ERROR:
                self.stream.write(f"{ERROR_COLOR}{flavour}: {self.getDescription(test)}")
            elif flavour == FAIL:
                self.stream.write(f"{FAIL_COLOR}{flavour}: {self.getDescription(test)}")

            self._print_separator(SEPARATOR2)
            self.stream.writeln(err)
            self.stream.flush()
