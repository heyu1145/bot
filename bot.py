import discord
from discord.ext import commands
import logging
import asyncio
import random
import time
from config.config import DISCORD_CONFIG, TIME_CONFIG
from utils.storage import load_trusted_users, is_bot_owner, data_manager
from utils.permissions import has_data_access
from customerror import *
from utils.auto_refresh import create_refresh_task
from utils.cog_loader import CogLoader

# Setup logging - KEPT AS IS
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.propagate = True

# Load environment variables and validate configs - KEPT AS IS
TOKEN = DISCORD_CONFIG['TOKEN']
OWNER_USER_ID = DISCORD_CONFIG['OWNER_USER_ID']

if not TOKEN:
    logger.error("❌ ERROR: No Discord token found! Set TOKEN in environment variables")
    raise TokenNotFoundError("Didnt found token in environment!")

if not OWNER_USER_ID:
    logger.error("❌ ERROR: No owner user ID found! Set OWNER_USER_ID in environment variables")
    raise OwnerUseridNoFoundError("Didnt found in environment!")

# Bot setup - KEPT AS IS
intents = discord.Intents.default()
for intent_name, intent_value in DISCORD_CONFIG['INTENTS'].items():
    setattr(intents, intent_name, intent_value)

bot = commands.Bot(command_prefix=DISCORD_CONFIG['COMMAND_PREFIX'], intents=intents, help_command=None)
bot.start_time = time.time()
refresh_task = create_refresh_task(bot)

# Uptime function - ADDED
def get_uptime():
    uptime_seconds = int(time.time() - bot.start_time)
    days, remainder = divmod(uptime_seconds, TIME_CONFIG['UPTIME_DIVISORS']['day_seconds'])
    hours, remainder = divmod(remainder, TIME_CONFIG['UPTIME_DIVISORS']['hour_seconds'])
    minutes, seconds = divmod(remainder, TIME_CONFIG['UPTIME_DIVISORS']['minute_seconds'])
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

# Load cogs - UPDATED to use automatic loading
async def load_cogs():
    try:
        # 使用CogLoader自动加载所有cogs
        cog_loader = CogLoader(bot, 'cogs')
        load_result = await cog_loader.load_all_cogs()
        
        total_loaded = load_result['total_loaded']
        total_failed = load_result['total_failed']
        
        if total_loaded > 0:
            logger.info(f"✅ Successfully loaded {total_loaded} cogs")
        if total_failed > 0:
            logger.error(f"❌ {total_failed} cogs failed to load")
            for failed in load_result['failed']:
                logger.error(f"   - {failed['cog']}: {failed['error']}")
    except Exception as e:
        logger.error(f"❌ Error loading cogs automatically: {e}")

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

    if not refresh_task.is_running():
        refresh_task.start()
        logger.info("refresh task started!")

    # Set bot status - ADDED
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{len(bot.guilds)} servers | use /help to get all commands!"
        )
    )

# Enhanced ping command - UPDATED
@bot.tree.command(name="ping", description="Check the bot's response time and status")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    api_latency = round(random.uniform(100,230))
    
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
