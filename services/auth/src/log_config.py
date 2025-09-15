import logging
from enum import StrEnum

from src.config import settings

LOG_FORMAT_DEBUG = "%(levelname)s: %(message)s [%(pathname)s:%(funcName)s:%(lineno)d]"
LOG_FORMAT_DEFAULT = "%(levelname)s: %(message)s"


class LogLevels(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


LOG_COLORS = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARN": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[95m",
}
RESET_COLOR = "\033[0m"


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level_color = LOG_COLORS.get(record.levelname, "")
        record.levelname = f"{level_color}{record.levelname}{RESET_COLOR}"
        return super().format(record)


def configure_logging():
    log_level = str(settings.LOG_LEVEL).upper()
    log_levels = list(LogLevels)

    if log_level not in log_levels:
        # Using error as the default log level
        log_level = LogLevels.error

    formatter = ColoredFormatter(
        fmt=LOG_FORMAT_DEBUG if log_level == LogLevels.debug else LOG_FORMAT_DEFAULT
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.handlers = [handler]
