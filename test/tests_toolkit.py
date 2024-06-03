from unittest import TestCase

from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer



LEFT_BUTTON = Qt.MouseButton.LeftButton

class TestWindowsCaseMixin():

    def test_windows_opening(self:TestCase):
        for window, open_window_button in self.test_windows_open.items():
            window_object = getattr(window, "window")

            def check_window_appearance():
                self.assertTrue(window_object.isVisible(), f"Window {window.__name__} hasn't showed after click on button {open_window_button.text()}")
                window_object.done(1)

            QTimer.singleShot(100, check_window_appearance)# Timer will call this function after 100 milliseconds. QDialog use exec to show up so it block program loop
            open_window_button.click()



class DataBaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass



    