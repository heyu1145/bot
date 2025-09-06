import discord
from discord.ext import commands
import os
import asyncio
import logging
import time
from keep_alive import keep_alive, update_bot_status

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('discord_bot')

# Start the keep-alive server
keep_alive()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load cogs automatically
async def load_cogs():
    loaded_commands = 0
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Loaded cog: {filename[:-3]}")
                loaded_commands += 1
            except Exception as e:
                logger.error(f"Failed to load cog {filename}: {e}")
    return loaded_commands

@bot.event
async def on_ready():
    # Count total users across all servers
    total_users = sum(guild.member_count for guild in bot.guilds)
    
    # Update status
    update_bot_status(
        online=True,
        servers=len(bot.guilds),
        commands_loaded=len(bot.commands),
        users=total_users
    )
    
    logger.info(f"Logged in as {bot.user.name}")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Connected to {len(bot.guilds)} server(s)")
    logger.info(f"Serving {total_users} users")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error(f"Command error: {error}")

# Ping command
@bot.tree.command(name="ping", description="Check bot latency and status")
async def ping(interaction: discord.Interaction):
    start_time = time.time()
    
    # Calculate latency
    latency = round(bot.latency * 1000)  # Convert to ms
    
    # Create embed
    embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(name="Bot Latency", value=f"`{latency}ms`", inline=True)
    embed.add_field(name="API Latency", value=f"`{round((time.time() - start_time) * 1000)}ms`", inline=True)
    embed.add_field(name="Servers", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="Uptime", value=f"`{get_uptime()}`", inline=True)
    embed.add_field(name="Users", value=f"`{sum(guild.member_count for guild in bot.guilds)}`", inline=True)
    embed.add_field(name="Commands", value=f"`{len(bot.commands)}`", inline=True)
    
    embed.set_footer(text=f"Requested by {interaction.user.display_name}")
    
    await interaction.response.send_message(embed=embed)

def get_uptime():
    """Calculate bot uptime in human readable format"""
    if not bot.start_time:
        return "Not available"
    
    uptime_seconds = int(time.time() - bot.start_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

# Store bot start time
bot.start_time = time.time()

# Run the bot
async def main():
    async with bot:
        loaded_commands = await load_cogs()
        update_bot_status(commands_loaded=loaded_commands)
        
        # Get token from environment variable
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logger.error("DISCORD_BOT_TOKEN environment variable not set!")
            return
        
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())