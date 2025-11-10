from __future__ import annotations
"""MIT License with Non-Monetization Clause

Copyright (c) 2024 - present Ostap Telychko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

2. The Software and any modifications thereof shall not be sold, licensed for a fee,
or monetized in any way. Commercial use is permitted only if the Software remains
freely available to end users.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QTabWidget, QToolButton,QSizePolicy,\
    QGraphicsDropShadowEffect

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

from project_configuration import GENERAL_ICONS_DIRECTORY
from DesktopQtToolkit.qsingleton import QSingleton
from GUI.gui_constants import ALIGNMENT, ALIGN_H_CENTER, ICON_SIZE, APP_ICON, BASIC_FONT, SHADOW_EFFECT_ARGUMENTS,\
BIG_BASIC_FONT

from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button
from DesktopQtToolkit.horizontal_scroll_area import HorizontalScrollArea

if TYPE_CHECKING:
    from PySide6.QtGui import QMoveEvent
    from DesktopQtToolkit.message_window import MessageWindow



class MainWindow(QWidget, metaclass=QSingleton):
    """Represents main window structure.

        Warning
        -------
        This class contains non-GUI related objects like `sub_windows` and `message_windows`.
        
        `sub_windows` - is a dictionary that contains all sub windows.

        `message_windows` - is a dictionary that contains all message windows.

        `singleton_message` - is a message that will be displayed when trying to create multiple instances of the class.
    """

    singleton_message = "Main window is already created. Use WindowsRegistry instead."

    def __init__(self) -> None:
        super().__init__()
        self.resize(1500, 770)
        self.setMinimumHeight(770)
        self.setMinimumWidth(900)
        self.setWindowTitle("Account Organizer")
        self.setWindowIcon(APP_ICON)
        self.setWindowFlags(Qt.WindowType.NoDropShadowWindowHint)
        self.setObjectName("main_window")

        #Account balance and settings
        self.account_current_balance = QLabel("Balance: 0")
        self.account_current_balance.setFont(BIG_BASIC_FONT)

        self.settings = QToolButton()
        self.settings.setIcon(QIcon(os.path.join(GENERAL_ICONS_DIRECTORY, "Settings icon.png")))
        self.settings.setIconSize(ICON_SIZE)

        #Year and month
        self.previous_year_button = create_button("<",(32,30))
        self.next_year_button = create_button(">",(32,30))

        self.current_year = QLabel("2023")
        self.current_year.setFont(BASIC_FONT)
        self.current_year.setProperty("class", "light-text")

        self.Year_layout = QHBoxLayout()
        self.Year_layout.addWidget(self.previous_year_button,alignment=ALIGN_H_CENTER | ALIGNMENT.AlignTop)
        self.Year_layout.addWidget(self.current_year, 1, alignment=ALIGN_H_CENTER | ALIGNMENT.AlignVCenter)
        self.Year_layout.addWidget(self.next_year_button,alignment=ALIGN_H_CENTER | ALIGNMENT.AlignTop)

        self.previous_month_button = create_button("<",(30,30))
        self.next_month_button = create_button(">",(30,30))

        self.current_month = QLabel("April")
        self.current_month.setFont(BASIC_FONT)
        self.current_month.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.current_month.setMinimumWidth(100)
        self.current_month.setProperty("class", "light-text")
        self.current_month.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.Month_layout = QHBoxLayout()
        self.Month_layout.addWidget(self.previous_month_button, alignment=ALIGNMENT.AlignLeft)
        self.Month_layout.addWidget(self.current_month, alignment=ALIGN_H_CENTER)
        self.Month_layout.addWidget(self.next_month_button, alignment=ALIGNMENT.AlignRight)

        self.Date_management_layout = QVBoxLayout()
        self.Date_management_layout.addLayout(self.Year_layout)
        self.Date_management_layout.addLayout(self.Month_layout)

        self.Date_management_wrapper = QWidget()
        self.Date_management_wrapper.setProperty("class", "wrapper")
        self.Date_management_wrapper.setGraphicsEffect(
            QGraphicsDropShadowEffect(self.Date_management_wrapper, **SHADOW_EFFECT_ARGUMENTS)
        )
        self.Date_management_wrapper.setLayout(self.Date_management_layout)

        #Income and expenses windows 
        self.Incomes_and_expenses = QTabWidget()
        self.Incomes_and_expenses.setFont(BASIC_FONT)

        self.Incomes_window = QWidget()
        self.Incomes_window.setContentsMargins(0, 10, 0, 10)
        self.Incomes_window.setMinimumHeight(350)
        
        self.add_incomes_category = create_button("Create category",(170,40))

        self.Incomes_window_layout = QHBoxLayout()
        self.Incomes_window_layout.addWidget(self.add_incomes_category)

        self.Incomes_window_layout.setSpacing(70)
        self.Incomes_window.setLayout(self.Incomes_window_layout)

        self.Incomes_scroll = HorizontalScrollArea()
        self.Incomes_scroll.setWidget(self.Incomes_window)
        self.Incomes_scroll.setWidgetResizable(True)
        self.Incomes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.Incomes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.Incomes_scroll.setObjectName("Income-window")
        self.Incomes_scroll.setStyleSheet("#Income-window{ border-color:rgba(0,205,0,100); border-width:2px }")
            
        self.Expenses_window = QWidget()
        self.Expenses_window.setContentsMargins(0, 10, 0, 10)

        self.add_expenses_category = create_button("Create category",(170,40))

        self.Expenses_window_layout = QHBoxLayout()
        self.Expenses_window_layout.addWidget(self.add_expenses_category)
            
        self.Expenses_window_layout.setSpacing(70)
        self.Expenses_window.setLayout(self.Expenses_window_layout)

        self.Expenses_scroll = HorizontalScrollArea()
        self.Expenses_scroll.setWidget(self.Expenses_window)
        self.Expenses_scroll.setWidgetResizable(True)
        self.Expenses_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.Expenses_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.Expenses_scroll.setObjectName("Expenses-window")
        self.Expenses_scroll.setStyleSheet("#Expenses-window{ border-color:rgba(205,0,0,100); border-width:2px }")

        self.Incomes_and_expenses.addTab(self.Incomes_scroll,"Income")
        self.Incomes_and_expenses.addTab(self.Expenses_scroll,"Expenses")
        self.Incomes_and_expenses.setMinimumHeight(500)
        self.Incomes_and_expenses.setObjectName("Incomes-and-expenses")
        self.Incomes_and_expenses.setStyleSheet("QTabWidget::pane{border:none}")

        self.window_bottom = QHBoxLayout()
        self.statistics = create_button("Statistics",(160,40))
        self.search = create_button("Search",(100,40))

        self.mini_calculator_label = QLabel("Mini-calculator")
        self.mini_calculator_label.setFont(BASIC_FONT)
        self.mini_calculator_text = QLineEdit()
        self.mini_calculator_text.setPlaceholderText("2 * 3 = 6;  3 / 2 = 1.5;  3 + 2 = 5;  2 - 3 = -1;  4 ** 2 = 16")
        self.mini_calculator_text.setMinimumWidth(400)

        self.calculate = create_button("=",(100,40))
        self.calculate.setFont(BIG_BASIC_FONT)
        
        self.window_bottom.addStretch(1)
        self.window_bottom.addWidget(self.statistics)
        self.window_bottom.addWidget(self.search)
        self.window_bottom.addStretch(5)
        self.window_bottom.addWidget(self.mini_calculator_label)
        self.window_bottom.addWidget(self.mini_calculator_text)
        self.window_bottom.addWidget(self.calculate)
        self.window_bottom.addStretch(1)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.settings, alignment=ALIGNMENT.AlignTop | ALIGNMENT.AlignRight)
        self.main_layout.addWidget(self.account_current_balance, alignment=ALIGN_H_CENTER | ALIGNMENT.AlignTop)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(self.Date_management_wrapper, alignment=ALIGN_H_CENTER)
        self.main_layout.addWidget(self.Incomes_and_expenses)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.window_bottom)
        self.main_layout.addStretch(1)

        self.setLayout(self.main_layout)

        self.sub_windows:dict[int, SubWindow] = dict()
        self.message_windows:dict[int, MessageWindow] = dict()
    

    def moveEvent(self, event:QMoveEvent) -> None:
        """This method is used to move all sub windows and message windows when the main window is moved."""

        for sub_window in self.sub_windows.values():
            main_window_center = self.geometry().center()
            sub_window_geometry = sub_window.geometry()

            main_window_center.setX(int(main_window_center.x()-sub_window_geometry.width()/2))
            main_window_center.setY(int(main_window_center.y()-sub_window_geometry.height()/2))

            sub_window.move(main_window_center)
        
        for message_window in self.message_windows.values():
            main_window_center = self.geometry().center()
            message_window_geometry = message_window.geometry()

            main_window_center.setX(int(main_window_center.x()-message_window_geometry.width()/2))
            main_window_center.setY(int(main_window_center.y()-message_window_geometry.height()/2))

            message_window.move(main_window_center)

        event.accept()
        super().moveEvent(event)



