from unittest import TestCase
from datetime import datetime

from PySide6.QtCore import QTimer

from languages import LANGUAGES
from project_configuration import AVAILABLE_LANGUAGES
from AppObjects.session import Session
from tests.tests_toolkit import qsleep

from GUI.gui_constants import app
from GUI.windows.main_window import MainWindow
from GUI.windows.settings import SettingsWindow
from GUI.windows.messages import Messages
from GUI.windows.statistics import StatisticsWindow
from GUI.windows.category import AddCategoryWindow




class TestMainWindow(TestCase):

    def test_1_windows_opening(self:TestCase):
        test_windows_open = {SettingsWindow:MainWindow.settings, StatisticsWindow:MainWindow.statistics, AddCategoryWindow:MainWindow.add_incomes_category}

        for window, open_window_button in test_windows_open.items():
            window_object = getattr(window, "window")

            def check_window_appearance():
                self.assertTrue(window_object.isVisible(), f"Window {window.__name__} hasn't showed after click on button {open_window_button.text()}")
                window_object.done(1)

            QTimer.singleShot(100, check_window_appearance)# Timer will call this function after 100 milliseconds. QDialog use exec to show up so it block program loop
            open_window_button.click()
        
        qsleep(500)


    def test_2_date_change(self):
        months_list = LANGUAGES[Session.language]["Months"]
        current_month = datetime.now().month
        translated_current_month = months_list[current_month]

        current_showed_month = MainWindow.current_month.text()
        self.assertEqual(translated_current_month, current_showed_month, f"Wrong current month has been showed {current_showed_month} instead of {translated_current_month}")

        translated_next_month = months_list[current_month+1] if current_month != 12 else months_list[1]
        MainWindow.next_month_button.click()
        current_showed_month = MainWindow.current_month.text()
        self.assertEqual(translated_next_month, current_showed_month, f"Wrong next month has been showed {current_showed_month} instead of {translated_next_month}")
        
        translated_previous_month = months_list[current_month]
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
    

    def test_3_mini_calculator(self):
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
        translated_warning = LANGUAGES[Session.language]["Windows"]["Main"]["Mini calculator"][2]
        self.assertEqual(translated_warning, result, f"Mini calculator has returned wrong result for incorrect expression {result} instead of {translated_warning}")

        MainWindow.mini_calculator_text.setText("5/0")
        MainWindow.calculate.click()
        result = MainWindow.mini_calculator_text.text()
        translated_warning = LANGUAGES[Session.language]["Windows"]["Main"]["Mini calculator"][1]
        self.assertEqual(translated_warning, result, f"Mini calculator has returned wrong result for division by zero {result} instead of {translated_warning}")

        MainWindow.mini_calculator_text.setText("")
        def check_empty_expression_error():
            result = MainWindow.mini_calculator_text.text()
            translated_message = LANGUAGES[Session.language]["Messages"][12]
            self.assertTrue(Messages.empty_expression.isVisible(), f"Mini calculator hasn't showed error {translated_message}. Result expression {result}")
            Messages.empty_expression.done(1)

        QTimer.singleShot(100, check_empty_expression_error)
        MainWindow.calculate.click()

        MainWindow.mini_calculator_text.setText("quit()")
        def check_forbidden_expression():
            result = MainWindow.mini_calculator_text.text()
            translated_message = LANGUAGES[Session.language]["Messages"][13]
            self.assertTrue(Messages.forbidden_calculator_word.isVisible(), f"Mini calculator hasn't showed error {translated_message}. Result expression {result}")
            Messages.forbidden_calculator_word.done(1)

        QTimer.singleShot(100, check_forbidden_expression)
        MainWindow.calculate.click()
        qsleep(500)


    def test_4_language_change(self):
        all_languages = AVAILABLE_LANGUAGES.copy()
        all_languages.remove(Session.language)
        previous_language = Session.language
        language_to_change = all_languages[0]

        def open_settings():
            SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(language_to_change))
            expected_translation = LANGUAGES[language_to_change]["Windows"]["Settings"][0]
            result = SettingsWindow.window.windowTitle()

            self.assertEqual(result, expected_translation, f"Language has't been changed. Expected translation {expected_translation} not {result}")
            SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(previous_language))
            SettingsWindow.window.done(1)

        QTimer.singleShot(100, open_settings)
        MainWindow.settings.click()
        qsleep(500)
    

    def test_5_theme_change(self):
        def open_settings():
            current_theme = Session.theme
            current_style_sheet = app.styleSheet()
            current_theme_icon = SettingsWindow.switch_themes_button.icon()

            SettingsWindow.switch_themes_button.click()

            self.assertNotEqual(current_theme, Session.theme, f"Session theme hasn't changed. Theme {current_theme}")
            self.assertNotEqual(current_style_sheet, app.styleSheet(), f"App style sheet hasn't changed.")
            self.assertNotEqual(current_theme_icon, SettingsWindow.switch_themes_button.icon(), f"Theme icon  hasn't changed.")

            SettingsWindow.switch_themes_button.click()
            SettingsWindow.window.done(1)
        
        QTimer.singleShot(100, open_settings)
        MainWindow.settings.click()
        qsleep(500)
