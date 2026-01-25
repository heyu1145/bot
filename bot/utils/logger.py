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
    value: str,
    logging_dir: Path = this_file.parent.parent / "logs"
) -> logging.Logger:
    """
    an function returns a logger by name
    """
    ...


@overload
def get_logger(
    value: logging.Logger,
    logging_dir: Path = this_file.parent.parent / "logs"
) -> logging.Logger:
    """
    an empty logger pack for log
    """
    ...


def get_logger(
        value,
        logging_dir=this_file.parent.parent / "logs"
) -> logging.Logger:
    """Get a configured logger instance."""
    logger: logging.Logger = logging.getLogger(f"bot_logger ( {value} ) : ")
    if isinstance(value, logging.Logger):
        logger = value

    if not logging_dir.exists():
        logging_dir.mkdir()

    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logging_file = logging_dir / f"{file_prefix}.log"

    fh = logging.FileHandler(logging_file, encoding="utf-8")

    fh.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    return logger
