from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QScrollArea, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

from DesktopQtToolkit.sub_window import SubWindow

from GUI.windows.main_window import MainWindow
from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS



class UpdateProgressWindow():
    """Represents Update progress window structure."""

    window = SubWindow(MainWindow.window, MainWindow.sub_windows)

    update_progress_title = QLabel("Update progress")

    download_label = QLabel("")
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

    backups_upgrade_label = QLabel()
    backups_upgrade_progress = QProgressBar()
    backups_upgrade_progress.setFormat("%v/%m")
    backups_upgrade_progress.setTextVisible(True)

    backups_upgrade_layout = QVBoxLayout()
    backups_upgrade_layout.addWidget(backups_upgrade_label)
    backups_upgrade_layout.addWidget(backups_upgrade_progress)

    backups_upgrade_wrapper = QWidget()
    backups_upgrade_wrapper.setLayout(backups_upgrade_layout)
    backups_upgrade_wrapper.setProperty("class", "wrapper")
    backups_upgrade_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(backups_upgrade_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    backups_upgrade_wrapper.setFixedWidth(300)

    apply_update_label = QLabel()
    apply_update_progress = QProgressBar()
    apply_update_progress.setRange(0, 4)

    apply_update_layout = QVBoxLayout()
    apply_update_layout.addWidget(apply_update_label)
    apply_update_layout.addWidget(apply_update_progress)

    apply_update_wrapper = QWidget()
    apply_update_wrapper.setLayout(apply_update_layout)
    apply_update_wrapper.setProperty("class", "wrapper")
    apply_update_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(apply_update_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    apply_update_wrapper.setFixedWidth(300)

    scroll_layout = QVBoxLayout()
    scroll_layout.addWidget(download_wrapper)
    scroll_layout.addWidget(backups_upgrade_wrapper)
    scroll_layout.addWidget(apply_update_wrapper)
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