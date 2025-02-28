import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from project_configuration import ROOT_DIRECTORY, APP_LOG_FILE, ERROR_LOG_FILE, MAX_LOG_SIZE, MAX_LOG_BACKUPS, APP_LOG_FORMAT, ERROR_LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIRECTORY, MAX_ERROR_LOG_SIZE


os.makedirs(LOGS_DIRECTORY, exist_ok=True)


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno <= logging.INFO


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app_handler = RotatingFileHandler(APP_LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=MAX_LOG_BACKUPS, encoding="utf-8")
app_handler.setFormatter(logging.Formatter(APP_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
app_handler.setLevel(logging.DEBUG)
app_handler.addFilter(InfoFilter())
logger.addHandler(app_handler)

error_handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=MAX_ERROR_LOG_SIZE, backupCount=MAX_LOG_BACKUPS, encoding="utf-8")
error_handler.setFormatter(logging.Formatter(ERROR_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
error_handler.setLevel(logging.WARNING)
logger.addHandler(error_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(APP_LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
console_handler.setLevel(logging.WARNING)
logger.addHandler(console_handler)


def get_logger(name) -> logging.Logger:
    return logging.getLogger(name)

