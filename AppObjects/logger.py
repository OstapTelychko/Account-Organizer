from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import os
import logging
from collections.abc import Set, Mapping
from logging.handlers import RotatingFileHandler
from project_configuration import APP_LOG_FILE, ERROR_LOG_FILE, MAX_LOG_SIZE, MAX_LOG_BACKUPS, APP_LOG_FORMAT, \
ERROR_LOG_FORMAT, LOG_DATE_FORMAT, LOGS_DIRECTORY, MAX_ERROR_LOG_SIZE, TERMINAL_IGNORE_LOG_MESSAGES, \
REPLACE_LOG_MESSAGES

if TYPE_CHECKING:
    from logging import LogRecord


os.makedirs(LOGS_DIRECTORY, exist_ok=True)


class InfoFilter(logging.Filter):
    """This class is used to filter out logs with level INFO and below"""

    def filter(self, record:LogRecord) -> bool:
        return record.levelno <= logging.INFO
    


class IgnoreFilter(logging.Filter):
    """This class is used to filter out logs that are in the ignored_messages set"""

    def __init__(self, ignored_messages:Set[str]|None=None) -> None:
        super().__init__()

        if ignored_messages is None:
            ignored_messages = set()

        if not isinstance(ignored_messages, Set):
            raise TypeError(f"ignored_messages must be a set-like, not {type(ignored_messages)}")
        
        self.ignored_messages = ignored_messages


    def filter(self, record:LogRecord) -> bool:
        """This method is used to filter out logs that are in the ignored_messages set"""

        message = record.getMessage()
        if message in self.ignored_messages:
            return False
        return True



class ReplaceMessageFormatter(logging.Formatter):

    def __init__(
        self,
        fmt:str|None = None,
        datefmt:str|None = None,
        style:Literal['%', '{', '$'] = "%",
        validate:bool = True,
        *,
        replace_messages:Mapping[str, str]|None=None,
        defaults:dict[str, str]|None = None
    ) -> None:
        """
            This formatter is used to replace messages in the log with the values in the replace_messages dict.

            Arguments
            ---------
                `fmt` : (str) - The format string to use for the log messages.
                `datefmt` : (str) - The format string to use for the date and time.
                `style` : (str) - The style to use for the format string. Default is '%'.
                `validate` : (bool) - Whether to validate the format string or not. Default is True.
                `replace_messages` : (Mapping) - A dictionary of messages to replace. Replace the key with the value in the log message. 
        """

        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

        if replace_messages is None:
            replace_messages = dict()

        if not isinstance(replace_messages, Mapping):        
            raise TypeError(f"replace_messages must be a dict-like, not {type(replace_messages)}")
        
        self.replace_messages = replace_messages

    
    def format(self, record:LogRecord) -> str:
        message = record.getMessage()

        for key in self.replace_messages:
            if key == message:
                return self.replace_messages[key]
        
        return super().format(record)


ReplaceFormatter = ReplaceMessageFormatter(
    fmt=APP_LOG_FORMAT, datefmt=LOG_DATE_FORMAT, replace_messages=REPLACE_LOG_MESSAGES
)
ErrorReplaceFormatter = ReplaceMessageFormatter(
    fmt=ERROR_LOG_FORMAT, datefmt=LOG_DATE_FORMAT, replace_messages=REPLACE_LOG_MESSAGES
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

app_handler = RotatingFileHandler(APP_LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=MAX_LOG_BACKUPS, encoding="utf-8")
app_handler.setFormatter(ReplaceFormatter)
app_handler.setLevel(logging.DEBUG)
app_handler.addFilter(InfoFilter())
logger.addHandler(app_handler)

error_handler = RotatingFileHandler(
    ERROR_LOG_FILE, maxBytes=MAX_ERROR_LOG_SIZE, backupCount=MAX_LOG_BACKUPS, encoding="utf-8"
)
error_handler.setFormatter(ErrorReplaceFormatter)
error_handler.setLevel(logging.WARNING)
logger.addHandler(error_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ReplaceFormatter)
console_handler.setLevel(logging.WARNING)
console_handler.addFilter(IgnoreFilter(TERMINAL_IGNORE_LOG_MESSAGES))
logger.addHandler(console_handler)


def get_logger(name:str) -> logging.Logger:
    """Get a logger with the specified name. If the logger already exists, return it.

        Arguments
        ---------
            `name` : (str) - Name of the logger to get.
        Returns
        -------
            `logging.Logger` object with the specified name.
    """

    return logging.getLogger(name)

