import discord
from discord.ext import commands
import os
import logging
import asyncio
import time
from utils.storage import load_trusted_users, is_bot_owner
from utils.permissions import has_data_access

# Setup logging - KEPT AS IS
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.propagate = False

# Load environment variables - KEPT AS IS
TOKEN = os.getenv('TOKEN')
OWNER_USER_ID = os.getenv('OWNER_USER_ID')

if not TOKEN:
    logger.error("❌ ERROR: No Discord token found! Set TOKEN in environment variables")
    exit(1)

if not OWNER_USER_ID:
    logger.error("❌ ERROR: No owner user ID found! Set OWNER_USER_ID in environment variables")
    exit(1)

# Bot setup - KEPT AS IS
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_scheduled_events = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
bot.start_time = time.time()

# Uptime function - ADDED
def get_uptime():
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

# Load cogs - KEPT AS IS
async def load_cogs():
    try:
        await bot.load_extension('cogs.tickets')
        await bot.load_extension('cogs.events')
        await bot.load_extension('cogs.data_management')
        await bot.load_extension('cogs.admin')
        await bot.load_extension('cogs.help')
        logger.info("✅ All cogs loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load cogs: {e}")

@bot.event
async def on_ready():
    logger.info(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'🔗 Connected to {len(bot.guilds)} server(s)')
    
    await load_cogs()
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"❌ Command sync failed: {e}")

    # Set bot status - ADDED
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(bot.guilds)} servers | use /help to get all commands!"
        )
    )

# Enhanced ping command - UPDATED
@bot.tree.command(name="ping", description="Check the bot's response time and status")
async def ping(interaction: discord.Interaction):
    start_time = time.time()
    latency = round(bot.latency * 1000)
    api_latency = round((time.time() - start_time) * 1000)
    
    embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
    embed.add_field(name="Bot Latency", value=f"`{latency}ms`", inline=True)
    embed.add_field(name="API Response", value=f"`{api_latency}ms`", inline=True)
    embed.add_field(name="Uptime", value=f"`{get_uptime()}`", inline=True)
    embed.add_field(name="Servers", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="Users", value=f"`{sum(guild.member_count for guild in bot.guilds)}`", inline=True)
    embed.add_field(name="Cogs Loaded", value=f"`{len(bot.cogs)}`", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Enhanced bot_info command - UPDATED
@bot.tree.command(name="bot_info", description="Get detailed bot information")
async def bot_info(interaction: discord.Interaction):
    total_users = sum(guild.member_count for guild in bot.guilds)
    
    embed = discord.Embed(title="🤖 Bot Information", color=discord.Color.blue())
    embed.add_field(name="Name", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Total Users", value=total_users, inline=True)
    embed.add_field(name="Uptime", value=get_uptime(), inline=True)
    embed.add_field(name="Cogs Loaded", value=len(bot.cogs), inline=True)
    embed.add_field(name="Commands", value=len(bot.tree.get_commands()), inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Bot startup function - ADDED for proper async handling
async def main():
    async with bot:
        await bot.start(TOKEN)

# Run the bot - UPDATED for proper error handling
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except discord.LoginFailure:
        logger.error("❌ Invalid token! Check your environment variables")
    except Exception as e:
        logger.error(f"❌ Critical error: {str(e)}")
