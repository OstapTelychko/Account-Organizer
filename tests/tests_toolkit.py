from unittest import TestCase

from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer

from backend.models import Category, Transaction, Account

from AppObjects.session import Session
from GUI.category import load_category
from AppManagement.category import activate_categories, remove_categories_from_list


LEFT_BUTTON = Qt.MouseButton.LeftButton


class TestWindowsCaseMixin():

    def test_windows_opening(self:TestCase):
        for window, open_window_button in self.test_windows_open.items():
            window_object = getattr(window, "window")

            def check_window_appearance():
                self.assertTrue(window_object.isVisible(), f"Window {window.__name__} hasn't showed after click on button {open_window_button.text()}")
                window_object.done(1)

            QTimer.singleShot(100, check_window_appearance)# Timer will call this function after 100 milliseconds. QDialog use exec to show up so it block program loop
            open_window_button.click()



class DBTestCase(TestCase):

    def __init_subclass__(cls) -> None:
        if "setUp" in cls.__dict__:
            cls.setUp = DBTestCase.set_up_decorator(cls.setUp)
        else:
            cls.setUp = DBTestCase.set_up_decorator(super().setUp)

    

    def set_up_decorator(func):
        def wrapper(self:DBTestCase):
            Session.db.create_category("Test income category", "Incomes", 0)
            Session.db.create_category("Test expenses category", "Expenses", 0)
            
            self.income_category = Session.db.get_category("Test income category", "Incomes")
            self.expenses_category = Session.db.get_category("Test expenses category", "Expenses")

            Session.db.add_transaction(self.income_category.id, Session.current_year, Session.current_month, 1, 1600, "Test income transaction")
            Session.db.add_transaction(self.expenses_category.id, Session.current_year, Session.current_month, 1, 1600, "Test expenses transaction")

            remove_categories_from_list()
            Session.categories[self.income_category.id] = load_category(self.income_category.category_type, self.income_category.name, Session.db, self.income_category.id, 0, Session.current_year, Session.current_month, Session.language)
            Session.categories[self.expenses_category.id] = load_category(self.expenses_category.category_type, self.expenses_category.name, Session.db, self.expenses_category.id, 0, Session.current_year, Session.current_month, Session.language)
            activate_categories()

        return wrapper
    

    @classmethod
    def setUpClass(cls):
        cls.income_category:Category
        cls.expenses_category:Category
    

    def tearDown(self) -> None:
        Session.db.session.query(Category).delete()
        Session.db.session.query(Transaction).delete()
        Session.db.session.query(Account).filter(Account.name != "Test user").delete()
        Session.account_name = "Test user"



    