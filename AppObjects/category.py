from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QLabel, QPushButton, QToolButton, QWidget
    from DesktopQtToolkit.table_widget import CustomTableWidget


class Category:
    """Represents a category in the application.
    It contains the `id`, `type` (income or expense), `name`, `position` (for sorting),
    and labels like `total_value_label`, `name_label`, buttons like `settings`, 
    `table_data`, `add_transaction`, `delete_transaction`, and `edit_transaction` for displaying and managing the category."""

    def __init__(
            self, 
            id:int,
            type:str,
            name:str,
            position:int,

            total_value_label:QLabel,
            name_label:QLabel,
            settings:QToolButton,
            table_data:CustomTableWidget,
            add_transaction:QPushButton,
            delete_transaction:QPushButton,
            edit_transaction:QPushButton,
            window:QWidget):
    
        self.id = id
        self.type = type
        self.name = name
        self.position = position

        self.total_value_label = total_value_label
        self.name_label = name_label
        self.settings = settings
        self.table_data = table_data
        self.add_transaction = add_transaction
        self.delete_transaction = delete_transaction
        self.edit_transaction = edit_transaction
        self.window = window