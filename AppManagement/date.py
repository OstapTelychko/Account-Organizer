from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from languages import LanguageStructure
from AppManagement.category import load_categories_data


logger = get_logger(__name__)

def next_month() -> None:
    """Load next month. If current month is December, load January."""

    app_core = AppCore.instance()
    if app_core.current_month != 12:
        app_core.current_month +=1
        WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(app_core.current_month))
    else:
        WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(1))
        app_core.current_month = 1
    load_categories_data()
    logger.info(f"Next month loaded: {LanguageStructure.Months.get_translation(app_core.current_month)}")


def previous_month() -> None:
    """Load previous month. If current month is January, load December."""

    app_core = AppCore.instance()
    app_core.current_month -= 1
    if app_core.current_month != 0:
        WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(app_core.current_month))
    else:
        WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(12))
        app_core.current_month = 12
    load_categories_data()
    logger.info(f"Previous month loaded: {LanguageStructure.Months.get_translation(app_core.current_month)}")


def next_year() -> None:
    """Load next year. If current year is 2023, load 2024."""

    app_core = AppCore.instance()
    app_core.current_year += 1
    WindowsRegistry.MainWindow.current_year.setText(str(app_core.current_year))
    load_categories_data()
    logger.info(f"Next year loaded: {app_core.current_year}")


def previous_year() -> None:
    """Load previous year. If current year is 2024, load 2023."""
    
    app_core = AppCore.instance()
    app_core.current_year -= 1
    WindowsRegistry.MainWindow.current_year.setText(str(app_core.current_year))
    load_categories_data()
    logger.info(f"Previous year loaded: {app_core.current_year}")