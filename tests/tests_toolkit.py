from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any
import pkgutil
import shutil
from functools import wraps, partial
from traceback import format_exception

from unittest import TestCase, TextTestResult
from unittest.mock import patch, create_autospec, DEFAULT as MOCK_DEFAULT, MagicMock

from colorama import init as colorama_init, Fore
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

from PySide6.QtCore import QEventLoop, QTimer

from backend.models import Category, Transaction, Account
from project_configuration import CATEGORY_TYPE
from AppManagement.category import activate_categories, remove_categories_from_list
from GUI.category import load_category

from AppObjects.session import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger


if TYPE_CHECKING:
    from AppObjects.category import Category as GUICategory
    from unittest.runner import _WritelnDecorator
    from typing import Type, Tuple, Iterable, Any
    from types import TracebackType

    OptExcInfo = Tuple[Type[BaseException], BaseException, TracebackType] | Tuple[None, None, None]
    UnpatchedFunction = Callable[..., Any]



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

def qsleep(miliseconds:int) -> None:
    """Sleep for a given number of milliseconds. time.sleep() is not used because it blocks the main event loop.

        Arguments
        ---------
            `miliseconds` : (int) - Number of milliseconds to sleep.
    """

    loop = QEventLoop()
    QTimer.singleShot(miliseconds, loop.quit)
    loop.exec()


def safe_patch(target:str, spec:Any|None=None) -> Callable[[UnpatchedFunction], Callable[[UnpatchedFunction], Any]]:
    """Patch with create_autospec(spec, spec_set=True) and inject as argument."""

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            original = MOCK_DEFAULT
            if not spec:
                try:
                    target_module, attribute = target.rsplit('.', 1)
                except (TypeError, ValueError, AttributeError):
                    raise TypeError(
                        f"Need a valid target to patch. You supplied: {target!r}")
                
                getter, name = partial(pkgutil.resolve_name, target_module), attribute

                getter = getter()
                try:
                    original = getter.__dict__[name]
                except (AttributeError, KeyError):
                    original = getattr(getter, name, MOCK_DEFAULT)

                mock_obj = create_autospec(original, spec_set=True)
            else:
                mock_obj = create_autospec(spec, spec_set=True)

            if callable(spec) or original is not MOCK_DEFAULT and callable(original):                    
                mock_obj = MagicMock(spec=mock_obj, spec_set=True)#For some reason spec_set=True is not working with functions in create_autospec, but it works if created MagickMock manually

            with patch(target, new=mock_obj):
                args = list(args)
                args.append(mock_obj)
                return func(*args, **kwargs)
            
        return wrapper
    return decorator



class DBTestCase(TestCase):
    """This class is used to create a test case that uses a database.
        It creates a test database and removes it after the test is finished."""

    def __init__(self, methodName:str = "runTest") -> None:
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

        app_core = AppCore.instance()
        @wraps(func)
        def wrapper(self:DBTestCase) -> None:
            app_core.db.category_query.create_category("Test income category", "Incomes", 0)
            app_core.db.category_query.create_category("Test expenses category", "Expenses", 0)
            
            new_income_category = app_core.db.category_query.get_category("Test income category", "Incomes")
            new_expenses_category = app_core.db.category_query.get_category("Test expenses category", "Expenses")

            if new_income_category is None or new_expenses_category is None:
                logger.error("Just created categories not found in the database")
                raise ValueError("Just created categories not found in the database")
            
            self.income_category = new_income_category
            self.expenses_category = new_expenses_category

            app_core.db.transaction_query.add_transaction(self.income_category.id, app_core.current_year, app_core.current_month, 1, 1000, "Test income transaction")
            app_core.db.transaction_query.add_transaction(self.expenses_category.id, app_core.current_year, app_core.current_month, 1, 1000, "Test expenses transaction")

            app_core.categories[self.income_category.id] = load_category(self.income_category.category_type, self.income_category.name, app_core.db, self.income_category.id, 0, app_core.current_year, app_core.current_month)
            app_core.categories[self.expenses_category.id] = load_category(self.expenses_category.category_type, self.expenses_category.name, app_core.db, self.expenses_category.id, 0, app_core.current_year, app_core.current_month)
            activate_categories()

            return func(self)#Looks like it should be self.func but since we are outside of the class, we have to do func(self)
        
        return wrapper
    

    def select_correct_tab(self, category:GUICategory) -> None:
        """This method is used to select the correct tab in the main window.

            Arguments
            ---------
                `category` : (GUICategory) - Category to select tab.
        """

        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
    

    def tearDown(self) -> None:
        """This method is used to remove the test database after the test is finished."""

        remove_categories_from_list()
        app_core = AppCore.instance()
        with app_core.db.session_factory() as session:
            with session.begin():
                session.query(Category).delete()
                session.query(Transaction).delete()
                session.query(Account).filter(Account.id != 1).delete()
        
        app_core.config.account_name = "Test user"
        app_core.db.set_account_id(app_core.config.account_name)



