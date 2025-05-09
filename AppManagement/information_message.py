from threading import Thread
from PySide6.QtCore import QTimer
from AppObjects.windows_registry import WindowsRegistry



def show_information_message(text:str) -> None:
    """This method is used to show the information message window and center it on the main window.

        Arguments
        -------
            `text` (str): message to show
    """

    WindowsRegistry.InformationMessage.message_text.setText(text)

    def _center_message() -> None:
        """This method is used to center the message window on the main window."""

        main_window_center = WindowsRegistry.MainWindow.geometry().center()
        information_message_geometry = WindowsRegistry.InformationMessage.geometry()

        main_window_center.setX(int(main_window_center.x()-information_message_geometry.width()/2))
        main_window_center.setY(int(main_window_center.y()-information_message_geometry.height()/2))

        WindowsRegistry.InformationMessage.move(main_window_center)


    try:
        message_worker = Thread(target=WindowsRegistry.InformationMessage.run)
        message_worker.start()
        QTimer.singleShot(50, _center_message)
    except RuntimeError:
        pass # When the program exits, this prevents a widget deletion error