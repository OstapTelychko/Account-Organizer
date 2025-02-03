from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

from DesktopQtToolkit.sub_window import SubWindow

from GUI.windows.main_window import MainWindow
from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS


class UpdateProgressWindow():
    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    update_progress_title = QLabel("Update progress")

    download_label = QLabel("Downloading update...")
    download_progress = QProgressBar()
    download_progress.setRange(0, 100)

    download_layout = QVBoxLayout()
    download_layout.addWidget(download_label)
    download_layout.addWidget(download_progress)

    download_wrapper = QWidget()
    download_wrapper.setLayout(download_layout)
    download_wrapper.setProperty("class", "wrapper")
    download_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(download_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    download_wrapper.setFixedWidth(300)

    scroll_layout = QVBoxLayout()
    scroll_layout.addWidget(download_wrapper)
    scroll_layout.setSpacing(30)
    scroll_layout.setContentsMargins(10, 10, 30, 10)

    scroll_widget = QWidget()
    scroll_widget.setLayout(scroll_layout)

    update_stages_scroll = QScrollArea()
    update_stages_scroll.setWidgetResizable(True)
    update_stages_scroll.setWidget(scroll_widget)
    update_stages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    main_layout = QVBoxLayout()
    main_layout.addLayout(window.window_menu_layout)
    main_layout.addWidget(update_progress_title, alignment=Qt.AlignmentFlag.AlignHCenter)
    main_layout.addWidget(update_stages_scroll)
    main_layout.setContentsMargins(30, 10, 30, 30)

    window.window_container.setLayout(main_layout)