"""
base of a cog
"""
import discord
from discord import app_commands
from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        return await super().cog_load()

    async def cog_unload(self) -> None:
        return await super().cog_unload()

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        return await super().cog_app_command_error(interaction, error)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BaseCog(bot))
