"""
Main pointer
"""

import asyncio
import json
import signal
import sys
import subprocess
from pathlib import Path
from random import uniform
from types import FrameType
from typing import NoReturn
from aiohttp.client_exceptions import ConnectionTimeoutError
import dotenv
import discord
from discord import app_commands
from discord.ext import commands
from bot_tasks import activate_activity_task, activate_reload_task
from cogs.cogs_finder import CogsFinder
from utils.logger import get_logger
from utils.utils import convert_sub_tree, jsonify_sub_tree, frame_back_n

logger, *_ = get_logger(__name__)


BACKEND_PROCESS: subprocess.Popen[bytes] | None = None
THIS_DIR: Path = Path(__file__).parent.resolve()
TOKEN_KEY: str = "TOKEN"

all_cogs: list[str] = []  # list of all cogs, will be filled by CogsFinder

# use subprocess to run backend_file


async def run_service() -> None:
    logger.info("start run the backend file")

    path = (THIS_DIR / "ext" / "service.py").resolve()

    # check the file exsits
    if not path.exists():
        logger.warning(
            "backend file (%s) no found! front service may dont work", path)
        return

    process = subprocess.Popen(
        [sys.executable, str(path)], stdout=sys.stdout, stderr=sys.stderr
    )

    global BACKEND_PROCESS
    BACKEND_PROCESS = process

    # wait a small random time to check the process
    await asyncio.sleep(uniform(2, 4))

    if process.poll() is not None:
        BACKEND_PROCESS = None
        logger.warning(
            "failed to start backend file!, return code: %i", process.poll())
    else:
        logger.info("start successful")


def cleanup() -> None:
    if not BACKEND_PROCESS or BACKEND_PROCESS.poll() is not None:
        logger.info("backend process exited.")
        return

    logger.debug("terminating backend...")
    BACKEND_PROCESS.terminate()
    try:
        BACKEND_PROCESS.wait(uniform(2, 4))
        logger.debug("backend terminated.")
    except subprocess.TimeoutExpired:
        logger.warning("terminate failed, killing it...")
        BACKEND_PROCESS.kill()


def signal_handler(sig: int, frame: FrameType | None) -> NoReturn:
    if frame:
        _, count, frame = frame_back_n(frame, 10)
        logger.debug("frame num %i: frame log: file: %s, running line: %s, func name: %s",
                     count, frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name)
    logger.debug("handled signal %i, exiting...", sig)
    cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# load token from .env file
dotenv_pathstr = dotenv.find_dotenv()
if not dotenv_pathstr:
    logger.error("No .env file found in %s or parent directories", THIS_DIR)
    raise FileNotFoundError(
        "No .env file found, please copy .env.example to .env and set your token")

dotenv_path = Path(dotenv_pathstr)

value: str | None = dotenv.get_key(
    dotenv_path, TOKEN_KEY, encoding=sys.getdefaultencoding())

if value:
    logger.debug("Loaded token from file %s", dotenv_path)
    token: str = value
else:
    logger.critical("Failed to load token")
    raise RuntimeError(
        f"Failed to load token, please set the token in the .env file with the key {TOKEN_KEY}"
    )


# bot setup
intents: discord.Intents = discord.Intents.default()
intents.guild_scheduled_events = True

bot: commands.Bot = commands.Bot(
    command_prefix="!", intents=intents
)


# default commands: ping, help
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction) -> None:
    logger.debug("%s runned the ping command", interaction.user.display_name)

    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="Pong!", color=discord.Color.green(), timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"requested by {interaction.user.name}")
    embed.add_field(
        name="bot username",
        value=interaction.client.user.name,  # type: ignore[union-attr]
        inline=False,
    )
    embed.add_field(
        name="latency",
        value=f"{round(interaction.client.latency * 1000, 2)}ms",
        inline=False,
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="help", description="Show help message")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help", description="This is a help message.", color=discord.Color.blue()
    )
    for cmd in bot.tree.walk_commands():
        if isinstance(cmd, app_commands.Group):
            continue
        parents: list[str] = []
        temp: app_commands.Command | app_commands.Group | None = cmd
        while temp is not None:
            parents.append(temp.name)
            temp = temp.parent

        embed.add_field(
            name="/" + " ".join(reversed(parents)), value=cmd.description, inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# handle the error of command


@bot.event
async def on_command_error(
    ctx: commands.Context, error: discord.errors.DiscordException
) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    logger.exception("failed to run command, error: %s", error)
    await ctx.send(f"raised an error while running command, error: {error}")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.errors.AppCommandError
) -> None:
    embed = discord.Embed(
        title="Error",
        description=error,
        color=0xFF0000,
        timestamp=discord.utils.utcnow(),
    )
    logger.exception(
        "Error while running command %s, \n\nerror: %s",
        interaction.command.name if interaction.command else "Unknown name",
        error,
    )
    if not interaction.response.is_done():
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        except discord.InteractionResponded:
            pass  # to the followup

    await interaction.followup.send(embed=embed, ephemeral=True)


# prints and sync when ready


@bot.event
async def on_ready() -> None:
    if not bot.user:
        logger.error("How the bot user is None???")
        raise RuntimeError("Bot user is None")

    logger.info("logged in as %s (id: %s)", bot.user.name, bot.user.id)
    await bot.tree.sync()
    logger.info("Loaded Commands: %i", len(list(bot.tree.walk_commands())))
    logger.debug("current tree:")
    logger.debug(
        json.dumps(
            jsonify_sub_tree(convert_sub_tree(bot)), indent=4, ensure_ascii=False
        )
    )
    activate_activity_task(bot).start()
    activate_reload_task(bot).start()


async def main() -> None:
    # load cogs
    cogs_finder = CogsFinder(bot)
    successcount, failcount = await cogs_finder.load_cogs()
    global all_cogs
    all_cogs = cogs_finder.list_cogs()
    logger.info("Cogs loaded: %i successful, %i failed.",
                successcount, failcount)

    # start backend server
    await run_service()

    # run bot
    try:
        await bot.start(token)
    except ConnectionTimeoutError:
        logger.error(
            "Connection Timed Out, Please check your connection and try again")
    except discord.RateLimited:
        logger.error(
            "You are being rate limited by Discord, please wait and try again later")
    except discord.PrivilegedIntentsRequired:
        logger.error(
            "Privileged intents are required to run the bot,"
            "please enable them in the Discord Developer Portal")
    except discord.LoginFailure as e:
        error_msg = str(e)
        if "Improper token has been passed" in error_msg:
            logger.error(
                "Login failed! Invalid token provided. Please check your .env file and ensure the TOKEN key is set correctly."
            )
        else:
            logger.exception("Login failed! error: %s", e)
    finally:
        cleanup()


if __name__ == "__main__":
    asyncio.run(main())
else:
    logger.warning("you should not run it by module, exiting...")
