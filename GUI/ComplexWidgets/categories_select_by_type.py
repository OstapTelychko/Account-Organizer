from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from GUI.gui_constants import ALIGN_H_CENTER, ALIGNMENT
from AppObjects.category import Category
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget




class CategoriesSelectionByType(QWidget):
    """Complex widget for selecting categories by type (income/expense)."""

    class CategoryItem(QWidget):
        """Represents a category item in the categories list."""
    
        def __init__(self, category_name:str, remove_category_label:str, add_category_label:str) -> None:
            super().__init__()

            self.category_name = QLabel(category_name)
            self.category_name.setProperty("class", "light-text")
            self.category_name.setWordWrap(True)
            self.category_name.setMinimumWidth(200)

            self.remove_category_button = create_button(remove_category_label, (100, 40))
            self.remove_category_button.setDisabled(True)

            self.add_category_button = create_button(add_category_label, (100, 40))

            self.category_layout = QHBoxLayout()
            self.category_layout.addWidget(self.category_name, alignment=ALIGN_H_CENTER)
            self.category_layout.addWidget(self.add_category_button, alignment=ALIGNMENT.AlignRight)
            self.category_layout.addWidget(self.remove_category_button, alignment=ALIGNMENT.AlignRight)

            self.category_wrapper = create_wrapper_widget(self.category_layout, "category_list_item")
    
    def __init__(self) -> None:
        super().__init__()

        self.selected_categories_data:dict[int, tuple[Category, str]] = {}