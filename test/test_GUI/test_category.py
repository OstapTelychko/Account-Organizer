from PySide6.QtCore import QTimer
from test.tests_toolkit import DBTestCase

from backend.models import Category
from AppObjects.session import Session

from GUI.windows.main_window import MainWindow
from GUI.windows.category import AddCategoryWindow



class TestCategory(DBTestCase):

    def test_category_creation(self):

        def add_category(name:str):
            AddCategoryWindow.category_name.setText(name)
            AddCategoryWindow.button.click()

        QTimer.singleShot(100, lambda: add_category("Test incomes creation category"))
        MainWindow.add_incomes_category.click()
        self.assertTrue(Session.db.session.query(Category).filter_by(name="Test incomes creation category").first(), "Incomes category hasn't been created")

        QTimer.singleShot(100, lambda: add_category("Test expenses creation category"))
        MainWindow.Incomes_and_expenses.setCurrentIndex(1)
        MainWindow.add_expenses_category.click()
        self.assertTrue(Session.db.session.query(Category).filter_by(name="Test expenses creation category").first(), "Expenses category hasn't been created")
