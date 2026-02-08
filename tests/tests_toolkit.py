from __future__ import annotations
import shutil
import os

from typing import TYPE_CHECKING, Callable
from functools import wraps
from traceback import format_exception
from threading import Thread
from time import sleep
from datetime import date

from colorama import init as colorama_init, Fore
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

from unittest import TestCase, TextTestResult
from unittest.mock import Mock

from PySide6.QtCore import QEventLoop, QTimer, QObject, Signal
from PySide6.QtWidgets import QPushButton, QToolButton, QCheckBox

from backend.models import Category, Transaction, Account
from project_configuration import TEST_BACKUPS_DIRECTORY, CategoryType
from AppManagement.category import activate_categories, remove_categories_from_list
from AppManagement.backup_management import remove_backup
from GUI.category import load_category
from DesktopQtToolkit.sub_window import SubWindow

from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from AppObjects.logger import get_logger
from AppObjects.app_exceptions import WidgetIsDisabledError, WidgetIsNotVisibleError


if TYPE_CHECKING:
    from AppObjects.category import Category as GUICategory
    from unittest.runner import _WritelnDecorator
    from unittest.mock import _patch
    from typing import Type, Tuple, Iterable, Any
    from types import TracebackType

    OptExcInfo = Tuple[Type[BaseException], BaseException, TracebackType] | Tuple[None, None, None]



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

def qsleep(milliseconds:int) -> None:
    """Sleep for a given number of milliseconds. time.sleep() is not used because it blocks the main event loop.

        Arguments
        ---------
            `milliseconds` : (int) - Number of milliseconds to sleep.
    """

    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()


def assert_any_call_with_details(mock: Mock, *args:Any, msg: str | None = None, **kwargs:dict[str, Any]) -> None:
    """
    Like mock.assert_any_call but if it fails raises AssertionError that
    includes mock.call_args_list for easier debugging.
    """

    if not hasattr(mock, "assert_any_call"):
        raise TypeError(f"First argument must be a Mock instance not {type(mock).__name__}")

    try:
        mock.assert_any_call(*args, **kwargs)
    except AssertionError as exc:
        calls = getattr(mock, "call_args_list", [])
        prefix = f"{msg}\n" if msg else ""
        calls_string = "\n".join(f"Call {call_number}: {call}" for call_number, call in enumerate(calls, start=1))
        detailed = f"{prefix}{exc}\n\nCalls list:\n{calls_string}"
        raise AssertionError(detailed) from None


def is_active_patch(patch:_patch[Any]) -> bool:
    """Check if a patch is active.

        Arguments
        ---------
            `patch` : (_patch) - Patch to check.
        Returns
        -------
            `bool` - True if the patch is active, False otherwise.
    """
    return getattr(patch, "is_local", False)


class DefaultTestCase(TestCase):
    """This class is used to create a default test case which every test case should inherit from."""

    class SubWindowCloseWorker(QObject):
        close_window = Signal(SubWindow)

    TIMEOUT_SEC = 6  # Default timeout for test to auto-close sub-windows in seconds

    def setUp(self) -> None:
        super().setUp()
        self.test_running = True
        self.sub_window_closer = self.SubWindowCloseWorker()
        self.timeout_error: Exception | None = None
        self.sub_window_closer.close_window.connect(lambda window: window.done(1))
        Thread(target=self.close_all_sub_windows).start()
    

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        qsleep(2000)#Wait for the application to initialize properly
        

    def close_all_sub_windows(self) -> None:
        """This method will close all sub-windows after each test."""

        sleep(self.TIMEOUT_SEC)
        if self.test_running:
            self.timeout_error = TimeoutError(
                f"Test took too long to complete (>{self.TIMEOUT_SEC} seconds), closing all sub-windows and failing the test."
            )
            while self.test_running:
                for sub_window in WindowsRegistry.MainWindow.sub_windows.values():
                    if sub_window.isVisible():
                        self.sub_window_closer.close_window.emit(sub_window)
                sleep(0.1)
    

    def click_on_widget(self, widget:QPushButton|QToolButton|QCheckBox) -> None:
        """Click on a widget.

            Arguments
            ---------
                `widget` : (QWidget) - Widget to click on.
        """

        if not isinstance(widget, (QPushButton, QToolButton, QCheckBox)):
            raise TypeError(f"Widget must be an instance of QPushButton, QToolButton or QCheckBox not {type(widget).__name__}")
        
        if not widget.isVisible():
            raise WidgetIsNotVisibleError(f"\nWidget {widget} with text '{widget.text()}' is not visible\n")

        if not widget.isEnabled():
            raise WidgetIsDisabledError(f"\nWidget {widget} with text '{widget.text()}' is not enabled\n")
        
        widget.click()
    

    def get_incomes_and_expenses_categories(self) -> Tuple[list[GUICategory], list[GUICategory]]:
        """This method is used to get all income and expense categories from the application.

            Returns
            -------
                `Tuple[list[GUICategory], list[GUICategory]]` - Tuple of two lists, first list contains income categories,
                second list contains expense categories.
        """

        app_core = AppCore.instance()
        income_categories, expense_categories = app_core.get_income_and_expense_categories()

        return income_categories, expense_categories


    def tearDown(self) -> None:
        self.test_running = False
        if self.timeout_error:
            raise self.timeout_error
        super().tearDown()


