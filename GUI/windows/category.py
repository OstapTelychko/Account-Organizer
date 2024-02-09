from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QScrollArea, QDialog, QSizePolicy
from PySide6.QtCore import Qt

from GUI.windows.main import APP_ICON, BASIC_FONT, ALIGMENT, create_button, close_dialog




class CategorySettingsWindow():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle(" ")
    window.closeEvent = close_dialog
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.setFont(BASIC_FONT)

    rename_category = create_button("Rename category",(255,40))
    rename_category.setProperty("class", "button")

    delete_category = create_button("Delete category",(255,40))
    delete_category.setProperty("class", "button")

    change_category_position = create_button("Change position", (255, 40))
    change_category_position.setProperty("class", "button")

    copy_transactions = create_button("Copy transactions",(275,40))
    copy_transactions.setProperty("class", "button")

    main_layout = QVBoxLayout()
    main_layout.addWidget(rename_category, alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(delete_category, alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(change_category_position, alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(copy_transactions,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class AddCategoryWindow():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Add category")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog

    category_name = QLineEdit()
    category_name.setPlaceholderText("Category name")

    button = create_button("Add category", (160,40))

    main_layout = QVBoxLayout()

    main_layout.addWidget(category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)



class ChangeCategoryPositionWindow():
    window = QDialog()
    window.resize(800,800)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Change category position")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog

    preview_category_position = QLabel()
    preview_category_name = QLabel()
    preview_category_container = QWidget()
    preview_category_container.setProperty("class", "category_list_item")

    preview_category_layout = QHBoxLayout()
    preview_category_layout.addWidget(preview_category_position, alignment=ALIGMENT.AlignRight)
    preview_category_layout.addWidget(preview_category_name, alignment=ALIGMENT.AlignLeft)
    preview_category_container.setLayout(preview_category_layout)

    new_position = QLineEdit()
    enter_new_position = create_button("Save", (140, 30))

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
    categories_list_scroll.setStyleSheet(
        """QScrollArea{
            border:none;
            background-color:rgb(43, 43, 43);
            border-radius:10px;
            padding:5px;
            margin-left:0px;
            margin-top:10px;
            margin-right:10px;
            margin-bottom:10px}""")
    categories_list_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
    

    main_layout = QVBoxLayout()
    main_layout.addStretch(1)
    main_layout.addWidget(preview_category_container, alignment=ALIGMENT.AlignHCenter)
    main_layout.addLayout(new_position_layout)
    main_layout.addWidget(categories_list_scroll, alignment=ALIGMENT.AlignHCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)



class RenameCategoryWindow():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Rename")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog

    new_category_name = QLineEdit()
    new_category_name.setMinimumWidth(150)
    new_category_name.setPlaceholderText("New name")
    button = create_button("Rename", (170,40))

    main_layout = QVBoxLayout()
    main_layout.addWidget(new_category_name,alignment=ALIGMENT.AlignHCenter)
    main_layout.addWidget(button,alignment=ALIGMENT.AlignHCenter)

    window.setLayout(main_layout)