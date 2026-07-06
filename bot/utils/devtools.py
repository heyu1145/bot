"""
stores development tools
"""
import inspect
from typing import Any, NoReturn

# DEV INFO


def TODO(msg: Any) -> NoReturn:
    """raises a NotImplementedError with the given message"""
    raise NotImplementedError(f"TODO: {msg}")


def WARN(msg: Any) -> None:
    """raises a Warning with the given message"""
    raise Warning(f"WARN: {msg}")


def FIXME(msg: Any) -> None:
    """raises a Warning with the given message"""
    raise Warning(f"FIXME: {msg}")

# DEBUG INFO


def CURRENT_LINE() -> int:
    """returns the current line number in program"""
    return inspect.currentframe().f_back.f_lineno  # type: ignore[union-attr]


def LOCAL_VARS() -> dict:
    """returns the local variables in the current scope"""
    return inspect.currentframe().f_back.f_locals  # type: ignore[union-attr]


def GLOBAL_VARS() -> dict:
    """returns the global variables in the current scope"""
    return inspect.currentframe().f_back.f_globals  # type: ignore[union-attr]


def CALLER_INFO() -> tuple[str, int, str] | None:
    """returns the caller's filename, line number, and function name"""
    frame = inspect.currentframe().f_back.f_back  # type: ignore[union-attr]
    if frame is not None:
        return (frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name)
    return None
