# User Custom Modules Guide

## Overview

This guide explains how to create and integrate custom modules (cogs) into the Discord bot. The bot features an auto-cog loading system that automatically discovers and loads all extension modules in the `cogs/` directory.

## Adding Custom Cogs

### Basic Structure

To create a new custom cog, create a Python file in the `cogs/` directory with the following structure:

```python
import discord
from discord.ext import commands
from config.config import DISCORD_CONFIG
from utils.storage import load_trusted_users
from utils.permissions import has_data_access

class MyCustomCog(commands.Cog, name="My Custom"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.qualified_name} is ready.')

    @commands.command(name='hello')
    async def hello_command(self, ctx):
        await ctx.send(f'Hello, {ctx.author.mention}!')

    @discord.app_commands.command(name="greet", description="Greet a user")
    async def greet slash_command(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        await interaction.response.send_message(f'Hello, {user.mention}!')

async def setup(bot):
    await bot.add_cog(MyCustomCog(bot))
```

### Steps to Add a New Module

1. Create a new Python file in the `cogs/` directory (e.g., `my_custom_cog.py`)
2. Implement your commands and features using the Discord.py Cog structure
3. Include a `setup()` function to register the cog
4. The bot will automatically discover and load your new cog on restart

## Auto-Cog Loading System

### How It Works
- Automatically discovers all `.py` files in the `cogs/` directory (excluding `__init__.py`)
- Loads each module as a cog extension when the bot starts
- Provides detailed logging of loading status and errors

### Adding New Cogs
To add new functionality:
1. Create a new Python file in the `cogs/` directory
2. Follow the standard cog structure with a setup function
3. The bot will automatically discover and load it on restart

### Excluding Specific Cogs
To exclude specific cogs from loading, modify the `load_cogs` function in `bot.py`:
```python
load_result = await cog_loader.load_all_cogs(exclude_cogs=['cogs.debug'])
```

## Best Practices for Custom Modules

### 1. Follow Naming Conventions
- Use descriptive names for your cog files: `moderation.py`, `utilities.py`
- Use PascalCase for class names: `ModerationCog`, `UtilityCog`
- Use snake_case for function names: `ban_user`, `clean_messages`

### 2. Include Proper Error Handling
```python
@commands.command(name='my_command')
async def my_command(self, ctx):
    try:
        # Your command logic
        await ctx.send("Success!")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
```

### 3. Use Proper Permissions
```python
@commands.command(name='admin_command')
@commands.has_permissions(administrator=True)
async def admin_command(self, ctx):
    await ctx.send("This is an admin command")
```

### 4. Implement Slash Commands for Better UX
```python
@discord.app_commands.command(name="my_command", description="Description of command")
@discord.app_commands.describe(parameter1="Description of parameter")
async def my_slash_command(self, interaction: discord.Interaction, parameter1: str):
    await interaction.response.send_message(f"You provided: {parameter1}")
```

## Using Bot Utilities in Custom Modules

### Storage Utilities
```python
from utils.storage import (
    load_trusted_users, add_trusted_user,
    load_active_tickets, save_active_ticket
)

# Example usage
trusted_users = load_trusted_users(ctx.guild.id)
if str(ctx.author.id) in trusted_users:
    # User has special access
```

### Permission Utilities
```python
from utils.permissions import is_admin_or_owner, has_data_access

# Example usage
if is_admin_or_owner(ctx):
    # Perform admin action
```

### Data Management
```python
from utils.data_storage import data_manager

# Access custom data
data = data_manager.get_data(guild_id, "my_custom_data")
```

## Example: Creating a Simple Utility Cog

Here's a complete example of a custom utility cog:

```python
import discord
from discord.ext import commands
import datetime
from utils.permissions import is_admin_or_owner

class UtilityCog(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="server_info", description="Get information about the server")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"Info about {guild.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="user_info", description="Get information about a user")
    @discord.app_commands.describe(user="The user to get info for")
    async def user_info(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"Info about {user.display_name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Joined", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @commands.command(name='echo')
    async def echo_command(self, ctx, *, message):
        """Echo back the provided message"""
        if is_admin_or_owner(ctx):
            await ctx.send(message)
        else:
            await ctx.send("You don't have permission to use this command.")

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
```

## Testing Custom Modules

### Before Deployment
1. Test in a development server first
2. Verify all commands work as expected
3. Check error handling for edge cases
4. Ensure proper permissions are enforced

### Common Testing Scenarios
- Commands with no parameters
- Commands with required parameters
- Commands with optional parameters
- Commands with invalid inputs
- Permission-restricted commands

## Troubleshooting

### Common Issues

1. **Cog not loading**: Ensure your file has a `setup()` function
2. **Commands not working**: Check that your cog class inherits from `commands.Cog`
3. **Import errors**: Verify all imports are available in your environment
4. **Permission issues**: Double-check permission decorators

### Debugging Tips
- Check the bot logs for loading errors
- Use `!ping` or `/ping` to verify the bot is running
- Test commands in a private channel first
- Use the debug cog if available for detailed logs

## Advanced Features

### Using Views and Modals
```python
class MyView(discord.ui.View):
    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Button clicked!")

@discord.app_commands.command(name="show_view", description="Show an interactive view")
async def show_view(self, interaction: discord.Interaction):
    view = MyView()
    await interaction.response.send_message("Here's a view:", view=view)
```

### Background Tasks
```python
import asyncio

async def my_background_task(self):
    await self.bot.wait_until_ready()
    while not self.bot.is_closed():
        # Your task logic here
        await asyncio.sleep(300)  # Run every 5 minutes

def cog_load(self):
    self.bg_task = self.bot.loop.create_task(self.my_background_task())
```

This system allows for easy extension of the bot's functionality while maintaining consistency with the existing architecture.