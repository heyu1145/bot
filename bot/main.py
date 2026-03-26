"""
Main pointer
"""
import asyncio
from collections.abc import Callable
import datetime
import json
import signal
import sys
import subprocess
from pathlib import Path
from random import choice, uniform
from types import FrameType
from typing import NoReturn
from aiohttp.client_exceptions import ConnectionTimeoutError
import discord
from discord import app_commands
from discord.ext import commands, tasks
from cogs.cogs_finder import CogsFinder
from config.config_loader import ConfigLoader
from utils.logger import get_logger
from utils.utils import convert_sub_tree, jsonify_sub_tree

logger, *_ = get_logger(__name__)

cogs: list[str] = []

ACTIVITY_CODE: dict[str, list[str]] = {
    "coding": [
        "print(\"hello world!\")",
        "Compiling...",
        "Debugging errors",
        "Writing some code",
        "Waiting for CI/CD pipeline",
        "Choosing from 0 and 1",
        "Naming foos and bars",
    ],
    "gaming": [
        "Playing chess",
        "Mining in Minecraft",
        "Playing Roblox",
        "Building 90s in fortnite",
        "Finding Mario's princess",
        "Looking for diamonds",
        "Racing through tracks",
    ],
    "music": [
        "Listening to tunes",
        "Composing a new song",
        "Jamming to beats",
        "Mixing tracks",
        "Making some lo-fis",
    ],
    "reading": [
        "Reading a thrilling novel",
        "Exploring new worlds in books",
        "Learning new things",
        "Diving into fantasy realms",
        "Studying fascinating topics",
        "Trying to understand manuals...",
    ],
    "other": [
        "Chatting with friends",
        "Watching a movie",
        "Cooking a delicious meal",
        "Traveling the world",
        "Exercising and staying fit",
        "Meditating for peace",
        "Editing photos",
        "Choosing a new hobby",
        "Completing tasks",
    ],
    "puns": [
        "Resolving Promises",
        "Thinking about this and that",
        "Awaiting results",
        "Handling callbacks",
        "Cutting Threads",
        "Running Loops",
        "Fetching Data",
    ],
    "ai": [
        "Generating text...",
        "Analyzing data...",
        "Learning from patterns...",
        "Creating art...",
        "Understanding language...",
        "Deep Thinking...",
        "Planning ideas...",
    ],
}

backend_process: subprocess.Popen[bytes] | None = None

# use subprocess to run backend_file


async def run_service() -> None:
    logger.info("start run the backend file")

    path = (Path(".") / "ext" / "service.py").resolve()

    # check the file exsits
    if not path.exists():
        logger.warning(
            "backend file (%s) no found! front service may dont work",
            path.relative_to(".")
        )
        return

    process = subprocess.Popen(
        [sys.executable, str(path)],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    global backend_process
    backend_process = process

    # wait a small random time to check the process
    await asyncio.sleep(uniform(2, 4))

    if process.poll() is not None:
        backend_process = None
        logger.warning(
            "failed to start backend file!, return code: %i", process.poll())
    else:
        logger.info("start successful")


def cleanup() -> None:
    global backend_process
    if not backend_process or backend_process.poll() is not None:
        logger.info("backend process exited.")
        return

    logger.debug("terminating backend...")
    backend_process.terminate()
    try:
        backend_process.wait(uniform(2, 4))
    except subprocess.TimeoutExpired:
        logger.warning("terminate failed, killing it...")
        backend_process.kill()


def signal_handler(sig: int, frame: FrameType | None) -> NoReturn:
    _ = frame
    logger.debug("handled signal %i, exiting...", sig)
    cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# load configs
config_loader: ConfigLoader = ConfigLoader()
token: str = config_loader.load_token()

config: dict = config_loader.load_config()

# bot setup
intents: discord.Intents = discord.Intents.default()
intents.guild_scheduled_events = True

bot: commands.Bot = commands.Bot(
    command_prefix=config.get("prefix", "!"),
    intents=intents
)


# default commands: ping, help, listCogs
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction) -> None:
    logger.debug('%s runned the ping command', interaction.user.display_name)

    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="Pong!",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"requested by {interaction.user.name}")
    embed.add_field(
        name="bot username",
        value=interaction.client.user.name,  # type: ignore[optional]
        inline=False
    )
    embed.add_field(
        name="latency",
        value=f"{round(interaction.client.latency * 1000, 2)}ms",
        inline=False
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="help", description="Show help message")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help",
        description="This is a help message.",
        color=discord.Color.blue()
    )
    for cmd in bot.tree.walk_commands():
        if isinstance(cmd, app_commands.Group):
            continue
        parents: list[str] = []
        temp = cmd
        while temp is not None:
            parents.append(temp.name)
            temp = temp.parent

        embed.add_field(name=f"/" + " ".join(reversed(parents)),
                        value=cmd.description, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="listcogs", description="List all loaded cogs")
