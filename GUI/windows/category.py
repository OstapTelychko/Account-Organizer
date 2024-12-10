from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt


from DesktopQtToolkit.sub_window import SubWindow
from DesktopQtToolkit.create_button import create_button

from GUI.gui_constants import ALIGMENT, SHADOW_EFFECT_ARGUMENTS
from GUI.windows.main_window import MainWindow




class CategorySettingsWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    rename_category = create_button("Rename category",(255,40))

    delete_category = create_button("Delete category",(255,40))

    change_category_position = create_button("Change position", (255, 40))

    copy_transactions = create_button("Copy transactions",(275,40))

    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(rename_category, alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(delete_category, alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(change_category_position, alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(copy_transactions,alignment=ALIGMENT.AlignHCenter)
    main_layout.setContentsMargins(30, 10, 30, 20)

    window.window_container.setLayout(main_layout)



class AddCategoryWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    category_name = QLineEdit()
    category_name.setPlaceholderText("Category name")

    button = create_button("Add category", (160,40))
    button.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(30)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.setContentsMargins(30, 10, 30, 30)

    window.window_container.setLayout(main_layout)



class ChangeCategoryPositionWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    preview_category_position = QLabel()
    preview_category_position.setProperty("class", "category_list_item")
    
    preview_category_name = QLabel()
    preview_category_name.setProperty("class", "light-text")

    preview_category_container = QWidget()
    preview_category_container.setProperty("class", "category_list_item")
    preview_category_container.setGraphicsEffect(QGraphicsDropShadowEffect(preview_category_container, **SHADOW_EFFECT_ARGUMENTS))

    preview_category_layout = QHBoxLayout()
    preview_category_layout.addWidget(preview_category_position, alignment=ALIGMENT.AlignRight)
    preview_category_layout.addWidget(preview_category_name, alignment=ALIGMENT.AlignLeft)
    preview_category_container.setLayout(preview_category_layout)

    new_position = QLineEdit()
    enter_new_position = create_button("Save", (140, 30))
    enter_new_position.setDefault(True)

    new_position_layout = QHBoxLayout()
    new_position_layout.addWidget(new_position, alignment=ALIGMENT.AlignHorizontal_Mask)
    new_position_layout.addWidget(enter_new_position, alignment=ALIGMENT.AlignLeft)
    new_position_layout.setContentsMargins(0, 50, 0, 50)

    categories_list_layout = QVBoxLayout()
    categories_list_window = QWidget()
    categories_list_window.setLayout(categories_list_layout)

    categories_list_scroll = QScrollArea()
    categories_list_scroll.setWidget(categories_list_window)
    categories_list_scroll.setWidgetResizable(True)
    categories_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    categories_list_scroll.setMinimumHeight(350)
    categories_list_scroll.setMinimumWidth(400)
    categories_list_scroll.setStyleSheet("""QScrollArea{border:none;}""")
    categories_list_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
    categories_list_scroll.setProperty("class", "wrapper")
    categories_list_scroll.setGraphicsEffect(QGraphicsDropShadowEffect(categories_list_scroll, **SHADOW_EFFECT_ARGUMENTS))
    

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addStretch(1)
    main_layout.addWidget(preview_category_container, alignment=ALIGMENT.AlignHCenter)
    main_layout.addLayout(new_position_layout)
    main_layout.addWidget(categories_list_scroll, alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)
    main_layout.setContentsMargins(30, 10, 30, 20)

    window.window_container.setLayout(main_layout)



class RenameCategoryWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    new_category_name = QLineEdit()
    new_category_name.setMinimumWidth(150)
    new_category_name.setPlaceholderText("New name")

    button = create_button("Rename", (170,40))
    button.setDefault(True)

    main_layout = QVBoxLayout()
    main_layout.setSpacing(30)
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(new_category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)
    main_layout.setContentsMargins(40, 10, 40, 20)

    window.window_container.setLayout(main_layout)