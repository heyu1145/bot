import discord
from discord import app_commands
from discord.ext import commands
from utils.test import save,load,remove,save_msg

class testCog(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    
  @app_commands.command(name="test",description="test refresh message")
  @app_commands.describe(channel="where to test")
  async def test(self, interaction: discord.Interaction, channel:discord.TextChannel):
    embed = discord.Embed(
      title="remote",
      description="{}",
      color=discord.Color.blue(),
      footer=f"refresh time: {discord.utils.utcnow()}"
    )
    message = await channel.send(embed=embed)
    save_msg(str(interaction.guild.id),message.channel.id,message.id)
    await interaction.response.send_message("successful",ephemeral=True)
  
  @app_commands.command(name="add",description="add thing you want to refresh")
  @app_commands.describe(message="message")
  async def add(self, interaction:discord.Interaction, message:str):
    save(str(interaction.guild.id),message)
    await interaction.response.send_message("added",ephemeral=True)
  
  @app_commands.command(name="delete",description="delete thing you dont want to refresh")
  @app_commands.describe(message="message you want to delete")
  async def delete(self, interaction:discord.Interaction, message:str):
    if not remove(str(interaction.guild.id),message):
      await interaction.response.send_message("didnt found!",ephemeral=True)
    else:
      await interaction.response.send_message("delete successful",ephemeral=True)
      
  @app_commands.command(name="list",description="list all thing")
  async def list(self,interaction:discord.Interaction):
    data = load(str(interaction.guild.id))
    if data != []:
      description = ""
      for thing in data:
        description += f"* {thing}\n"
    else:
      description = "* No items"
    embed = discord.Embed(
      title="all thing in refresh list:",
      description=description,
      color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed,ephemeral=True) 

async def setup(bot):
  await bot.add_cog(testCog(bot))
