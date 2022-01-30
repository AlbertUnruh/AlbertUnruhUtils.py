__all__ = ("get_logger",)


import sys
import typing
from logging import (
    getLogger,
    Formatter,
    StreamHandler,
)


_LOG_LEVEL_STR = typing.Literal[
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
]
_F = "\033[33m[{asctime}] [{name}] [{levelname}]\t{message}\033[0m"
_logging_formatter = Formatter(_F, style="{")
_logging_handler = StreamHandler(sys.stdout)
_logging_handler.setFormatter(_logging_formatter)


def get_logger(
    name: typing.Optional[str],
    *,
    level: typing.Union[_LOG_LEVEL_STR, int] = "DEBUG",
):
    """
    Parameters
    ----------
    name: str, optional
        The name from the logger.
        (`root` if `None`)
    level: _LOG_LEVEL_STR, int
        The loglevel.

    Returns
    -------
    logging.Logger
    """
    logger = getLogger(name)
    logger.addHandler(_logging_handler)
    if isinstance(level, str):
        level = level.upper()
    logger.setLevel(level)
    return logger
