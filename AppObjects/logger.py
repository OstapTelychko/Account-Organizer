import os
import logging
from logging.handlers import RotatingFileHandler
from project_configuration import APP_LOG_FILE, ERROR_LOG_FILE, MAX_LOG_SIZE, MAX_LOG_BACKUPS, APP_LOG_FORMAT, ERROR_LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIRECTORY, MAX_ERROR_LOG_SIZE


os.makedirs(LOGS_DIRECTORY, exist_ok=True)


class InfoFilter(logging.Filter):
    """This class is used to filter out logs with level INFO and below"""

    def filter(self, record):
        return record.levelno <= logging.INFO



class BreakLineFormatter(logging.Formatter):
    """This class is used to format the logs. It replaces the message "__BREAK_LINE__" with an break line
    (string is empty but logger always add \\n to the end of the message)"""

    def format(self, record):
        if record.getMessage() == "__BREAK_LINE__":
            return ""
        return super().format(record)



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app_handler = RotatingFileHandler(APP_LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=MAX_LOG_BACKUPS, encoding="utf-8")
app_handler.setFormatter(BreakLineFormatter(APP_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
app_handler.setLevel(logging.DEBUG)
app_handler.addFilter(InfoFilter())
logger.addHandler(app_handler)

error_handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=MAX_ERROR_LOG_SIZE, backupCount=MAX_LOG_BACKUPS, encoding="utf-8")
error_handler.setFormatter(BreakLineFormatter(ERROR_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
error_handler.setLevel(logging.WARNING)
logger.addHandler(error_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(BreakLineFormatter(APP_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)


def get_logger(name) -> logging.Logger:
    """Get a logger with the specified name. If the logger already exists, return it.

        Arguments
        ---------
            `name` : (str) - Name of the logger to get.
        Returns
        -------
            `logging.Logger` object with the specified name.
    """

    return logging.getLogger(name)

