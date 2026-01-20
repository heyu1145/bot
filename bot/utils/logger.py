"""
logger dispatcher
"""
import logging


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(f"bot_logger ( {name} ) : ")
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
