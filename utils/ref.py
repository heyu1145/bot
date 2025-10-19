import discord
from discord.ext import tasks
import asyncio
from utils.test import load, load_msg

def create_refresh_task(bot):
    @tasks.loop(minutes=1)
    async def refresh_embeds():
        print("🔄 Refreshing embeds...")
        
        all_data = load_msg() or {}
        tasks = []
        
        for guild_id_str, channels in all_data.items():
            guild = bot.get_guild(int(guild_id_str))
            if not guild:
                continue

            for channel_id_str, message_ids in channels.items():
                channel = guild.get_channel(int(channel_id_str))
                if not channel:
                    continue

                for message_id in message_ids:
                    task = refresh_single_embed(bot, guild_id_str, channel, message_id)
                    tasks.append(task)
        
        # Run all refresh operations concurrently with rate limiting
        for i in range(0, len(tasks), 5):  # 5 at a time
            batch = tasks[i:i+5]
            await asyncio.gather(*batch, return_exceptions=True)
            await asyncio.sleep(1)  # Rate limit between batches

    async def refresh_single_embed(bot, guild_id, channel, message_id):
        try:
            message = await channel.fetch_message(int(message_id))
            if message.embeds:
                old_embed = message.embeds[0]
                current_data = load(guild_id)
                
                new_embed = discord.Embed(
                    title=old_embed.title or "Remote",
                    description=str(current_data),
                    color=old_embed.color or discord.Color.blue()
                )
                new_embed.timestamp = discord.utils.utcnow()
                
                await message.edit(embed=new_embed)
                print(f"✅ Refreshed message {message_id}")
                
        except Exception as e:
            print(f"❌ Failed to refresh {message_id}: {e}")

    return refresh_embeds
