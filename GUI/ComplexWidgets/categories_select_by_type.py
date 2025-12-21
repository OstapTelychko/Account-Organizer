from functools import partial
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QGraphicsDropShadowEffect,\
    QPushButton
from PySide6.QtCore import Qt

from GUI.gui_constants import ALIGN_H_CENTER, ALIGNMENT, SHADOW_EFFECT_ARGUMENTS, ALIGN_V_CENTER
from languages import LanguageStructure
from AppObjects.category import Category
from project_configuration import CATEGORY_TYPE

from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.create_wrapper_widget import create_wrapper_widget
from DesktopQtToolkit.list_widget import CustomListWidget




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
        self.categories:dict[int, CategoriesSelectionByType.CategoryItem] = {}

        self.selected_categories_list = CustomListWidget()
        self.selected_categories_list.setMinimumWidth(400)
        self.selected_categories_list.setMinimumHeight(225)

        self.add_all_incomes_categories = create_button("Add all", (150, 40))
        self.remove_all_incomes_categories = create_button("Remove all", (150, 40))

        self.add_all_incomes_categories = create_button("Add all", (150, 40))
        self.remove_all_incomes_categories = create_button("Remove all", (150, 40))

        self.incomes_buttons_layout = QHBoxLayout()
        self.incomes_buttons_layout.addWidget(self.add_all_incomes_categories, alignment=ALIGN_H_CENTER)
        self.incomes_buttons_layout.addWidget(self.remove_all_incomes_categories, alignment=ALIGN_H_CENTER)

        self.incomes_categories_list_layout = QVBoxLayout()
        self.incomes_categories_list_layout.setSpacing(15)
        self.incomes_categories_list_layout.setContentsMargins(10, 10, 20, 10)

        self.incomes_categories_layout = QVBoxLayout()
        self.incomes_categories_layout.addLayout(self.incomes_buttons_layout)
        self.incomes_categories_layout.addLayout(self.incomes_categories_list_layout)

        self.incomes_categories_list_window = QWidget()
        self.incomes_categories_list_window.setLayout(self.incomes_categories_layout)

        self.incomes_categories_list_scroll = QScrollArea()
        self.incomes_categories_list_scroll.setWidget(self.incomes_categories_list_window)
        self.incomes_categories_list_scroll.setWidgetResizable(True)
        self.incomes_categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.incomes_categories_list_scroll.setMinimumHeight(300)
        self.incomes_categories_list_scroll.setMaximumHeight(300)
        self.incomes_categories_list_scroll.setMinimumWidth(500)
        self.incomes_categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
        self.incomes_categories_list_scroll.setProperty("class", "wrapper")
        self.incomes_categories_list_scroll.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.incomes_categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS)
        )

        self.add_all_expenses_categories = create_button("Add all", (150, 40))
        self.remove_all_expenses_categories = create_button("Remove all", (150, 40))

        self.expenses_buttons_layout = QHBoxLayout()
        self.expenses_buttons_layout.addWidget(self.add_all_expenses_categories, alignment=ALIGN_H_CENTER)
        self.expenses_buttons_layout.addWidget(self.remove_all_expenses_categories, alignment=ALIGN_H_CENTER)

        self.expenses_categories_list_layout = QVBoxLayout()
        self.expenses_categories_list_layout.setSpacing(15)
        self.expenses_categories_list_layout.setContentsMargins(10, 10, 20, 10)

        self.expenses_categories_layout = QVBoxLayout()
        self.expenses_categories_layout.addLayout(self.expenses_buttons_layout)
        self.expenses_categories_layout.addLayout(self.expenses_categories_list_layout)

        self.expenses_categories_list_window = QWidget()
        self.expenses_categories_list_window.setLayout(self.expenses_categories_layout)
        
        self.expenses_categories_list_scroll = QScrollArea()
        self.expenses_categories_list_scroll.setWidget(self.expenses_categories_list_window)
        self.expenses_categories_list_scroll.setWidgetResizable(True)
        self.expenses_categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.expenses_categories_list_scroll.setMinimumHeight(300)
        self.expenses_categories_list_scroll.setMaximumHeight(300)
        self.expenses_categories_list_scroll.setMinimumWidth(500)
        self.expenses_categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
        self.expenses_categories_list_scroll.setProperty("class", "wrapper")
        self.expenses_categories_list_scroll.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.expenses_categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS)
        )

        self.categories_lists_layout = QHBoxLayout()
        self.categories_lists_layout.addWidget(self.incomes_categories_list_scroll)
        self.categories_lists_layout.addWidget(self.expenses_categories_list_scroll)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.selected_categories_list, alignment=ALIGN_H_CENTER | ALIGN_V_CENTER)
        self.main_layout.addLayout(self.categories_lists_layout)

        self.setLayout(self.main_layout)

        self.add_all_incomes_categories.clicked.connect(partial(
            self.add_all_categories_to_statistics_list, CATEGORY_TYPE[0]))
        self.add_all_expenses_categories.clicked.connect(partial(
            self.add_all_categories_to_statistics_list, CATEGORY_TYPE[1]))
        
        self.remove_all_incomes_categories.clicked.connect(partial(
            self.remove_all_categories_from_statistics_list, CATEGORY_TYPE[0]))
        self.remove_all_expenses_categories.clicked.connect(partial(
            self.remove_all_categories_from_statistics_list, CATEGORY_TYPE[1]))


    def update_selected_categories(self, selected_categories:dict[int, tuple[Category, str]]) -> None:
        """Update the selected categories list with the provided categories.

            Arguments
            ---------
                `selected_categories` (dict[int, tuple[Category, str]]): dictionary of selected categories
        """

        #Reset selected categories
        self.selected_categories_list.clear()

        for iteration, selected_category in enumerate(selected_categories):
            self.selected_categories_list.addItem(
                f"{iteration+1}. {selected_categories[selected_category][0].name} ({selected_categories[selected_category][1]})"
            )


    def add_category_to_statistics_list(
            self,
            category:Category,
            category_type_translate:str,
            remove_button:QPushButton,
            add_button:QPushButton
        ) -> None:
        """Add category to the custom range statistics list

            Arguments
            ---------
                `category` (Category): category to add to selected categories
                `category_type_translate` (str): translated category type
                `remove_button` (QPushButton): enable button to remove category
                `add_button` (QPushButton): disable button to add category
        """

        self.selected_categories_data[category.id] = (category, category_type_translate)
        selected_categories = self.selected_categories_data
        self.update_selected_categories(selected_categories)

        remove_button.setDisabled(False)
        add_button.setDisabled(True)


    def add_all_categories_to_statistics_list(self, categories_type:str) -> None:
        """Add all categories to the custom range statistics list

            Arguments
            ---------
                `categories_type` (str): type of categories to add (incomes/expenses)
        """

        add_text = LanguageStructure.GeneralManagement.get_translation(1)

        if categories_type == CATEGORY_TYPE[0]:
            for category_wrapper_index in range(self.incomes_categories_list_layout.count()):
                category_wrapper = self.incomes_categories_list_layout.itemAt(category_wrapper_index).widget()

                for widget in category_wrapper.children():
                    if isinstance(widget, QPushButton) and widget.text() == add_text:
                        widget.click()

        elif categories_type == CATEGORY_TYPE[1]:
            for category_wrapper_index in range(self.expenses_categories_list_layout.count()):
                category_wrapper = self.expenses_categories_list_layout.itemAt(category_wrapper_index).widget()

                for widget in category_wrapper.children():
                    if isinstance(widget, QPushButton) and widget.text() == add_text:
                        widget.click()


    def remove_category_from_statistics_list(
            self,
            category:Category,
            add_button:QPushButton,
            remove_button:QPushButton
        ) -> None:
        """Remove category from the custom range statistics list

            Arguments
            ---------
                `category` (Category): category to remove from selected categories
                `add_button` (QPushButton): enable button to add category
                `remove_button` (QPushButton): disable button to remove category
        """

        del self.selected_categories_data[category.id]
        selected_categories = self.selected_categories_data
        self.update_selected_categories(selected_categories)

        remove_button.setDisabled(True)
        add_button.setDisabled(False)
    

    def remove_all_categories_from_statistics_list(self, categories_type:str) -> None:
        """Remove all categories from the custom range statistics list

            Arguments
            ---------
                `categories_type` (str): type of categories to remove (incomes/expenses)
        """

        remove_text = LanguageStructure.GeneralManagement.get_translation(0)

        if categories_type == CATEGORY_TYPE[0]:
            for category_wrapper_index in range(self.incomes_categories_list_layout.count()):
                category_wrapper = self.incomes_categories_list_layout.itemAt(
                    category_wrapper_index
                ).widget()

                for widget in category_wrapper.children():
                    if isinstance(widget, QPushButton) and widget.text() == remove_text:
                        widget.click()

        elif categories_type == CATEGORY_TYPE[1]:
            for category_wrapper_index in range(self.expenses_categories_list_layout.count()):
                category_wrapper = self.expenses_categories_list_layout.itemAt(
                    category_wrapper_index
                ).widget()

                for widget in category_wrapper.children():
                    if isinstance(widget, QPushButton) and widget.text() == remove_text:
                        widget.click()


    def clear_categories_selection(self) -> None:
        """
        Clears all selected categories from the selection list and removes them from options to select.
        """

        while self.incomes_categories_list_layout.count():
            self.incomes_categories_list_layout.takeAt(0).widget().setParent(None)#type: ignore[call-overload] #MyPy doesn't recognize that None works as detaching method

        while self.expenses_categories_list_layout.count():
            self.expenses_categories_list_layout.takeAt(0).widget().setParent(None)#type: ignore[call-overload]

        self.selected_categories_list.clear()
        self.selected_categories_data.clear()


    def add_categories_to_selection(self, categories:list[Category]) -> None:
        """
        Adds categories to respective lists based on their type and allows selection.

        Args:
            categories (list[Category]): A list of categories to be added.
        """

        #Remove previous categories
        self.clear_categories_selection()

        for category in categories:
            category_item = self.CategoryItem(
                category.name,
                LanguageStructure.GeneralManagement.get_translation(0),
                LanguageStructure.GeneralManagement.get_translation(1)
            )
            self.categories[category.id] = category_item

            if category.type == CATEGORY_TYPE[0]:#Income
                category_type_translate = LanguageStructure.MainWindow.get_translation(1)
                self.incomes_categories_list_layout.addWidget(
                    category_item.category_wrapper,
                    alignment=ALIGN_V_CENTER
                )
            else:
                category_type_translate = LanguageStructure.MainWindow.get_translation(2)
                self.expenses_categories_list_layout.addWidget(
                    category_item.category_wrapper,
                    alignment=ALIGN_V_CENTER    
                )

            category_item.remove_category_button.clicked.connect(partial(
                self.remove_category_from_statistics_list,
                category, category_item.add_category_button, category_item.remove_category_button))
            category_item.add_category_button.clicked.connect(partial(
                self.add_category_to_statistics_list,
                category, category_type_translate, category_item.remove_category_button, category_item.add_category_button))
    

    def set_translation_to_add_and_remove_all_categories_buttons(self, add_text:str, remove_text:str) -> None:
        """Set translated text to add and remove all categories buttons."""

        self.add_all_expenses_categories.setText(add_text)
        self.add_all_incomes_categories.setText(add_text)
        self.remove_all_expenses_categories.setText(remove_text)
        self.remove_all_incomes_categories.setText(remove_text)
