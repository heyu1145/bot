"""
hex helper functions
"""


def hex_to_int(hex_str: str | int) -> int:
    """
    an function supports hex to integer

    args:
    hex_str: str of hex, only support last 6 char

    returns:
    an int hex convered to int
    """
    if isinstance(hex_str, int):
        return hex_str
    hex_str = hex_str.lower().lstrip().lstrip("#")
    try:
        return int(hex_str[-6:], 16)
    except:
        return 0


def int_to_hex(hex_int: int | str) -> str:
    """
    an function supports int to hex

    args:
    hex_int integer

    returns:
    str that convered to hex str (000000-ffffff)
    last 6 if > ffffff
    """
    if isinstance(hex_int, str):
        try:
            hex_int = int(hex_int)
        except:
            return "000000"
    return f"{hex(hex_int)[-6:]:0>6}"
