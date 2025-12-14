from __future__ import annotations
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtGui import QTextDocument, QPainter, QAbstractTextDocumentLayout, QPalette
from PySide6.QtCore import Qt, QSize, QPersistentModelIndex, QModelIndex





class QRichTextDelegate(QStyledItemDelegate):
    """
    Item delegate that renders item DisplayRole data as Qt rich text (HTML fragment).
    Use for QListWidget / QTableWidget / any QAbstractItemView to get <span>, <b>, colors, etc.
    """

    def paint(self, painter:QPainter, option:QStyleOptionViewItem, index:QModelIndex | QPersistentModelIndex) -> None:
        """Custom paint builds a QTextDocument from the HTML string."""

        html = index.data(Qt.ItemDataRole.DisplayRole)
        if not html:
            super().paint(painter, option, index)
            return
        html = f"<div style='line-height: 0.7;'>{html}</div>"

        doc = QTextDocument()
        doc.setHtml(html)
        doc.setDocumentMargin(0)
        doc.setTextWidth(option.rect.width())#type:ignore[attr-defined] # This attribute exists, but PySide6 types are incomplete.

        painter.save()
        painter.translate(option.rect.topLeft())#type:ignore[attr-defined] 
        context = QAbstractTextDocumentLayout.PaintContext()
        # Set the text color in the paint context
        context.palette.setColor(QPalette.ColorRole.Text, option.palette.color(QPalette.ColorRole.Text))#type:ignore[attr-defined]
        
        doc.documentLayout().draw(painter, context)
        painter.restore()


    def sizeHint(self, option:QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        """Return the preferred (width, height) for the item given its HTML content."""

        html = index.data(Qt.ItemDataRole.DisplayRole)
        if not html:
            return super().sizeHint(option, index)
        html = f"<div style='line-height: 0.7;'>{html}</div>"
        
        doc = QTextDocument()
        doc.setHtml(html)

        # Determine a working width: if option.rect.width() == 0 (first pass),
        # pick a reasonable fallback (e.g. 400) so multi-line text expands.
        width = option.rect.width() if option.rect.width() > 0 else 400 #type:ignore[attr-defined] 
        doc.setTextWidth(width)

        return QSize(int(width), int(doc.size().height()))