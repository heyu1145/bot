import discord
from discord.ext import tasks
import asyncio
from config.config import RATE_LIMIT_CONFIG
from utils.data_storage import load_items, load_dynamic_messages


def create_refresh_task(bot):
    """
    创建自动刷新任务，用于刷新动态消息
    
    Args:
        bot: Discord机器人实例
    
    Returns:
        Refresh task object
    """
    @tasks.loop(minutes=1)
    async def refresh_dynamic_messages():
        """刷新所有动态消息的主任务"""
        print("🔄 Refreshing dynamic messages...")
        
        all_data = load_dynamic_messages() or {}
        tasks_to_execute = []
        
        for guild_id_str, channels in all_data.items():
            guild = bot.get_guild(int(guild_id_str))
            if not guild:
                print(f"⚠️ Guild {guild_id_str} not found, skipping...")
                continue

            for channel_id_str, message_ids in channels.items():
                channel = guild.get_channel(int(channel_id_str))
                if not channel:
                    print(f"⚠️ Channel {channel_id_str} not found in guild {guild_id_str}, skipping...")
                    continue

            for message_id in message_ids:
                task = refresh_single_message(bot, guild_id_str, channel, int(message_id))
                tasks_to_execute.append(task)
        
        # 批量执行刷新操作并应用速率限制
        for i in range(0, len(tasks_to_execute), RATE_LIMIT_CONFIG['BATCH_SIZE']):
            batch = tasks_to_execute[i:i+RATE_LIMIT_CONFIG['BATCH_SIZE']]
            results = await asyncio.gather(*batch, return_exceptions=True)
            
            # 检查异常结果
            for result in results:
                if isinstance(result, Exception):
                    print(f"❌ Task failed with error: {result}")
            
            await asyncio.sleep(RATE_LIMIT_CONFIG['BATCH_DELAY'])

    async def refresh_single_message(bot, guild_id: str, channel: discord.TextChannel, message_id: int):
        """
        刷新单个消息
        
        Args:
            bot: Discord机器人实例
            guild_id: 服务器ID
            channel: 频道对象
            message_id: 消息ID
        """
        try:
            message = await channel.fetch_message(message_id)
            if message.embeds:
                old_embed = message.embeds[0]
                
                # 获取当前数据用于更新嵌入
                current_data = load_items(guild_id)
                
                # 更新嵌入内容
                new_embed = discord.Embed(
                    title=old_embed.title or "📊 Dynamic Message",
                    description=format_data_for_embed(current_data),
                    color=old_embed.color or discord.Color.blue()
                )
                new_embed.timestamp = discord.utils.utcnow()
                new_embed.set_footer(text="Last updated", icon_url=bot.user.display_avatar.url if bot.user else None)
                
                await message.edit(embed=new_embed)
                print(f"✅ Refreshed message {message_id}")
                
        except discord.NotFound:
            print(f"❌ Message {message_id} not found, removing from refresh list...")
            # 这里可以添加从动态消息列表中移除不存在的消息的逻辑
        except Exception as e:
            print(f"❌ Failed to refresh message {message_id}: {e}")

    def format_data_for_embed(data) -> str:
        """
        将数据格式化为嵌入描述
        
        Args:
            data: 要格式化的数据
        
        Returns:
            str: 格式化后的字符串
        """
        if not data:
            return "No data available"
        
        if isinstance(data, list):
            formatted_items = []
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    item_str = ", ".join([f"**{k}**: {v}" for k, v in item.items()])
                    formatted_items.append(f"`{i+1}`. {item_str}")
                else:
                    formatted_items.append(f"`{i+1}`. {str(item)}")
            return "\n".join(formatted_items)
        else:
            return str(data)

    return refresh_dynamic_messages


def create_custom_refresh_task(bot, refresh_interval_minutes: int = 5, data_fetcher = None):
    """
    创建自定义刷新任务
    
    Args:
        bot: Discord机器人实例
        refresh_interval_minutes: 刷新间隔（分钟）
        data_fetcher: 自定义数据获取函数
    
    Returns:
        Custom refresh task object
    """
    @tasks.loop(minutes=refresh_interval_minutes)
    async def custom_refresh_task():
        """自定义刷新任务"""
        print(f"🔄 Running custom refresh task (interval: {refresh_interval_minutes} min)...")
        
        all_data = load_dynamic_messages() or {}
        tasks_to_execute = []
        
        for guild_id_str, channels in all_data.items():
            guild = bot.get_guild(int(guild_id_str))
            if not guild:
                continue

            for channel_id_str, message_ids in channels.items():
                channel = guild.get_channel(int(channel_id_str))
                if not channel:
                    continue

            for message_id in message_ids:
                task = refresh_single_message_custom(bot, guild_id_str, channel, int(message_id), data_fetcher)
                tasks_to_execute.append(task)
        
        # 执行任务并应用速率限制
        for i in range(0, len(tasks_to_execute), RATE_LIMIT_CONFIG['BATCH_SIZE']):
            batch = tasks_to_execute[i:i+RATE_LIMIT_CONFIG['BATCH_SIZE']]
            await asyncio.gather(*batch, return_exceptions=True)
            await asyncio.sleep(RATE_LIMIT_CONFIG['BATCH_DELAY'])

    async def refresh_single_message_custom(bot, guild_id: str, channel: discord.TextChannel, message_id: int, data_fetcher):
        """刷新单个消息（自定义版本）"""
        try:
            message = await channel.fetch_message(message_id)
            if message.embeds:
                old_embed = message.embeds[0]
                
                # 使用自定义数据获取器或默认获取器
                if data_fetcher and callable(data_fetcher):
                    current_data = data_fetcher(guild_id)
                else:
                    current_data = load_items(guild_id)
                
                new_embed = discord.Embed(
                    title=old_embed.title or "📊 Dynamic Message",
                    description=format_data_for_embed(current_data),
                    color=old_embed.color or discord.Color.blue()
                )
                new_embed.timestamp = discord.utils.utcnow()
                new_embed.set_footer(text=f"Updated every {refresh_interval_minutes} min", 
                                   icon_url=bot.user.display_avatar.url if bot.user else None)
                
                await message.edit(embed=new_embed)
                print(f"✅ Custom refreshed message {message_id}")
                
        except Exception as e:
            print(f"❌ Failed to custom refresh message {message_id}: {e}")

    def format_data_for_embed(data) -> str:
        """格式化数据用于嵌入"""
        if not data:
            return "No data available"
        
        if isinstance(data, list):
            formatted_items = []
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    item_str = ", ".join([f"**{k}**: {v}" for k, v in item.items()])
                    formatted_items.append(f"`{i+1}`. {item_str}")
                else:
                    formatted_items.append(f"`{i+1}`. {str(item)}")
            return "\n".join(formatted_items)
        else:
            return str(data)

    return custom_refresh_task