class DBTestCase(DefaultTestCase):
    """This class is used to create a test case that uses a database.
        It creates a test database and removes it after the test is finished."""

    def __init__(self, methodName:str = "runTest") -> None:
        super().__init__(methodName)

        self.income_category:Category
        self.income_transaction:Transaction
        self.expenses_category:Category
        self.expenses_transaction:Transaction

        self.test_income_transaction_name = "Test income transaction"
        self.test_expenses_transaction_name = "Test expenses transaction"
        self.test_income_category_name = "Test income category"
        self.test_expenses_category_name = "Test expenses category"


    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        original_setUp = cls.__dict__.get("setUp", super().setUp)
        wrapped_setUp = cls.set_up_decorator(original_setUp)
        setattr(cls, "setUp", wrapped_setUp)

    
    @staticmethod
    def set_up_decorator(func:Callable[[DBTestCase], None]) -> Callable[[DBTestCase], None]:
        """
            This decorator is used to set up the test case.
            It creates first objects so we don't have to create them in every test case.

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
            os.makedirs(TEST_BACKUPS_DIRECTORY, exist_ok=True)

            app_core.db.category_query.create_category(self.test_income_category_name, "Incomes", 0)
            app_core.db.category_query.create_category(self.test_expenses_category_name, "Expenses", 0)
            
            new_income_category = app_core.db.category_query.get_category(self.test_income_category_name, "Incomes")
            new_expenses_category = app_core.db.category_query.get_category(self.test_expenses_category_name, "Expenses")
            if new_income_category is None or new_expenses_category is None:
                logger.error("Just created categories not found in the database")
                raise ValueError("Just created categories not found in the database")
            
            self.income_category = new_income_category
            self.expenses_category = new_expenses_category

            self.income_transaction = app_core.db.transaction_query.add_transaction(
                self.income_category.id,
                date(app_core.current_year, app_core.current_month, date.today().day),
                1000,
                self.test_income_transaction_name
            )
            self.expenses_transaction = app_core.db.transaction_query.add_transaction(
                self.expenses_category.id,
                date(app_core.current_year, app_core.current_month, date.today().day),
                1000,
                self.test_expenses_transaction_name
            )

            for category in [self.income_category, self.expenses_category]:
                app_core.categories[category.id] = load_category(
                    category,
                    app_core.db,
                    app_core.current_year,
                    app_core.current_month
                )
            activate_categories()

            return func(self)#Looks like it should be self.func but since we are outside of the class, we have to do func(self)
        
        return wrapper
    

    def select_correct_tab(self, category:GUICategory) -> None:
        """This method is used to select the correct tab in the main window.

            Arguments
            ---------
                `category` : (GUICategory) - Category to select tab.
        """

        WindowsRegistry.MainWindow.Incomes_and_expenses.setCurrentIndex(CategoryType.get_index(category.type))
    

    def remove_all_backups(self) -> None:
        """This method is used to remove all backups in application memory created during the test."""
        
        while AppCore.instance().backups:
            WindowsRegistry.BackupManagementWindow.backups_table.selectRow(0)
            QTimer.singleShot(100, WindowsRegistry.Messages.below_recommended_min_backups.ok_button.click)
            QTimer.singleShot(150, WindowsRegistry.Messages.delete_backup_confirmation.ok_button.click)
            remove_backup()


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
        
        self.remove_all_backups()
        if os.path.exists(TEST_BACKUPS_DIRECTORY):
            shutil.rmtree(TEST_BACKUPS_DIRECTORY)

        super().tearDown()



class OutOfScopeTestCase(DefaultTestCase):
    """
    This class is used to capture the tests assertion errors from functions that are runned using QTimer.singleShot.
    """

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        for attr in dir(cls):
            if attr.startswith("test") and callable(getattr(cls, attr)):
                original_test = getattr(cls, attr)
                wrapped_test = cls.check_out_of_scope_failure(original_test)
                setattr(cls, attr, wrapped_test)


    def setUp(self) -> None:
        super().setUp()
        self._assertion_error: Exception | None = None


    def catch_failure(self, func: Callable[[], None]) -> Callable[[], None]:
        """
        This decorator is used to catch the assertion errors from functions that are runned using QTimer.singleShot.
        """

        @wraps(func)
        def wrapper() -> None:
            try:
                func()
            except Exception as e:
                self._assertion_error = e
                raise e
        
        return wrapper
    

    @staticmethod
    def check_out_of_scope_failure(func:Callable[[OutOfScopeTestCase], None]) -> Callable[[OutOfScopeTestCase], None]:
        """This decorator checks if in assertions errors occurred out of scope and raises them."""

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
