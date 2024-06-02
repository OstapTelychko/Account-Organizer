from unittest import TestCase
from datetime import datetime

from PySide6.QtTest import QTest
from PySide6.QtCore import QTimer
from test.tests_toolkit import TestWindowsCaseMixin, LEFT_BUTTON

from languages import LANGUAGES
from AppObjects.session import Session

from GUI.windows.main import MainWindow, SettingsWindow
from GUI.windows.errors import Errors
from GUI.windows.statistics import StatisticsWindow
from GUI.windows.category import AddCategoryWindow




class TestMainWindow(TestCase, TestWindowsCaseMixin):

    def setUp(self) -> None:
        self.test_windows_open = {SettingsWindow:MainWindow.settings, StatisticsWindow:MainWindow.statistics, AddCategoryWindow:MainWindow.add_incomes_category}


    def test_date_change(self):
        months_list = LANGUAGES[Session.language]["Months"]
        current_month = datetime.now().month
        translated_current_month = months_list[current_month]

        current_showed_month = MainWindow.current_month.text()
        self.assertEqual(translated_current_month, current_showed_month, f"Wrong current month has been showed {current_showed_month} instead of {translated_current_month}")

        translated_next_month = months_list[current_month+1] if current_month != 12 else months_list[1]
        MainWindow.next_month_button.click()
        current_showed_month = MainWindow.current_month.text()
        self.assertEqual(translated_next_month, current_showed_month, f"Wrong next month has been showed {current_showed_month} instead of {translated_next_month}")

        translated_previous_month = months_list[current_month] if current_month != 1 else months_list[12]
        MainWindow.previous_month_button.click()
        current_showed_month = MainWindow.current_month.text()
        self.assertEqual(translated_previous_month, current_showed_month, f"Wrong previous month has been showed {current_showed_month} instead of {translated_previous_month}")

        current_year = datetime.now().year
        current_showed_year = MainWindow.current_year.text()
        self.assertEqual(str(current_year), current_showed_year, f"Wrong current year has been showed {current_showed_year} instead of {current_year}")

        MainWindow.next_year_button.click()
        current_showed_year = MainWindow.current_year.text()
        self.assertEqual(str(current_year+1), current_showed_year, f"Wrong next year has been showed {current_showed_year} instead of {current_year+1}")
        
        MainWindow.previous_year_button.click()
        current_showed_year = MainWindow.current_year.text()
        self.assertEqual(str(current_year), current_showed_year, f"Wrong previous year has been showed {current_showed_year} instead of {current_year}")
    

    def test_mini_calculator(self):
        MainWindow.mini_calculator_text.setText("2*2")
        MainWindow.calculate.click()
        result = MainWindow.mini_calculator_text.text()
        self.assertEqual("4", result, f"Mini calculator has returned wrong result for expression 2*2 {result} instead of 4")

        MainWindow.mini_calculator_text.setText("100+300+400+500")
        MainWindow.calculate.click()
        result = MainWindow.mini_calculator_text.text()
        self.assertEqual("1300", result, f"Mini calculator has returned wrong result for expression 100+300+400+500 {result} instead of 1300")

        MainWindow.mini_calculator_text.setText("1000Money+friends")
        MainWindow.calculate.click()
        result = MainWindow.mini_calculator_text.text()
        translated_warning = LANGUAGES[Session.language]["Mini calculator"][2]
        self.assertEqual(translated_warning, result, f"Mini calculator has returned wrong result for incorrect expression {result} instead of {translated_warning}")

        MainWindow.mini_calculator_text.setText("5/0")
        MainWindow.calculate.click()
        result = MainWindow.mini_calculator_text.text()
        translated_warning = LANGUAGES[Session.language]["Mini calculator"][1]
        self.assertEqual(translated_warning, result, f"Mini calculator has returned wrong result for division by zero {result} instead of {translated_warning}")

        MainWindow.mini_calculator_text.setText("")
        def check_empty_expression_error():
            result = MainWindow.mini_calculator_text.text()
            translated_error = LANGUAGES[Session.language]["Errors"][12]
            self.assertTrue(Errors.empty_expression.isVisible(), f"Mini calculator hasn't showed error {translated_error}. Result expression {result}")
            Errors.empty_expression.done(1)

        QTimer.singleShot(100, check_empty_expression_error)
        MainWindow.calculate.click()

        MainWindow.mini_calculator_text.setText("quit()")
        def check_forbidden_expression():
            result = MainWindow.mini_calculator_text.text()
            translated_error = LANGUAGES[Session.language]["Errors"][13]
            self.assertTrue(Errors.forbidden_calculator_word.isVisible(), f"Mini calculator hasn't showed error {translated_error}. Result expression {result}")
            Errors.forbidden_calculator_word.done(1)

        QTimer.singleShot(100, check_forbidden_expression)
        MainWindow.calculate.click()
