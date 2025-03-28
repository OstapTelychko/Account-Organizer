from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from functools import partial

from GUI.windows.main_window import MainWindow
from AppObjects.session import Session



def assign_shortcuts():
    """
    Assign shortcuts to the application.
    """

    for sub_window in MainWindow.sub_windows.values():
        close_current_window_shortcut = QShortcut(
            QKeySequence(Session.shortcuts[Session.ShortcutId.CLOSE_CURRENT_WINDOW]),
            sub_window
        )
        close_current_window_shortcut.activated.connect(partial(lambda sub_window: sub_window.done(1), sub_window))
