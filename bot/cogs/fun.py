"""fun commands"""
import random
import discord
from discord import app_commands
from discord.ext import commands


class FunCog(commands.Cog):
    """fun command cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dice", description="Roll some dice(s)")
    @app_commands.describe(
        num_dice="Number of dice to roll",
        max_dice_value="Maximum value of the dice"
    )
    async def dice(self, interaction: discord.Interaction, num_dice: int = 1, max_dice_value: int = 6):
        """Rolls a specified number of dice with a specified maximum value."""
        if num_dice < 1 or max_dice_value < 1:
            await interaction.response.send_message("Number of dice and maximum value must be at least 1.", ephemeral=True)
            return

        rolls = [str(random.randint(1, max_dice_value))
                 for _ in range(num_dice)]
        result = ", ".join(rolls)
        await interaction.response.send_message(
            (f"🎲 You rolled: {result}"
             + f" (Total: {sum(int(roll) for roll in rolls)})"
             if num_dice > 1
             else ""
             )
        )


async def setup(bot: commands.Bot) -> None:
    """Setup function for the FunCog."""
    await bot.add_cog(FunCog(bot))
