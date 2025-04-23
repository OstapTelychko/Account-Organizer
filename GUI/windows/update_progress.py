from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget, QScrollArea, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

from DesktopQtToolkit.sub_window import SubWindow
from GUI.gui_constants import SHADOW_EFFECT_ARGUMENTS

if TYPE_CHECKING:
    from GUI.windows.main_window import MainWindow


class UpdateProgressWindow(SubWindow):
    """Represents Update progress window structure."""

    def __init__(self, main_window:MainWindow, sub_windows:dict[int, SubWindow]) -> None:
        super().__init__(main_window, sub_windows)

        self.update_progress_title = QLabel("Update progress")

        self.download_label = QLabel("")
        self.download_progress = QProgressBar()
        self.download_progress.setRange(0, 100)

        self.download_layout = QVBoxLayout()
        self.download_layout.addWidget(self.download_label)
        self.download_layout.addWidget(self.download_progress)

        self.download_wrapper = QWidget()
        self.download_wrapper.setLayout(self.download_layout)
        self.download_wrapper.setProperty("class", "wrapper")
        self.download_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(self.download_wrapper, **SHADOW_EFFECT_ARGUMENTS))
        self.download_wrapper.setFixedWidth(300)

        self.backups_upgrade_label = QLabel()
        self.backups_upgrade_progress = QProgressBar()
        self.backups_upgrade_progress.setFormat("%v/%m")
        self.backups_upgrade_progress.setTextVisible(True)

        self.backups_upgrade_layout = QVBoxLayout()
        self.backups_upgrade_layout.addWidget(self.backups_upgrade_label)
        self.backups_upgrade_layout.addWidget(self.backups_upgrade_progress)

        self.backups_upgrade_wrapper = QWidget()
        self.backups_upgrade_wrapper.setLayout(self.backups_upgrade_layout)
        self.backups_upgrade_wrapper.setProperty("class", "wrapper")
        self.backups_upgrade_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(self.backups_upgrade_wrapper, **SHADOW_EFFECT_ARGUMENTS))
        self.backups_upgrade_wrapper.setFixedWidth(300)

        self.apply_update_label = QLabel()
        self.apply_update_progress = QProgressBar()
        self.apply_update_progress.setRange(0, 4)

        self.apply_update_layout = QVBoxLayout()
        self.apply_update_layout.addWidget(self.apply_update_label)
        self.apply_update_layout.addWidget(self.apply_update_progress)

        self.apply_update_wrapper = QWidget()
        self.apply_update_wrapper.setLayout(self.apply_update_layout)
        self.apply_update_wrapper.setProperty("class", "wrapper")
        self.apply_update_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(self.apply_update_wrapper, **SHADOW_EFFECT_ARGUMENTS))
        self.apply_update_wrapper.setFixedWidth(300)

        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.addWidget(self.download_wrapper)
        self.scroll_layout.addWidget(self.backups_upgrade_wrapper)
        self.scroll_layout.addWidget(self.apply_update_wrapper)
        self.scroll_layout.setSpacing(30)
        self.scroll_layout.setContentsMargins(10, 10, 30, 10)

        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.scroll_layout)

        self.update_stages_scroll = QScrollArea()
        self.update_stages_scroll.setWidgetResizable(True)
        self.update_stages_scroll.setWidget(self.scroll_widget)
        self.update_stages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.window_menu_layout)
        self.main_layout.addWidget(self.update_progress_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.update_stages_scroll)
        self.main_layout.setContentsMargins(30, 10, 30, 30)

        self.window_container.setLayout(self.main_layout)