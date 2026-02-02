"""
Main pointer
"""
import asyncio
import logging
import sys
import subprocess
from pathlib import Path
from aiohttp.client_exceptions import ConnectionTimeoutError
import discord
from discord import app_commands
from discord.ext import commands
from cogs.cogs_finder import CogsFinder
from config.config_loader import ConfigLoader
from utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

cogs: list[str] = []

# use subprocess to run backend_file


async def run_service() -> None:
    logger.info("start run the backend file")

    path = Path("./utils/service.py").resolve()

    # check the file exsits
    if not path.exists():
        logger.warning(
            "backend file (%s) no found! front service may dont work",
            path.relative_to(".")
        )
        return

    thread = subprocess.Popen(
        [sys.executable, str(path)],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    await asyncio.sleep(2.2)

    if thread.poll() is not None:
        logger.warning(
            "failed to start backend file!, return code: %i", thread.poll())
    else:
        logger.info("start successful")

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
async def ping(interaction: discord.Interaction):
    logger.debug('%s runned the ping command', interaction.user.display_name)

    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="Pong!",
        description=f"Client user: {interaction.client.user.name}", # type: ignore[none]
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"requested by {interaction.user.name}")
    embed.add_field(
            name="latency",
            value=f"{round(interaction.client.latency  * 1000, 2)}ms",
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
    for cog in bot.tree.walk_commands():
        embed.add_field(name=cog.name,
                        value=cog.description, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="listcogs", description="List all loaded cogs")
async def list_cogs(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Loaded Cogs",
        description="\n".join(cogs) if cogs else "No cogs loaded.",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# handle the error imof command
@bot.event
async def on_command_error(ctx: commands.Context, error: discord.errors.DiscordException) -> None:
    if isinstance(error, commands.CommandNotFound): return
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
    logger.exception("Error while running command %s, error: %s",
                     interaction.command.name
                     if interaction.command else "Unknown", 
                     error
                     )

    await send(embed=embed, ephemeral=True)


# prints and sync when ready
@bot.event
async def on_ready() -> None:

    assert bot.user is not None, "how it did?!"

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


async def main():
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
    except discord.LoginFailure:
        logger.exception("The token does not exsits in discord! exiting...")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt handled! exiting...")
    except ConnectionTimeoutError:
        logger.warning("Connection Error! try check your connection")
else:
    logger.warning("you should not run it by module!")
