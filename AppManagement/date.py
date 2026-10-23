from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry

from languages import LanguageStructure
from AppManagement.category import load_categories_data
from AppManagement.information_message import show_information_message


logger = get_logger(__name__)

def show_date_change_message(month_changed:bool, year_changed:bool) -> None:
    """Show the information message about the changed month and/or year.

        Arguments
        ---------
            `month_changed` : (bool) - Whether the viewed month changed.
            `year_changed` : (bool) - Whether the viewed year changed.
    """

    app_core = AppCore.instance()
    lines:list[str] = []
    if month_changed:
        lines.append(
            LanguageStructure.DateChange.get_translation(0).replace(
                "%month%", LanguageStructure.Months.get_translation(app_core.current_month)
            )
        )
    if year_changed:
        lines.append(LanguageStructure.DateChange.get_translation(1).replace("%year%", str(app_core.current_year)))

    if lines:
        show_information_message("\n".join(lines))


def set_month_and_year(month:int, year:int) -> None:
    """Load the given month and year. Shows a message only for the parts that actually changed.

        Arguments
        ---------
            `month` : (int) - Month to load (1-12).
            `year` : (int) - Year to load.
    """

    app_core = AppCore.instance()
    month_changed = month != app_core.current_month
    year_changed = year != app_core.current_year
    if not month_changed and not year_changed:
        return

    app_core.current_month = month
    app_core.current_year = year
    WindowsRegistry.MainWindow.current_month.setText(LanguageStructure.Months.get_translation(month))
    WindowsRegistry.MainWindow.current_year.setText(str(year))
    load_categories_data()
    show_date_change_message(month_changed, year_changed)
    logger.info(f"Month and year loaded: {month}-{year}")


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
    show_date_change_message(True, False)
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
    show_date_change_message(True, False)
    logger.info(f"Previous month loaded: {LanguageStructure.Months.get_translation(app_core.current_month)}")


def next_year() -> None:
    """Load next year. If current year is 2023, load 2024."""

    app_core = AppCore.instance()
    app_core.current_year += 1
    WindowsRegistry.MainWindow.current_year.setText(str(app_core.current_year))
    load_categories_data()
    show_date_change_message(False, True)
    logger.info(f"Next year loaded: {app_core.current_year}")


def previous_year() -> None:
    """Load previous year. If current year is 2024, load 2023."""
    
    app_core = AppCore.instance()
    app_core.current_year -= 1
    WindowsRegistry.MainWindow.current_year.setText(str(app_core.current_year))
    load_categories_data()
    show_date_change_message(False, True)
    logger.info(f"Previous year loaded: {app_core.current_year}")