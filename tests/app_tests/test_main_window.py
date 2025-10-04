from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from PySide6.QtCore import QTimer

from languages import LanguageStructure
from project_configuration import AVAILABLE_LANGUAGES
from AppObjects.app_core import AppCore
from AppObjects.windows_registry import WindowsRegistry
from tests.tests_toolkit import qsleep, OutOfScopeTestCase

from GUI.gui_constants import app

if TYPE_CHECKING:
    from PySide6.QtWidgets import QPushButton, QToolButton
    from DesktopQtToolkit.sub_window import SubWindow



class TestMainWindow(OutOfScopeTestCase):
    """Test main window of the application."""

    def test_1_windows_opening(self) -> None:
        """Test opening windows from main window."""

        test_windows_open:dict[SubWindow, QPushButton | QToolButton] = {
            WindowsRegistry.SettingsWindow:WindowsRegistry.MainWindow.settings,
            WindowsRegistry.StatisticsWindow:WindowsRegistry.MainWindow.statistics,
            WindowsRegistry.AddCategoryWindow:WindowsRegistry.MainWindow.add_incomes_category
        }

        for window, open_window_button in test_windows_open.items():

            def _check_window_appearance() -> None:
                """Check if window is visible after clicking button."""

                self.assertTrue(
                    window.isVisible(),
                    f"Window {window.__class__.__name__} hasn't showed after click on button {open_window_button.text()}"
                )
                window.done(1)
            
            QTimer.singleShot(100, self.catch_failure(_check_window_appearance))# Timer will call this function after 100 milliseconds. QDialog use exec to show up so it block program loop
            open_window_button.click()
        
        qsleep(500)


    def test_2_date_change(self) -> None:
        """Test changing date in the application."""

        current_month = datetime.now().month
        translated_current_month = LanguageStructure.Months.get_translation(current_month)

        current_showed_month = WindowsRegistry.MainWindow.current_month.text()
        self.assertEqual(
            translated_current_month,
            current_showed_month,
            f"Wrong current month has been showed {current_showed_month} instead of {translated_current_month}"
        )

        translated_next_month = LanguageStructure.Months.get_translation(current_month+1) if current_month != 12 else LanguageStructure.Months.get_translation(1)
        WindowsRegistry.MainWindow.next_month_button.click()
        current_showed_month = WindowsRegistry.MainWindow.current_month.text()
        self.assertEqual(
            translated_next_month,
            current_showed_month,
            f"Wrong next month has been showed {current_showed_month} instead of {translated_next_month}"
        )
        
        translated_previous_month = LanguageStructure.Months.get_translation(current_month)
        WindowsRegistry.MainWindow.previous_month_button.click()
        current_showed_month = WindowsRegistry.MainWindow.current_month.text()
        self.assertEqual(
            translated_previous_month,
            current_showed_month,
            f"Wrong previous month has been showed {current_showed_month} instead of {translated_previous_month}"
        )

        current_year = datetime.now().year
        current_showed_year = WindowsRegistry.MainWindow.current_year.text()
        self.assertEqual(
            str(current_year),
            current_showed_year,
            f"Wrong current year has been showed {current_showed_year} instead of {current_year}"
        )

        WindowsRegistry.MainWindow.next_year_button.click()
        current_showed_year = WindowsRegistry.MainWindow.current_year.text()
        self.assertEqual(
            str(current_year+1),
            current_showed_year,
            f"Wrong next year has been showed {current_showed_year} instead of {current_year+1}"
        )
        
        WindowsRegistry.MainWindow.previous_year_button.click()
        current_showed_year = WindowsRegistry.MainWindow.current_year.text()
        self.assertEqual(
            str(current_year),
            current_showed_year,
            f"Wrong previous year has been showed {current_showed_year} instead of {current_year}"
        )
    

    def test_3_mini_calculator(self) -> None:
        """Test mini calculator in the application."""

        WindowsRegistry.MainWindow.mini_calculator_text.setText("2*2")
        WindowsRegistry.MainWindow.calculate.click()
        result = WindowsRegistry.MainWindow.mini_calculator_text.text()
        self.assertEqual(
            "4", result, f"Mini calculator has returned wrong result for expression 2*2 {result} instead of 4"
        )

        WindowsRegistry.MainWindow.mini_calculator_text.setText("100+300+400+500")
        WindowsRegistry.MainWindow.calculate.click()
        result = WindowsRegistry.MainWindow.mini_calculator_text.text()
        self.assertEqual(
            "1300",
            result,
            f"Mini calculator has returned wrong result for expression 100+300+400+500 {result} instead of 1300"
        )

        WindowsRegistry.MainWindow.mini_calculator_text.setText("1000Money+friends")
        WindowsRegistry.MainWindow.calculate.click()
        result = WindowsRegistry.MainWindow.mini_calculator_text.text()
        translated_warning = LanguageStructure.MiniCalculator.get_translation(2)
        self.assertEqual(
            translated_warning,
            result,
            f"Mini calculator has returned wrong result for incorrect expression {result} instead of {translated_warning}"
        )

        WindowsRegistry.MainWindow.mini_calculator_text.setText("5/0")
        WindowsRegistry.MainWindow.calculate.click()
        result = WindowsRegistry.MainWindow.mini_calculator_text.text()
        translated_warning = LanguageStructure.MiniCalculator.get_translation(1)
        self.assertEqual(
            translated_warning,
            result,
            f"Mini calculator has returned wrong result for division by zero {result} instead of {translated_warning}"
        )

        WindowsRegistry.MainWindow.mini_calculator_text.setText("")
        def _check_empty_expression_error() -> None:
            """Check if empty expression error is shown."""

            result = WindowsRegistry.MainWindow.mini_calculator_text.text()
            translated_message = LanguageStructure.Messages.get_translation(12)
            self.assertTrue(
                WindowsRegistry.Messages.empty_expression.isVisible(),
                f"Mini calculator hasn't showed error {translated_message}. Result expression {result}"
            )
            WindowsRegistry.Messages.empty_expression.done(1)

        QTimer.singleShot(100, self.catch_failure(_check_empty_expression_error))
        WindowsRegistry.MainWindow.calculate.click()

        WindowsRegistry.MainWindow.mini_calculator_text.setText("quit()")
        def _check_forbidden_expression() -> None:
            """Check if forbidden expression error is shown."""

            result = WindowsRegistry.MainWindow.mini_calculator_text.text()
            translated_message = LanguageStructure.Messages.get_translation(13)
            self.assertTrue(
                WindowsRegistry.Messages.forbidden_calculator_word.isVisible(),
                f"Mini calculator hasn't showed error {translated_message}. Result expression {result}"
            )
            WindowsRegistry.Messages.forbidden_calculator_word.done(1)

        QTimer.singleShot(100, self.catch_failure(_check_forbidden_expression))
        WindowsRegistry.MainWindow.calculate.click()
        qsleep(500)


    def test_4_language_change(self) -> None:
        """Test changing language in the application."""

        app_core = AppCore.instance()
        all_languages = AVAILABLE_LANGUAGES.copy()
        all_languages.remove(app_core.config.language)
        previous_language = app_core.config.language
        language_to_change = all_languages[0]

        def _open_settings() -> None:
            """Change language in the application."""

            WindowsRegistry.SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(language_to_change))
            expected_translation = LanguageStructure.Settings.get_translation(0)
            result = WindowsRegistry.SettingsWindow.windowTitle()

            self.assertEqual(
                result,
                expected_translation,
                f"Language has't been changed. Expected translation {expected_translation} not {result}"
            )
            WindowsRegistry.SettingsWindow.languages.setCurrentIndex(AVAILABLE_LANGUAGES.index(previous_language))
            WindowsRegistry.SettingsWindow.done(1)

        QTimer.singleShot(100, self.catch_failure(_open_settings))
        WindowsRegistry.MainWindow.settings.click()
        qsleep(500)
    

    def test_5_theme_change(self) -> None:
        """Test changing theme in the application."""

        app_core = AppCore.instance() 
        def _open_settings() -> None:
            """Change theme in the application."""

            current_theme = app_core.config.theme
            current_style_sheet = app.styleSheet()
            current_theme_icon = WindowsRegistry.SettingsWindow.switch_themes_button.icon()

            WindowsRegistry.SettingsWindow.switch_themes_button.click()

            self.assertNotEqual(
                current_theme, app_core.config.theme, f"Session theme hasn't changed. Theme {current_theme}"
            )
            self.assertNotEqual(current_style_sheet, app.styleSheet(), f"App style sheet hasn't changed.")
            self.assertNotEqual(
                current_theme_icon,
                WindowsRegistry.SettingsWindow.switch_themes_button.icon(),
                f"Theme icon  hasn't changed."
            )

            WindowsRegistry.SettingsWindow.switch_themes_button.click()
            WindowsRegistry.SettingsWindow.done(1)
        
        QTimer.singleShot(100, self.catch_failure(_open_settings))
        WindowsRegistry.MainWindow.settings.click()
        qsleep(500)
