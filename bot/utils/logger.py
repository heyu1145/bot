"""
logger dispatcher
"""

from typing import overload
import logging
from datetime import datetime
from pathlib import Path

this_file = Path(__file__).resolve()
now = datetime.now().astimezone()
file_prefix = now.isoformat(timespec="seconds")

__all__ = ("get_logger",)

PS1_COLORS: dict[str, str] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
}

FORMAT: str = (f"{PS1_COLORS['blue']}%(asctime)s{PS1_COLORS['reset']} - "
               f"{PS1_COLORS['green']}%(name)s{PS1_COLORS['reset']} - "
               f"{PS1_COLORS['yellow']}%(levelname)s{PS1_COLORS['reset']}"
               " - %(message)s")

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


@overload
def get_logger(
    value: str, logging_dir: Path = this_file.parent.parent / "logs"
) -> tuple[logging.Logger, logging.StreamHandler, logging.FileHandler]: ...


@overload
def get_logger[T: logging.Logger](
    value: T, logging_dir: Path = this_file.parent.parent / "logs"
) -> tuple[T, logging.StreamHandler, logging.FileHandler]: ...


def get_logger[T: logging.Logger](
    value: str | T, logging_dir=this_file.parent.parent / "logs"
) -> tuple[logging.Logger | T, logging.StreamHandler, logging.FileHandler]:
    """Get a configured logger instance."""
    logger: logging.Logger = logging.getLogger(str(value))
    if isinstance(value, logging.Logger):
        logger = value

    if not logging_dir.exists():
        logging_dir.mkdir()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logging_file = logging_dir / f"{file_prefix}.log"

    fh = logging.FileHandler(logging_file, encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return (logger, ch, fh)
