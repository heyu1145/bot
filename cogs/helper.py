import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils.helper import get_all_commands, get_command_info
from typing import List, Dict, Any

class HelperCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get all commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        commands = get_all_commands(self.bot)
        embed = discord.Embed(
            title="🤖 Command Help", 
            description="All available commands", 
            color=0xff8800, 
            timestamp=datetime.now()
        )
        
        if isinstance(commands, list) and commands:
            # Group commands by category
            categories = {}
            for command in commands:
                category = "General"
                if hasattr(command, 'binding') and command.binding:
                    category = command.binding.__class__.__name__.replace('Cog', '')
                
                if category not in categories:
                    categories[category] = []
                categories[category].append(command)
            
            # Add fields for each category
            for category, cmd_list in categories.items():
                command_text = "\n".join([f"• `/{cmd.name}` - {cmd.description or 'No description'}" for cmd in cmd_list])
                embed.add_field(
                    name=f"📁 {category}",
                    value=command_text,
                    inline=False
                )
            
            embed.set_footer(text="Use /cmd_info [command] for detailed information")
        else:
            embed.add_field(
                name="❌ No Commands",
                value="No commands were found or the bot is still loading.",
                inline=False
            )
            embed.set_footer(text="Contact Bot Owner for more information")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="cmd_info", description="Get information about a specific command")
    @app_commands.describe(cmd="Command name")
    async def cmd_info(self, interaction: discord.Interaction, cmd: str):
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        # FIXED: discord.Embed (capital E)
        embed = discord.Embed(
            title="🔍 Command Information", 
            description=f"Details for command: `{cmd}`", 
            color=0xff8800, 
            timestamp=datetime.now()
        )
        
        command_info = get_command_info(self.bot, cmd)
        
        if isinstance(command_info, dict):  # FIXED: Check if it's a dict, not list
            # Add basic command info
            embed.add_field(
                name="📝 Command",
                value=f"`/{command_info.get('name', cmd)}`",
                inline=False
            )
            
            embed.add_field(
                name="📋 Description", 
                value=command_info.get('description', 'No description provided'),
                inline=False
            )
            
            # Add parameters/options if they exist
            options = command_info.get('options', [])
            if options:
                params_text = "\n".join([f"• `{param.name}`: {param.description} {'(required)' if param.required else '(optional)'}" for param in options])
                embed.add_field(
                    name="⚙️ Parameters",
                    value=params_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚙️ Parameters",
                    value="No parameters required",
                    inline=False
                )
                
        else:
            embed.add_field(
                name="❌ Command Not Found",
                value=f"The command `{cmd}` was not found. Use `/help` to see available commands.",
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelperCog(bot))