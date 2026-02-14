from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QWidget
from PySide6.QtCore import Qt

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.shortcut_edit import ShortcutCaptureEdit
from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS, ALIGN_H_CENTER

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class ShortcutsWindow(SubWindow):

    class ShortcutWidget(QWidget):
        def __init__(self, parent:QWidget|None=None) -> None:
            super().__init__(parent)
            
            self.shortcut_name = QLabel()
            self.shortcut_name.setProperty("class", "light-text")

            self.shortcut_description = QLabel()
            self.shortcut_description.setProperty("class", "light-text")
            self.shortcut_description.setWordWrap(True)
            
            self.shortcut_info_layout = QVBoxLayout()
            self.shortcut_info_layout.addWidget(self.shortcut_name)
            self.shortcut_info_layout.addWidget(self.shortcut_description)

            self.shortcut_edit = ShortcutCaptureEdit()
            self.reset_shortcut = create_button("Reset", (100, 40))
            
            self.shortcut_edit_layout = QHBoxLayout()
            self.shortcut_edit_layout.addWidget(self.shortcut_edit)
            self.shortcut_edit_layout.addWidget(self.reset_shortcut)

            self.shortcut_layout = QVBoxLayout()
            self.shortcut_layout.addLayout(self.shortcut_info_layout)
            self.shortcut_layout.addLayout(self.shortcut_edit_layout)

            self.setLayout(self.shortcut_layout)



    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.close_current_window_shortcut = self.ShortcutWidget()
        self.open_settings_shortcut = self.ShortcutWidget()
        self.open_statistics_shortcut = self.ShortcutWidget()
        self.switch_account_shortcut = self.ShortcutWidget()
        self.switch_to_income_shortcut = self.ShortcutWidget()
        self.switch_to_expense_shortcut = self.ShortcutWidget()
        self.load_previous_month_shortcut = self.ShortcutWidget()
        self.load_next_month_shortcut = self.ShortcutWidget()
        self.focus_on_next_category_shortcut = self.ShortcutWidget()
        self.focus_on_previous_category_shortcut = self.ShortcutWidget()
        self.add_transaction_to_focused_category_shortcut = self.ShortcutWidget()
        self.select_previous_transaction_shortcut = self.ShortcutWidget()
        self.select_next_transaction_shortcut = self.ShortcutWidget()
        self.delete_transaction_shortcut = self.ShortcutWidget()
        self.edit_transaction_shortcut = self.ShortcutWidget()
        self.open_search_shortcut = self.ShortcutWidget()
        
        self.shortcuts_layout = QVBoxLayout()
        self.shortcuts_layout.addWidget(self.close_current_window_shortcut)
        self.shortcuts_layout.addWidget(self.open_settings_shortcut)
        self.shortcuts_layout.addWidget(self.open_statistics_shortcut)
        self.shortcuts_layout.addWidget(self.switch_account_shortcut)
        self.shortcuts_layout.addWidget(self.switch_to_income_shortcut)
        self.shortcuts_layout.addWidget(self.switch_to_expense_shortcut)
        self.shortcuts_layout.addWidget(self.load_previous_month_shortcut)
        self.shortcuts_layout.addWidget(self.load_next_month_shortcut)
        self.shortcuts_layout.addWidget(self.focus_on_next_category_shortcut)
        self.shortcuts_layout.addWidget(self.focus_on_previous_category_shortcut)
        self.shortcuts_layout.addWidget(self.add_transaction_to_focused_category_shortcut)
        self.shortcuts_layout.addWidget(self.select_previous_transaction_shortcut)
        self.shortcuts_layout.addWidget(self.select_next_transaction_shortcut)
        self.shortcuts_layout.addWidget(self.delete_transaction_shortcut)
        self.shortcuts_layout.addWidget(self.edit_transaction_shortcut)
        self.shortcuts_layout.addWidget(self.open_search_shortcut)

        self.shortcuts_container = QWidget()
        self.shortcuts_container.setProperty("class", "wrapper")
        self.shortcuts_container.setLayout(self.shortcuts_layout)

        self.shortcuts_scroll = QScrollArea()
        self.shortcuts_scroll.setWidget(self.shortcuts_container)
        self.shortcuts_scroll.setWidgetResizable(True)
        self.shortcuts_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.shortcuts_scroll.setGraphicsEffect(QGraphicsDropShadowEffect(self, **SHADOW_EFFECT_ARGUMENTS)) 
        self.shortcuts_scroll.setMinimumHeight(400)
        self.shortcuts_scroll.setMinimumWidth(450)
        self.shortcuts_scroll.setProperty("class", "wrapper")

        self.save_shortcuts = create_button("Save", (100, 40))

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.shortcuts_scroll)
        self.main_layout.addWidget(self.save_shortcuts, alignment=ALIGN_H_CENTER)
        self.main_layout.setContentsMargins(30, 10, 30, 30)

        self.window_container.setLayout(self.main_layout)
