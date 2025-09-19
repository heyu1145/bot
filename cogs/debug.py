import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.permissions import is_trusted_user

logger = logging.getLogger("Debug")

class Debugging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="debug", description="Debug logging utility")
    @app_commands.describe(debug_type="The type of debug output")
    @app_commands.choices(debug_type=[
        app_commands.Choice(name="All Levels", value="all"),
        app_commands.Choice(name="Info", value="info"),
        app_commands.Choice(name="Debug", value="debug"),
        app_commands.Choice(name="Warning", value="warning"),
        app_commands.Choice(name="Error", value="error")
    ])
    async def debug_command(self, interaction: discord.Interaction, debug_type: app_commands.Choice[str]):
        if not is_trusted_user(interaction.user.id):
            return await interaction.response.send_message("❌ Access denied", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        user_info = f"{interaction.user} (ID: {interaction.user.id})"
        message = f"User {user_info} executed debug command with type: {debug_type.value}"
        
        # Handle logging
        log_actions = {
            "all": lambda: [logger.info(message), logger.debug(message), 
                           logger.warning(message), logger.error(message)],
            "info": lambda: logger.info(message),
            "debug": lambda: logger.debug(message),
            "warning": lambda: logger.warning(message),
            "error": lambda: logger.error(message)
        }
        
        log_actions[debug_type.value]()
        
        await interaction.followup.send("✅ Debug logging completed", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Debugging(bot))
