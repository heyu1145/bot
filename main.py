import discord
from discord.ext import commands
import os
import logging
from utils.storage import load_trusted_users, is_bot_owner
from utils.permissions import has_data_access
from keep_alive import keep_alive

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

logger.propagate = False

logger.info("Starting keep_alive server...")
keep_alive_success = keep_alive()

if not keep_alive_success:
logger.warning("keep_alive server failed to start, but the bot running, the bot will offline after idle 5 minutes!")

# Load environment variables
TOKEN = os.getenv('TOKEN')
OWNER_USER_ID = os.getenv('OWNER_USER_ID')

if not TOKEN:
    logger.error("❌ ERROR: No Discord token found! Set TOKEN in environment variables")
    exit(1)

if not OWNER_USER_ID:
    logger.error("❌ ERROR: No owner user ID found! Set OWNER_USER_ID in environment variables")
    exit(1)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_scheduled_events = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load cogs
async def load_cogs():
    try:
        await bot.load_extension('cogs.tickets')
        await bot.load_extension('cogs.events')
        await bot.load_extension('cogs.data_management')
        await bot.load_extension('cogs.admin')
        logger.info("✅ All cogs loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load cogs: {e}")

@bot.event
async def on_ready():
    bot.start_time = discord.utils.utcnow()
    logger.info(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'🔗 Connected to {len(bot.guilds)} server(s)')
    
    await load_cogs()
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"❌ Command sync failed: {e}")

# Basic commands
@bot.tree.command(name="ping", description="Check the bot's response time")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Response time: {latency}ms", ephemeral=True)

@bot.tree.command(name="bot_info", description="Get basic bot information")
async def bot_info(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Bot Information", color=discord.Color.blue())
    embed.add_field(name="Name", value=bot.user.name, inline=True)
    embed.add_field(name="ID", value=bot.user.id, inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("❌ Invalid token! Check your environment variables")
    except Exception as e:
        logger.error(f"❌ Critical error: {str(e)}")