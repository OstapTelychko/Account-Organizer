from __future__ import annotations
from typing import TYPE_CHECKING, overload, Any
from PySide6.QtWidgets import QTableWidget, QApplication, QTableWidgetItem
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QKeyEvent, QWheelEvent, QPixmap, QIcon


# pyright: reportIncompatibleMethodOverride=false
class CustomTableWidget(QTableWidget):
    """This class is used to create a custom table widget that allows for copying multiple cells to the clipboard and prevents scrolling out of widget when the table widget runs out of rows."""

    @overload
    def __init__(self, parent:QWidget|None = ...) -> None: ...
    @overload
    def __init__(self, rows: int, columns: int, parent: QWidget|None = ...) -> None: ...
    def __init__(self, *args:Any, **kwargs:Any) -> None:
        super().__init__(*args, **kwargs)
    

    def keyPressEvent(self, event:QKeyEvent) -> None:
        "Allows copy multiple cell's text to the clipboard"

        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            copied_cells = self.selectedIndexes()

            copy_text = ''
            max_column = copied_cells[-1].column()
            for cell in copied_cells:
                copy_text += self.item(cell.row(), cell.column()).text()
                if cell.column() == max_column:
                    copy_text += '\n'
                else:
                    copy_text += '\t'
                    
            QApplication.clipboard().setText(copy_text)
    

    def wheelEvent(self, event:QWheelEvent) -> None:
        "Prevents scrolling out of widget when TableWidget run out of rows and is neseted into a ScrollArea"

        verticall_scrollbar = self.verticalScrollBar()
        if verticall_scrollbar.isVisible() and verticall_scrollbar.minimum() < verticall_scrollbar.maximum():
            super().wheelEvent(event)
            event.accept()
        else:
            event.ignore()
            


class CustomTableWidgetItem(QTableWidgetItem):
    """This class is used to create a custom table widget item that allows for sorting by string or float values.
    It overrides the less than operator to compare the values of the items.
    """

    @overload
    def __init__(self, icon:QIcon|QPixmap, text: str, type: int = ...) -> None: ...
    @overload
    def __init__(self, other:QTableWidgetItem) -> None: ...
    @overload
    def __init__(self, text: str, type: int = ...) -> None: ...
    @overload
    def __init__(self, type: int = ...) -> None: ...
    def __init__(self, *args:Any, **kwargs:Any) -> None:
        super().__init__(*args, **kwargs)
    

    def __lt__(self, other:CustomTableWidgetItem) -> bool:
        try:
            return float(self.data(Qt.ItemDataRole.EditRole)) < float(other.data(Qt.ItemDataRole.EditRole))
        except ValueError:
            # If conversion to float fails, fallback to string comparison
            return self.text() < other.text()

            
