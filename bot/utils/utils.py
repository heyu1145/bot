"""
an utils function include all unknown type func
"""
from collections.abc import Awaitable, Callable, Sequence
from typing import Literal, Protocol, TypedDict, cast, overload
import inspect
import discord
from discord.ext import commands

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
    if inspect.iscoroutinefunction(func):
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


type StringLike = ToStringAble | ToReprAble


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

class GroupSub(TypedDict):
    subcommands: list[discord.app_commands.Command]
    subgroups: dict[discord.app_commands.Group, 'GroupSub']

type RootTree = dict[Literal["__root__"], GroupSub]

def convert_sub_tree(bot: commands.Bot, /) -> RootTree:
    """
    Convert bot's tree to a sub tree

    Args:
        bot: the bot to read tree

    Returns:
        the root sub tree

    Note:
        for command/group which have no parents, their parent will set to str named '__root__'
    """
    sub_tree: RootTree = {
            "__root__": {
                "subcommands": [],
                "subgroups": {}
                }
            }
    for cmd in bot.tree.walk_commands(type=discord.AppCommandType.chat_input):
        current_tree = sub_tree["__root__"]
        parents: list[discord.app_commands.Group] = []

        temp = cmd.parent

        while temp is not None:
            parents.append(temp)
            temp = temp.parent

        for p in reversed(parents):
            if p not in current_tree["subgroups"]:
                current_tree["subgroups"][p] = {"subcommands":[], "subgroups":{}}
            current_tree = current_tree["subgroups"][p]

        if isinstance(cmd, discord.app_commands.Group):
            if cmd not in current_tree["subgroups"]:
                current_tree["subgroups"][cmd] = {"subcommands":[], "subgroups":{}}
        else:
            if cmd not in current_tree["subcommands"]:
                current_tree["subcommands"].append(cmd)

    return sub_tree

class JSONGroupSub(TypedDict):
    subcommands:list[str]
    subgroups:dict[str, 'JSONGroupSub']

type JSONRootTree = dict[Literal["__root__"], JSONGroupSub]

def jsonify_sub_tree(tree: RootTree, /) -> JSONRootTree:
    """
    jsonify the sub tree to jsonified

    Args:
        tree: the tree to jsonify

    Returns:
        tree after jsonify
    """
    def jsonify(groupsub: GroupSub, /) -> JSONGroupSub:
        return {
                "subcommands": [cmd.name for cmd in groupsub["subcommands"]],
                "subgroups": {group.name: jsonify(sub) for group, sub in groupsub["subgroups"].items()}
                }

    return {
            "__root__":jsonify(tree["__root__"])
            }
