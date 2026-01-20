"""
Main pointer
"""
import asyncio
import subprocess
from aiohttp.client_exceptions import ConnectionTimeoutError
import discord
import sys
from pathlib import Path
from discord.ext import commands
from cogs.cogs_finder import CogsFinder
from config.config_loader import ConfigLoader
from utils.logger import get_logger

logger = get_logger(__name__)

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

    await asyncio.sleep(2.0)

    if thread.poll() is not None:
        logger.warning(
            "failed to start backend file!, return code: %i", thread.poll())
    else:
        logger.info("start successful")

# load configs
config_loader: ConfigLoader = ConfigLoader()
token: str = config_loader.load_token()

config = config_loader.load_config()

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
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(
        title="Pong!",
        description=f"Latency: {round(interaction.client.latency * 1000)}ms",
        color=discord.Color.green()
    )
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="help", description="Show help message")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help",
        description="This is a help message.",
        color=discord.Color.blue()
    )
    embed.add_field(name="/ping", value="Check bot latency", inline=False)
    embed.add_field(name="/help", value="Show this help message", inline=False)
    embed.add_field(name="/listcogs",
                    value="List all loaded cogs", inline=False)
    for cog in cogs:
        embed.add_field(name=f"Cog: {cog}", value="Loaded cog", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="listcogs", description="List all loaded cogs")
async def list_cogs(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Loaded Cogs",
        description="\n".join(cogs) if cogs else "No cogs loaded.",
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# prints and sync when ready
@bot.event
async def on_ready() -> None:

    assert bot.user is not None, "how is did?!"

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
    await bot.start(token)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt handled! exiting...")
    except ConnectionTimeoutError:
        logger.warning("Connection Error! try check your connection")
