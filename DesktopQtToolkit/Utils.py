from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from DesktopQtToolkit.table_widget import CustomTableWidget
    from PySide6.QtWidgets import QTableWidgetItem, QLayout



def get_table_widget_item(table_widget: CustomTableWidget, row: int, column: int) -> QTableWidgetItem:
    """Get the item from the table widget at the specified row and column."""
    item = table_widget.item(row, column)
    if item is None:
        raise ValueError(f"No item found at row {row} and column {column}.")
    return item


def get_widget_from_layout(layout: QLayout, index: int) -> QWidget:
    """Get the widget from the layout at the specified index."""
    item = layout.itemAt(index)
    if item is None:
        raise ValueError(f"No item found at index {index}.")
    widget = item.widget()
    if widget is None:
        raise ValueError(f"No widget found at index {index}.")
    return widget