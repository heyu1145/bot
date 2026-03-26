import discord
from discord import app_commands
from discord.ext import commands
from utils.data_storage import save_item, load_items, remove_item, save_dynamic_message
from utils.storage import data_manager


class DynamicMessagesCog(commands.Cog, name="dynamic_messages"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_dynamic_msg", description="Create a dynamic message that auto-refreshes")
    @app_commands.describe(channel="Channel where to create the dynamic message")
    async def create_dynamic_msg(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """创建一个动态消息，该消息会自动刷新"""
        embed = discord.Embed(
            title="📊 Server Status",
            description="Real-time data will be displayed here",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="This message auto-refreshes")
        
        message = await channel.send(embed=embed)
        save_dynamic_message(str(interaction.guild.id), channel.id, message.id)
        await interaction.response.send_message(f"✅ Dynamic message created: {message.jump_url}", ephemeral=True)

    @app_commands.command(name="add_refresh_item", description="Add data that will be used to refresh dynamic messages")
    @app_commands.describe(data="Data to be added for refreshing (will replace {} in dynamic messages)")
    async def add_refresh_item(self, interaction: discord.Interaction, data: str):
        """添加用于刷新动态消息的数据"""
        save_item(str(interaction.guild.id), data)
        await interaction.response.send_message("✅ Data added for dynamic refresh", ephemeral=True)

    @app_commands.command(name="remove_refresh_item", description="Remove data from the refresh list")
    @app_commands.describe(data="Data to be removed from the refresh list")
    async def remove_refresh_item(self, interaction: discord.Interaction, data: str):
        """从刷新列表中移除数据"""
        if not remove_item(str(interaction.guild.id), data):
            await interaction.response.send_message("❌ Data not found in refresh list!", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Data removed from refresh list", ephemeral=True)

    @app_commands.command(name="list_refresh_items", description="List all data items for dynamic refresh")
    async def list_refresh_items(self, interaction: discord.Interaction):
        """列出所有用于动态刷新的数据项"""
        data = load_items(str(interaction.guild.id))
        if data:
            description = "\n".join([f"• {str(item)}" for item in data])
        else:
            description = "• No items in refresh list"
        
        embed = discord.Embed(
            title="🔄 Dynamic Refresh Items",
            description=description,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(DynamicMessagesCog(bot))