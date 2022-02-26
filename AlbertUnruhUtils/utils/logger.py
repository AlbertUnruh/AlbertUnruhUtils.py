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
_F = "\033[33m{asctime} \t{name: <15} {levelname: <10}\t{message}\033[0m"
_logging_formatter = Formatter(_F, style="{")
_logging_handler = StreamHandler(sys.stdout)
_logging_handler.setFormatter(_logging_formatter)


def get_logger(
    name: typing.Optional[str],
    *,
    level: typing.Union[_LOG_LEVEL_STR, int, None] = "DEBUG",
    add_handler: bool = True,
):
    """
    Parameters
    ----------
    name: str, optional
        The name from the logger.
        (`root` if `None`)
    level: _LOG_LEVEL_STR, int, optional
        The loglevel.
    add_handler: bool
        Whether a handler should be added or not.

    Returns
    -------
    logging.Logger
    """
    logger = getLogger(name)
    if add_handler:
        logger.addHandler(_logging_handler)
    if level is not None:
        if isinstance(level, str):
            level = level.upper()
        logger.setLevel(level)
    return logger
