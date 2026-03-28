"""
Load cogs from user imported dir ( default this Dir )
"""

from pathlib import Path
from discord.ext import commands
from utils.logger import get_logger

logger, *_ = get_logger(__name__)

this_file: str = Path(__file__).name
default_dir: Path = Path(__file__).parent


class CogsFinder:
    def __init__(self, bot: commands.Bot, cogs_dir: str | Path = default_dir) -> None:
        self.bot = bot
        self.cogs_dir = Path(cogs_dir)

    async def load_cogs(self) -> tuple[int, int]:
        """
        load all cogs in cogs_dir

        Returns:
            successcount and failed count
        """
        logger.debug("start loading in %s", self.cogs_dir)
        successcount = 0
        failcount = 0
        for file in self.cogs_dir.iterdir():
            if file.name == this_file:
                continue
            if file.name.endswith(".py") and not file.name.startswith("_"):
                try:
                    await self.bot.load_extension(f"{self.cogs_dir.name}.{file.stem}")
                    logger.debug("Loaded cog: %s", file.name)
                    successcount += 1
                except Exception as e:
                    logger.exception("Failed to load cog %s: %s", file.name, str(e))
                    failcount += 1
        logger.debug(
            "Finished loading cogs. Success: %i, Failures: %i", successcount, failcount
        )
        return successcount, failcount

    async def reload_cog(self, name: str | Path) -> bool:
        """
        reload the cog specific by cogs name or Path
        Returns:
            Successful or not
        """
        cog_path = self.cogs_dir / name
        if (
            not cog_path.exists()
            or not cog_path.name.endswith(".py")
            or cog_path.name.startswith("_")
        ):
            return False

        try:
            await self.bot.reload_extension(f"{self.cogs_dir}.{cog_path.stem}")
            return True
        except Exception as e:
            logger.exception("Failed to load cog %s: %s", name, e)
            return False

    async def reload_cogs(self) -> tuple[int, int]:
        """
        reload all cogs

        Returns:
            successcount and Failed count
        """
        logger.debug("start reload for %s", self.cogs_dir)
        successcount = 0
        failcount = 0
        for file in self.cogs_dir.iterdir():
            if file.name == this_file:
                continue
            if await self.reload_cog(file):
                logger.debug("successfully reloaded cog %s", file.name)
                successcount += 1
            else:
                failcount += 1

        return successcount, failcount

    def list_cogs(self) -> list[str]:
        return list(self.bot.cogs.keys())