async def list_cogs(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Loaded Cogs",
        description="\n".join(cogs) if cogs else "No cogs loaded.",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# handle the error of command


@bot.event
async def on_command_error(ctx: commands.Context, error: discord.errors.DiscordException) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    logger.exception("failed to run command, error: %s", error)
    await ctx.send(f"raised an error while running command, error: {error}")


@bot.tree.error
async def on_app_command_error(
        interaction: discord.Interaction,
        error: app_commands.errors.AppCommandError
) -> None:
    if interaction.response.is_done():
        send = interaction.followup.send
    else:
        send = interaction.response.send_message

    embed = discord.Embed(
        title="Error",
        description=error,
        color=0xff0000,
        timestamp=discord.utils.utcnow()
    )
    logger.exception("Error while running command %s, \n\nerror: %s",
                     interaction.command.name
                     if interaction.command else "Unknown name",
                     error
                     )

    await send(embed=embed, ephemeral=True)


STATUS_RULES: list[
    Callable[
        [datetime.datetime, str],
        tuple[bool, discord.Status]
    ]
] = [
    (lambda _, key: (key in ["coding"], discord.Status.dnd)),
    (lambda now, _: (now.hour <= 5 or now.hour >= 22, discord.Status.idle)),
    (lambda *_: (True, discord.Status.online))  # default
]

ACTIVITY_RULES: list[
    Callable[
            [datetime.datetime, str, str],
        tuple[bool, discord.activity.BaseActivity]
    ]
] = [
    (lambda _, key, value: (key in ["music"], discord.Activity(
        type=discord.ActivityType.listening, name=value))),
    (lambda _, __, value: (True, discord.activity.CustomActivity(name=value))),  # default
]


def get_status(now: datetime.datetime, activity_key: str) -> discord.Status:
    """get status based on time and status key"""
    for func in STATUS_RULES:
        check, status = func(now, activity_key)
        if check:
            return status
    return discord.Status.online


def get_activity(now: datetime.datetime, activity_key: str, activity_msg: str) -> discord.activity.BaseActivity:
    """get activity type by now and status key"""
    for func in ACTIVITY_RULES:
        check, activity = func(now, activity_key, activity_msg)
        if check:
            return activity
    return discord.activity.CustomActivity(name=activity_msg)

# adding activity handler task


@tasks.loop(minutes=10)
async def set_activity() -> None:
    """set bot activity randomly"""
    now = discord.utils.utcnow()
    logger.debug("Setting activity at %s", now.isoformat())
    activity_key = choice(list(ACTIVITY_CODE.keys()))
    activity_msg = choice(ACTIVITY_CODE[activity_key])
    await bot.change_presence(
        status=get_status(now, activity_key),
        activity=get_activity(now, activity_key, activity_msg)
    )
    logger.info("Activity set to type: %s, name: %s",
                activity_key, activity_msg)

# prints and sync when ready


@bot.event
async def on_ready() -> None:
    if not bot.user:
        logger.error("How the bot user is None???")
        return

    logger.info(
        "logged in as %s (id: %s)",
        bot.user.name,
        bot.user.id
    )
    await bot.tree.sync()
    logger.info(
        "Loaded Commands: %i",
        len(list(bot.tree.walk_commands()))
    )
    logger.info("current tree:")
    logger.info(json.dumps(
        jsonify_sub_tree(
            convert_sub_tree(bot)
        ),
        indent=4, ensure_ascii=False
    )
    )
    set_activity.start()


async def main() -> None:
    # load cogs
    cogs_finder = CogsFinder(bot)
    successcount, failcount = await cogs_finder.load_cogs()
    global cogs
    cogs = cogs_finder.listCogs()
    logger.info("Cogs loaded: %i successful, %i failed.",
                successcount, failcount)

    # start backend server
    await run_service()

    # run bot
    try:
        await bot.start(token)
    except ConnectionTimeoutError:
        logger.error("Connection Timed Out, Check your connection")
    except discord.LoginFailure as e:
        logger.exception("Login failed! error: %s", e)
        raise

if __name__ == "__main__":
    asyncio.run(main())
else:
    logger.warning("you should not run it by module!")
