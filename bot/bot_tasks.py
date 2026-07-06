"""
bot tasks
"""
from collections.abc import Callable
import datetime
from random import choice
from pathlib import Path
import discord
from discord.ext import commands, tasks
from utils.logger import get_logger

logger, *_ = get_logger(__name__)

THIS_FILE = Path(__file__)
THIS_DIR = THIS_FILE.parent
COG_DIR_NAME = "cogs"
SKIP_RELOAD_FILE_NAMES = ["cogs_finder.py"]

ACTIVITY_CODE: dict[str, list[str]] = {
    "coding": [
        'print("hello world!")',
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

STATUS_RULES: list[Callable[[datetime.datetime, str], tuple[bool, discord.Status]]] = [
    (lambda _, key: (key in ["coding"], discord.Status.dnd)),
    (lambda now, _: (now.hour <= 5 or now.hour >= 22, discord.Status.idle)),
    (lambda *_: (True, discord.Status.online)),  # default
]

ACTIVITY_RULES: list[
    Callable[[datetime.datetime, str, str],
             tuple[bool, discord.activity.BaseActivity]]
] = [
    (
        lambda _, key, value: (
            key in ["music"],
            discord.Activity(type=discord.ActivityType.listening, name=value),
        )
    ),
    (
        lambda _, __, value: (
            True, discord.activity.CustomActivity(name=value))
    ),  # default
]


def get_status(now: datetime.datetime, activity_key: str) -> discord.Status:
    """get status based on time and status key"""
    for func in STATUS_RULES:
        check, status = func(now, activity_key)
        if check:
            return status
    return discord.Status.online


def get_activity(
    now: datetime.datetime, activity_key: str, activity_msg: str
) -> discord.activity.BaseActivity:
    """get activity type by now and status key"""
    for func in ACTIVITY_RULES:
        check, activity = func(now, activity_key, activity_msg)
        if check:
            return activity
    return discord.activity.CustomActivity(name=activity_msg)


# adding activity handler task


def activate_activity_task(bot: commands.Bot) -> tasks.Loop:
    @tasks.loop(minutes=10)
    async def set_activity() -> None:
        """set bot activity randomly"""
        now = discord.utils.utcnow()
        logger.debug("Setting activity at %s", now.isoformat())
        activity_key = choice(list(ACTIVITY_CODE.keys()))
        activity_msg = choice(ACTIVITY_CODE[activity_key])
        await bot.change_presence(
            status=get_status(now, activity_key),
            activity=get_activity(now, activity_key, activity_msg),
        )
        logger.info("Activity set to type: %s, name: %s",
                    activity_key, activity_msg)

    return set_activity


def activate_reload_task(bot: commands.Bot) -> tasks.Loop:
    skip_reload: bool = False
    old_cog_hash: dict[str, int] = {}

    @tasks.loop(seconds=30)
    async def auto_reload() -> None:
        """auto reload cog when they update"""
        nonlocal skip_reload
        nonlocal old_cog_hash
        if skip_reload:
            return

        cog_dir = THIS_DIR / COG_DIR_NAME
        if not cog_dir.exists():
            logger.warning("cog_dir not exists, skipping cog reload")
            skip_reload = True
            return

        for cog_file in cog_dir.glob("*.py"):
            if cog_file.name in SKIP_RELOAD_FILE_NAMES or cog_file.name.startswith("_"):
                logger.debug("Skipping cog file: %s", cog_file.name)
                continue

            cog_name = f"{COG_DIR_NAME}.{cog_file.stem}"

            if cog_name not in old_cog_hash:
                old_cog_hash[cog_name] = hash(cog_file.read_bytes())
                logger.debug("Added cog: %s to hash", cog_name)
                if cog_name not in bot.extensions:
                    try:
                        await bot.load_extension(cog_name)
                        logger.info("Loaded new cog: %s, Command count now: %i",
                                    cog_name, len(list(bot.tree.walk_commands())))
                    except Exception as e:
                        logger.error(
                            "Failed to load cog: %s, error: %s", cog_name, e)

                continue

            new_hash = hash(cog_file.read_bytes())
            if new_hash == old_cog_hash[cog_name]:
                logger.debug("No changes detected for cog: %s", cog_name)
                continue

            try:
                await bot.reload_extension(cog_name)
                logger.info("Reloaded cog: %s, Command count now: %i",
                            cog_name, len(list(bot.tree.walk_commands())))
            except Exception as e:
                logger.error(
                    "Failed to reload cog: %s, error: %s", cog_name, e)

    return auto_reload
