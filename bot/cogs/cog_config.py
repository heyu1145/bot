"""config cogs"""
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from utils.logger import get_logger

logger, *_ = get_logger(__name__)

THIS_FILE = Path(__file__)
COG_DIR = THIS_FILE.parent
COG_DIR_NAME = COG_DIR.name

SKIP_FILE_NAME: set[str] = {"__init__.py", "cog_config.py", "cogs_finder.py"}


class CogConfig(commands.Cog):
    """config cogs"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def extensions(self) -> list[str]:
        return [ext[5:]
                for ext in self.bot.extensions.keys()
                if ext.startswith(f"{COG_DIR_NAME}.")
                ]

    config_group = app_commands.Group(
        name="config_cog", description="Configure the bot cogs")

    @config_group.command(name="enable", description="Enable a cog")
    @app_commands.describe(cog_name="The name of the cog to enable")
    async def enable_cog(self, interaction: discord.Interaction, cog_name: str) -> None:
        """Enable a cog"""
        if cog_name in self.extensions:

            embed = discord.Embed(
                description=f"The cog '{cog_name}' is already enabled.", color=discord.Color.red())

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        await self.bot.load_extension(f"{COG_DIR_NAME}.{cog_name}")
        embed = discord.Embed(
            description=f"The cog '{cog_name}' has been enabled.", color=discord.Color.green())

        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Cog '{cog_name}' has been enabled.")
        # Sync the command tree to register commands from the newly loaded cog
        await self.bot.tree.sync()

    @config_group.command(name="disable", description="Disable a cog")
    @app_commands.describe(cog_name="The name of the cog to disable")
    async def disable_cog(self, interaction: discord.Interaction, cog_name: str) -> None:
        """Disable a cog"""
        if cog_name not in self.extensions:

            embed = discord.Embed(
                description=f"The cog '{cog_name}' is not enabled.", color=discord.Color.red())

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        await self.bot.unload_extension(f"{COG_DIR_NAME}.{cog_name}")
        embed = discord.Embed(
            description=f"The cog '{cog_name}' has been disabled.", color=discord.Color.green())

        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Cog '{cog_name}' has been disabled.")
        # Sync the command tree to unregister commands from the unloaded cog
        await self.bot.tree.sync()

    @config_group.command(name="list", description="List all cogs and their status")
    async def list_cogs(self, interaction: discord.Interaction) -> None:
        """List all cogs and their status"""
        enabled_cogs = self.extensions
        all_cogs = [f.stem for f in COG_DIR.glob(
            "*.py") if f.is_file() and f.name not in SKIP_FILE_NAME]
        disabled_cogs = [cog for cog in all_cogs if cog not in enabled_cogs]

        embed = discord.Embed(title="Cogs Status", color=discord.Color.blue())
        embed.add_field(name="Enabled Cogs", value="\n".join(
            enabled_cogs) if enabled_cogs else "None", inline=False)
        embed.add_field(name="Disabled Cogs", value="\n".join(
            disabled_cogs) if disabled_cogs else "None", inline=False)
        embed.add_field(name="Available Cogs name",
                        value="\n".join(self.bot.cogs.keys()) if self.bot.cogs else "None", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """setup the cog"""
    await bot.add_cog(CogConfig(bot))
