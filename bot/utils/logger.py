"""
logger dispatcher
"""

from typing import overload
import logging
from datetime import datetime
from pathlib import Path

this_file = Path(__file__).resolve()
file_prefix = datetime.now().isoformat()


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
    formatter = logging.Formatter(
        "( %(name)s ) - %(asctime)s - %(levelname)s: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logging_file = logging_dir / f"{file_prefix}.log"

    fh = logging.FileHandler(logging_file, encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return (logger, ch, fh)
