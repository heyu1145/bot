"""
the embed json format checker
"""

from copy import deepcopy
import discord
from utils.hex_helper import to_color_int
from utils.utils import human_like_join

CORE_CONTENT: list[str] = [
    "title",
    "description",
    "footer",
    "author",
    "image",
    "thumbnail",
]

__all__ = ("convent_embed_json", "has_core_content", "convent_color_to_vaild")

EMPTY_THING: list = ["", None]

ERREMBED_FORMAT = discord.Embed(title="Failed", color=discord.Color.red())

SUCCESSEMBED_FORMAT = discord.Embed(
    title="success", color=discord.Color.green())


def has_core_content(data: dict) -> bool:
    """
    check a embed json has core content or not

    Args:
        the embed json

    Returns:
        True if has any content,
        False if not any
    """
    return any(core in data and data[core] not in EMPTY_THING for core in CORE_CONTENT)


def convent_color_to_vaild(data: dict) -> tuple[bool, dict | None]:
    """
    check and try convent color to int

    Args:
        the embed json

    Returns:
        True and origin dict for vaild
        False and convented dict for invalid
        False and None for invalid color type
    """
    color = data.get("color")
    if color is None or isinstance(color, int):
        return True, data

    if not isinstance(color, str):
        return False, None

    copy = deepcopy(data)

    color_int = to_color_int(color)

    copy["color"] = color_int

    return False, copy


def convent_embed_json(data: object) -> tuple[bool, dict | None, discord.Embed]:
    """
    try to convent embed json to a clean embed json format

    Args:
        a json str from user input or else

    Returns:
        True, cleaned dict and a success embed for successed and no convent
        False, cleaned dict and warning embed for successed but convent something
        False, None and error embed for convent failed
    """
    if not isinstance(data, dict):
        errembed = ERREMBED_FORMAT.copy()
        errembed.description = "the json str is not a json object"
        return False, None, errembed

    ok = has_core_content(data)
    if not ok:
        errembed = ERREMBED_FORMAT.copy()
        errembed.description = (
            f"The embed dont have any core content:{human_like_join(CORE_CONTENT)}"
        )
        return False, None, errembed

    warning_data: list[str] = []

    ok, newdata = convent_color_to_vaild(data)

    if not ok:
        if not newdata:
            errembed = ERREMBED_FORMAT.copy()
            errembed.description = "the color data could not resolved"

            return False, None, errembed

        warning_data.append(
            f"The color data is wrong but resolved, color now: {newdata.get('color')}"
        )

    sucembed = SUCCESSEMBED_FORMAT.copy()

    sucembed.description = "the embed json is convented"

    success = True

    if warning_data:
        success = False
        for warns in warning_data:
            sucembed.add_field(name="warning", value=warns, inline=False)

    return success, newdata, sucembed
