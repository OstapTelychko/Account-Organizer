from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer
from test.tests_toolkit import DBTestCase

from backend.models import Category
from AppObjects.session import Session
from project_configuration import CATEGORY_TYPE

from GUI.windows.main_window import MainWindow
from GUI.windows.errors import Errors
from GUI.windows.category import AddCategoryWindow, CategorySettingsWindow, RenameCategoryWindow, ChangeCategoryPositionWindow



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
    

    def test_category_deletion(self):
        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in Session.categories.copy().values():

            def delete_category():
                QTimer.singleShot(100, lambda: Errors.delete_category_confirmation.button(QMessageBox.StandardButton.Ok).click())
                CategorySettingsWindow.delete_category.click()

            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
            QTimer.singleShot(100, delete_category)
            category.settings.click()

        self.assertFalse(Session.db.session.query(Category).filter_by(name=income_category_name).first(), "Income category hasn't been deleted")
        self.assertFalse(Session.db.session.query(Category).filter_by(name=expenses_category_name).first(), "Expense category hasn't been deleted")
    

    def test_category_rename(self):
        income_category_name = self.income_category.name
        expenses_category_name = self.expenses_category.name

        for category in Session.categories.copy().values():

            def open_settings():

                def rename_category():
                    RenameCategoryWindow.new_category_name.setText(f"{category.name} rename test")
                    RenameCategoryWindow.button.click()

                QTimer.singleShot(100, rename_category)
                CategorySettingsWindow.rename_category.click()

            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
            QTimer.singleShot(100, open_settings)
            category.settings.click()

        self.assertTrue(Session.db.session.query(Category).filter_by(name=income_category_name+" rename test").first(), "Income category hasn't been renamed")
        self.assertTrue(Session.db.session.query(Category).filter_by(name=expenses_category_name+" rename test").first(), "Expense category hasn't been renamed")
    

    def test_category_position_change(self):
        Session.db.create_category("Second "+self.income_category.name, "Incomes", 1)
        Session.db.create_category("Second "+self.expenses_category.name, "Expenses", 1)

        for category in Session.categories.copy().values():

            def open_settings():
                def change_position():
                    ChangeCategoryPositionWindow.new_position.setText("1")
                    ChangeCategoryPositionWindow.enter_new_position.click()

                QTimer.singleShot(100, change_position)
                CategorySettingsWindow.change_category_position.click()

            MainWindow.Incomes_and_expenses.setCurrentIndex(next(index for index, category_type in CATEGORY_TYPE.items() if category.type == category_type))
            QTimer.singleShot(100, open_settings)
            category.settings.click()

        self.assertEqual(Session.db.get_category(self.income_category.name, "Incomes").position, 1, "Income category hasn't changed position to 1")
        self.assertEqual(Session.db.get_category("Second "+self.income_category.name, "Incomes").position, 0, "Income category hasn't changed position to 0")
        self.assertEqual(Session.db.get_category(self.expenses_category.name, "Expenses").position, 1, "Expenses category hasn't changed position to 1")
        self.assertEqual(Session.db.get_category("Second "+self.expenses_category.name, "Expenses").position, 0, "Expenses category hasn't changed position to 1")
    
