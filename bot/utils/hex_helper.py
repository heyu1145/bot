"""
hex helper functions
"""

VALID_HEX_STRING_SET = frozenset("0123456789abcdefABCDEF")


def normalize_string(s: str, /) -> str:
    """
    return the string exclude normal hex case
    """
    # drop spaces, # and 0x hex head
    return s.upper().strip().lstrip("#").replace("0X", "", 2)


def handle_short_string(s: str, /) -> str:
    """
    return the string handled hex short case ( RGB ) and other lower than 6-digits case
    like GGBB to 00GGBB / BB to 0000BB / *RRGGBB to RRGGBB 
    """

    # handles short hax format
    if len(s) == 3:
        return ''.join([char*2 for char in s])

    # handle other format
    s = s[-6:]
    return f"{s:0>6}"


def normalize_hex_color(color: str | int) -> str:
    """
    Convent str or integer input to 6-digits hex format (000000-FFFFFF)

    Args:
        color:
            - Integer format ( 0xRRGGBB )
            - String format ( include RGB, RRGGBB, #RGB, #RRGGBB )

    Returns:
        6-digits upper case format string

    we are highly recommend use string format for better expression
    """
    if isinstance(color, int):
        # < 0 is 0 and > 0xffffff is 0xffffff
        color_int = max(0, color) & 0xffffff
        return f"{color_int:06X}"

    formatted = normalize_string(color)
    formatted = handle_short_string(formatted)

    # check is vaild or not
    for char in formatted:
        if char not in VALID_HEX_STRING_SET:
            return "000000"

    return formatted


def to_color_int(color: str | int) -> int:
    """
    Convent str or int to hex integer

    Args:
        color:
            same as `normalize_hex_color`
            - Integer format
            - String format

    Returns:
        integer between 0x000000 and 0xffffff
    """
    if isinstance(color, int):
        return max(0, color) & 0xffffff

    color = normalize_string(color)
    color = handle_short_string(color)

    try:
        return int(color, 16)
    except (ValueError, TypeError):
        return 0


def split_rgb(rgb: str | int, /) -> tuple[int, int, int]:
    """
    convent rgb string to tuple of r, g and b
    """
    rgb = to_color_int(rgb)
    return (
        (rgb & 0xff0000) >> 16,
        (rgb & 0x00ff00) >> 8,
        rgb & 0x0000ff
    )


def rgba_to_rgb(rgba: str | int, bg: str | int = "#ffffff") -> str:
    """
    convent the rgba to the same rgb with the background

    Args:
        rgba:
            the rgba format ( #RGBA / #RRGGBBAA or 0xRRGGBBAA )
        bg: 
            the rgb format ( same as `normalize_hex_color` )

    Returns:
        the rgb of rgba with background ( 6-digits upper case format )
    """
    bg_r, bg_g, bg_b = split_rgb(bg)
    if isinstance(rgba, int):
        # int convent to istr
        rgba = f"{max(0, rgba) & 0xffffffff:08X}"

    rgba = normalize_string(rgba)

    # handle short format
    if len(rgba) == 4:
        rgba = ''.join([char*2 for char in rgba])

    # get last 8 digits
    rgba = f"{rgba:0>8}"
    rgba = rgba[-8:]
    try:
        rgba_int = int(rgba, 16)
    except (ValueError, TypeError):
        return "000000"

    r = (rgba_int & 0xff000000) >> 24
    g = (rgba_int & 0x00ff0000) >> 16
    b = (rgba_int & 0x0000ff00) >> 8
    a = (rgba_int & 0x000000ff) / 255
    nr = (1-a)*bg_r+a*r
    ng = (1-a)*bg_g+a*g
    nb = (1-a)*bg_b+a*b
    return f"{round(nr):02X}{round(ng):02X}{round(nb):02X}"