class OutOfScopeTestCase(TestCase):
    """This class is used to capture the tests assertion errors from functions that are runned using QTimer.singleShot."""

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        for attr in dir(cls):
            if attr.startswith("test") and callable(getattr(cls, attr)):
                original_test = getattr(cls, attr)
                wrapped_test = cls.check_out_of_scope_failure(original_test)
                setattr(cls, attr, wrapped_test)


    def setUp(self) -> None:
        super().setUp()
        self._assertion_error:AssertionError | None = None


    def catch_failure(self, func:Callable[[], None]) -> Callable[[], None]:
        """This decorator is used to catch the assertion errors from functions that are runned using QTimer.singleShot."""

        @wraps(func)
        def wrapper() -> None:
            try:
                func()
            except AssertionError as e:
                self._assertion_error = e
                raise e
        
        return wrapper
    

    @staticmethod
    def check_out_of_scope_failure(func:Callable[[OutOfScopeTestCase], None]) -> Callable[[OutOfScopeTestCase], None]:
        """This decorator checks if in assertions errors occured out of scope and raises them."""

        @wraps(func)
        def wrapper(self:OutOfScopeTestCase) -> None:
            func(self)

            if self._assertion_error is not None:
                raise self._assertion_error
        
        return wrapper



class ColoredTextTestResult(TextTestResult):

    def __init__(self, stream:_WritelnDecorator, descriptions:bool, verbosity:int) -> None:
        super().__init__(stream, descriptions, verbosity)


    def _print_separator(self, separator: str = SEPARATOR1) -> None:
        """Print a separator line with dynamic length (based on console width)."""
        width = shutil.get_terminal_size().columns-1
        self.stream.writeln("\n"+separator * width)


    def startTest(self, test:TestCase) -> None:
        """Override startTest to print separators and the test name."""
        self._print_separator()
        self.stream.writeln(f"Running test: {test}")

        super().startTest(test)


    def stopTest(self, test:TestCase) -> None:
        """Override stopTest to print a separator at the end of the test."""
        super().stopTest(test)


    def addSuccess(self, test:TestCase) -> None:
        """Override to print success message in green."""
        self.stream.write(SUCCESS_COLOR + f"{SUCCESS}: {test}")
        super().addSuccess(test)


    def addFailure(self, test:TestCase, err:OptExcInfo) -> None:
        """Override to print failure message in red."""
        self.stream.write(FAIL_COLOR + f"{FAIL}: {test}")

        exception_type, exception_value, traceback_obj = err
        formatted_exception = "".join(format_exception(exception_type, exception_value, traceback_obj))
        colored_exception = highlight(formatted_exception, LEXER, FORMATTER)

        self.failures.append((test, colored_exception))
        self._mirrorOutput = True#This is an protected attribute, it's used (if you use self.buffer = True) to mirror output to stdout/stderr
        #I don't use super method because it will print extra traceback message


    def addError(self, test:TestCase, err:OptExcInfo) -> None:
        """Override to print error message in yellow."""
        self.stream.write(ERROR_COLOR + f"{ERROR}: {test}")

        exception_type, exception_value, traceback_obj = err
        formatted_exception = "".join(format_exception(exception_type, exception_value, traceback_obj))
        colored_exception = highlight(formatted_exception, LEXER, FORMATTER)

        self.errors.append((test, colored_exception))
        self._mirrorOutput = True
        #I don't use super method because it will print extra traceback message
    

    def printErrorList(self, flavour:str, errors:Iterable[tuple[TestCase, str]]) -> None:
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
