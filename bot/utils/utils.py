"""
an utils function include all unknown type func
"""
from collections.abc import Awaitable, Callable, Sequence
from typing import Protocol, cast, overload
import asyncio
import discord

@overload
async def maybe_coro[T](
        func: Callable[..., T],
        /,
        *args,
        **kwargs
    ) -> T: ...

@overload
async def maybe_coro[T](
        func: Callable[..., Awaitable[T]],
        /,
        *args,
        **kwargs
    ) -> T: ...

async def maybe_coro[T](
    func: Callable[..., T | Awaitable[T]],
    /,
    *args,
    **kwargs
) -> T:
    """
    Call a function that not Corountine or await it

    Args:
        func: A Callable, Whether Corountine or not
        Args & Kwargs: Pass to func
    
    Tips:
        This function wouldn't handle sync function returns corountine
        Or async function returns more than two corountres

    Returns:
        func's returns
    """
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)

    return cast(T, func(*args, **kwargs))

class ToStringAble(Protocol):
    """
    class include __str__ (can str())
    """

    def __str__(self) -> str:
        ...


class ToReprAble(Protocol):
    """
    class include __repr__ (can repr())
    """

    def __repr__(self) -> str:
        ...


StringLike = ToStringAble | ToReprAble


def human_like_join(
    seq: Sequence[StringLike],
    *,
    delimiter: str = ", ",
    final: str = " or "
) -> str:
    """
    convert a Sequence (sized and iterable) to the human string

    E.g: ["a", "b", "c"] -> "a, b or c"

    Args:
        seq: the Sequence
        delimiter: the delimiter between elements
        final: the delimiter between last two elements

    Returns:
        original if seq is a str
        else human like string
    """
    if isinstance(seq, str):
        return seq

    str_seq: list[str] = [str(elem) for elem in seq]
    match len(str_seq):
        case 0:
            return ""
        case 1:
            return str_seq[0]
        case 2:
            return f"{str_seq[0]}{final}{str_seq[1]}"
        case _:
            return f"{delimiter.join(str_seq[:-1])}{final}{str_seq[-1]}"


def multi_set_fields(
        embed: discord.Embed,
        all_inline: bool = True,
        title_all_name: bool = True,
        **kwargs: object
) -> discord.Embed:
    """
    add fields multiply

    Args:
        embed: the embed to add
        all_inline: all fields is inline or not
        title_all_name: do title for all name in fields or not
        **kwargs: the name and value

    Returns:
        the Original Embed after added fields

    Raises:
        `ValueError` if kwargs count > 25
    """
    if len(kwargs) > 25:
        raise ValueError("you can only add 25 fields in one embed!")

    for name, value in kwargs.items():
        replaced = name.replace("_", " ")
        embed.add_field(
            name=replaced.title() if title_all_name else replaced,
            value=value,
            inline=all_inline
        )

    return embed
