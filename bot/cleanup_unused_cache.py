"""clean __pycache__, .pyc and logs older than 7 days"""
from collections.abc import Iterator
from pathlib import Path
from datetime import datetime, timedelta
import logging

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
THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent

logger = logging.Logger(__name__)
Formatter = logging.Formatter(f"{PS1_COLORS['yellow']}%(asctime)s{PS1_COLORS['reset']} - "
                              f"{PS1_COLORS['green']}%(levelname)s{PS1_COLORS['reset']} - "
                              f"{PS1_COLORS['white']}%(message)s{PS1_COLORS['reset']}")

console_handler = logging.StreamHandler()
console_handler.setFormatter(Formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


def check_time(dt: datetime, /) -> bool:
    """
    check if datetime is vaild

    Args:
        dt (datetime): datetime to check

    Returns:
        bool: True if datetime is vaild, False otherwise
    """
    if dt.tzinfo is None:
        dt.astimezone()  # convert to local time with tzinfo

    offset = dt - datetime.now().astimezone()

    return offset < timedelta(0)


def resolve_file_spwan_time(path: Path, /) -> datetime:
    """
    resolve file spawn time from file stat or file name

    Args:
        path (Path): file path

    Returns:
        datetime: file spawn time with tzinfo

    Raises:
        ValueError: if path is not a file
        FileNotFoundError: if file stat not available and file name does not match isoformat

    Note:
        1. use file name if file stat not available
        2. use local time for default timezone if isoformat does not contain timezone info
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    file_ctime = path.stat().st_ctime
    file_create_dt = datetime.fromtimestamp(file_ctime).astimezone()
    if check_time(file_create_dt):
        return file_create_dt

    if check_time(file_create_dt):
        return file_create_dt

    raise PermissionError(f"file '{path.name}'s stat not available")


def file_should_be_remove(path: Path, *, days: int = 7) -> bool:
    """
    check if file should be removed

    Args:
        path (Path): file path
        days (int, optional): days threshold. Defaults to 7.

    Returns:
        bool: True if file should be removed, False otherwise

    Raises:
        ValueError: if path is not a file
        FileNotFoundError: if file stat not available and file name does not match isoformat
    """
    spawn_time: datetime = resolve_file_spwan_time(path)
    return datetime.now().astimezone() - spawn_time > timedelta(days=days)


def delete_dir(path: Path, /) -> None:
    """
    delete directory and all its contents

    Args:
        path (Path): directory path

    Raises:
        ValueError: if path is not a directory
    """
    if not path.exists():
        return

    if not path.is_dir():
        raise ValueError(f"{path} is not a directory")

    for root, _, files in path.walk(top_down=False):
        for file in files:
            logger.info(
                f"delete file '{file}' in dir '{root.relative_to(THIS_DIR)}'")
            file_path = path / file
            file_path.unlink()

        logger.info(f"delete dir '{root.relative_to(THIS_DIR)}'")
        root.rmdir()


def cleanup_cache_and_logs(*, cache_dir: Path, logs_dir: Path, days: int = 7) -> None:
    """
    cleanup __pycache__, .pyc and logs older than 7 days

    Args:
        cache_dir (Path): __pycache__ directory path
        logs_dir (Path): logs directory path
        days (int, optional): days threshold. Defaults to 7.

    Raises:
        ValueError: if cache_dir is not a directory or logs_dir is not a directory
    """
    if not cache_dir.exists():
        logger.warning(f"{cache_dir} does not exist, skip cache cleanup")
    elif not cache_dir.is_dir():
        raise ValueError(f"{cache_dir} is not a directory")
    else:
        for path in cache_dir.glob("**/__pycache__"):
            delete_dir(path)

    if not logs_dir.exists():
        logger.warning(f"{logs_dir} does not exist, skip logs cleanup")
    elif not logs_dir.is_dir():
        raise ValueError(f"{logs_dir} is not a directory")
    else:
        del_all: bool = False

        logs: Iterator[Path] = logs_dir.glob("**/*.log")
        if not any(logs):
            logger.warning(
                f"no log file found in dir '{logs_dir.name}', skip logs cleanup")
            return
        for path in logs:
            if file_should_be_remove(path, days=days):
                if not del_all:
                    usr_input = input(
                        f"delete log file '{path.name}'? (yes / no / all): ").strip().lower()
                    if usr_input in ("yes", "y"):
                        path.unlink()
                    elif usr_input in ("all", "a"):
                        del_all = True
                        path.unlink()
                    elif usr_input in ("no", "n"):
                        continue
                    else:
                        logger.warning("invalid input, skip this file")
                else:
                    logger.info(f"delete log file '{path.name}'")
                    path.unlink()


if __name__ == "__main__":
    this_dir = Path(__file__).parent
    cache_dir = this_dir
    logs_dir = this_dir / "logs"
    cleanup_cache_and_logs(cache_dir=cache_dir, logs_dir=logs_dir)
