from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate

from project_configuration import QCALENDAR_DATE_FORMAT



def create_date_input() -> QDateEdit:
    """
    Create a QDateEdit widget with the current date and calendar popup enabled.
    """
    
    date_input = QDateEdit()
    date_input.setDisplayFormat(QCALENDAR_DATE_FORMAT)
    date_input.setCalendarPopup(True)
    date_input.setDate(QDate.currentDate())

    return date_input