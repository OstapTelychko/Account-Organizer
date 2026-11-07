from datetime import date
from calendar import monthrange
from PySide6.QtCore import Qt

from AppObjects.app_core import AppCore
from AppObjects.logger import get_logger
from AppObjects.windows_registry import WindowsRegistry
from DesktopQtToolkit.table_widget import CustomTableWidgetItem
from DesktopQtToolkit.Utils import get_table_widget_item

from languages import LanguageStructure
from project_configuration import CategoryType, InvestmentOperation
from backend.models import Transaction
from backend.investment_query import calculate_investment_timeline
from GeneralTools.Utils import generate_month_range
from GUI.gui_constants import ALIGNMENT

from AppManagement.balance import calculate_current_balance
from AppManagement.category import update_category_total_value



logger = get_logger(__name__)

def show_monthly_investments_window(total_amount:float|None = None) -> int:
    """Show Monthly investments window with all Investments categories of the account and their values
    at the end of the viewed month.

        Arguments
        ---------
            `total_amount` : (float|None) - Amount to distribute between categories. Defaults to empty.
    """

    app_core = AppCore.instance()
    window = WindowsRegistry.MonthlyInvestmentsWindow
    investment_categories = sorted(
        (category for category in app_core.categories.values() if category.type == CategoryType.Investment),
        key=lambda category: category.position
    )
    categories_values = app_core.db.investment_query.get_categories_values(
        [category.id for category in investment_categories],
        generate_month_range(app_core.current_year, app_core.current_month)[1]
    )

    table = window.investments_table
    table.blockSignals(True)
    table.setSortingEnabled(False)
    table.setRowCount(0)
    table.setRowCount(len(investment_categories))
    for row, category in enumerate(investment_categories):
        for column, text in enumerate((category.name, str(categories_values[category.id]), "", "", str(category.id))):
            item = CustomTableWidgetItem(text)
            if column in (0, 1, 4):
                item.setFlags(~ Qt.ItemFlag.ItemIsEditable)
            if column != 0:
                item.setTextAlignment(ALIGNMENT.AlignCenter)
            table.setItem(row, column, item)
    table.blockSignals(False)

    today = date.today()
    is_current_month = (app_core.current_year, app_core.current_month) == (today.year, today.month)
    window.operations_day.setText(str(today.day) if is_current_month else "")
    window.total_amount.setText("" if total_amount is None else str(total_amount))
    update_monthly_investments_remaining()

    window.setWindowTitle(LanguageStructure.Investments.get_translation(13))
    return window.exec()


def update_monthly_investments_remaining() -> None:
    """Show the part of the total amount that isn't deposited yet. The label is empty if there is no total amount."""

    window = WindowsRegistry.MonthlyInvestmentsWindow
    try:
        remaining = float(window.total_amount.text().replace(",", "."))
    except ValueError:
        window.remaining_amount.setText("")
        return

    for row in range(window.investments_table.rowCount()):
        try:
            remaining -= float(get_table_widget_item(window.investments_table, row, 2).text().replace(",", "."))
        except ValueError:
            continue
    window.remaining_amount.setText(LanguageStructure.Investments.get_translation(17) + str(round(remaining, 2)))


def save_monthly_investments() -> int:
    """Validate deposits and new values of all rows of Monthly investments window and save them.
    Nothing is saved if any row is invalid.
    """

    app_core = AppCore.instance()
    window = WindowsRegistry.MonthlyInvestmentsWindow
    raw_day = window.operations_day.text()

    if raw_day == "":
        return WindowsRegistry.Messages.empty_fields.exec()

    _, max_month_day = monthrange(app_core.current_year, app_core.current_month)
    if not 0 < int(raw_day) <= max_month_day:
        WindowsRegistry.Messages.day_out_range.setText(LanguageStructure.Messages.get_translation(8)+f"1-{max_month_day}")
        return WindowsRegistry.Messages.day_out_range.exec()

    operations_date = date(app_core.current_year, app_core.current_month, int(raw_day))
    if operations_date > date.today():
        return WindowsRegistry.Messages.future_investment_operation.exec()

    categories_operations:dict[int, list[Transaction]] = {}
    for row in range(window.investments_table.rowCount()):
        category_id = int(get_table_widget_item(window.investments_table, row, 4).text())
        operations:list[Transaction] = []
        for column, operation_type in ((2, InvestmentOperation.Deposit), (3, InvestmentOperation.Revaluation)):
            raw_value = get_table_widget_item(window.investments_table, row, column).text().strip().replace(",", ".")
            if raw_value == "":
                continue
            try:
                value = round(float(raw_value), 2)
            except ValueError:
                return WindowsRegistry.Messages.incorrect_data_type.exec()
            if value < 0:
                return WindowsRegistry.Messages.incorrect_data_type.exec()
            if operation_type == InvestmentOperation.Deposit and value == 0:
                return WindowsRegistry.Messages.zero_investment_value.exec()
            operations.append(Transaction(
                date=operations_date, value=value, name="", operation_type=operation_type, category_id=category_id
            ))
        if operations:
            categories_operations[category_id] = operations

    if not categories_operations:
        return WindowsRegistry.Messages.empty_fields.exec()

    for category_id, operations in categories_operations.items():
        timeline = calculate_investment_timeline(
            app_core.db.transaction_query.get_all_transactions(category_id) + operations
        )
        if any(point.value_after < 0 for point in timeline):
            return WindowsRegistry.Messages.negative_investment_value.exec()

    for category_id, operations in categories_operations.items():
        for operation in operations:
            app_core.db.transaction_query.add_transaction(
                category_id, operation.date, operation.value, "", operation.operation_type
            )
            logger.info(
                f"[ENTITY: INVESTMENT] [ACTION: {InvestmentOperation(operation.operation_type).name.upper()}] "
                f"date={operation.date} value={operation.value} category_id={category_id}"
            )
        update_category_total_value(category_id)

    calculate_current_balance()
    window.hide()
    return 1
