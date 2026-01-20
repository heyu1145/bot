"""
Load cogs from user imported dir ( default this Dir )
"""

from logging import Logger
from pathlib import Path
from discord.ext import commands
from utils.logger import get_logger

logger: Logger = get_logger(__name__)

this_file: str = Path(__file__).name
default_dir: str = Path(__file__).parent.name


class CogsFinder:
    def __init__(self, bot: commands.Bot, cogs_dir: str = default_dir) -> None:
        self.bot = bot
        self.cogs_dir = cogs_dir

    async def load_cogs(self) -> tuple[int, int]:
        successcount = 0
        failcount = 0
        for file in Path(self.cogs_dir).iterdir():
            if file.name == this_file:
                continue
            if file.name.endswith(".py") and not file.name.startswith("_"):
                try:
                    await self.bot.load_extension(f"{self.cogs_dir}.{file.stem}")
                    logger.info("Loaded cog: %s", file.name)
                    successcount += 1
                except Exception as e:
                    logger.exception("Failed to load cog %s: %s",
                                     file.name, str(e))
                    failcount += 1
        logger.info(
            "Finished loading cogs. Success: %i, Failures: %i", successcount, failcount)
        return successcount, failcount

    def listCogs(self) -> list[str]:
        return list(self.bot.cogs.keys())
