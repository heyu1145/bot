"""
extra cogs for embed helper
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.hex_helper import hex_to_int


class EmbedsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @app_commands.command(name="send_embed", description="a command to send a embed")
    @app_commands.describe(
        channel="the channel the embed to send to",
        message="the message of the embed",
        title="the title of the embed",
        color="the color of the embed (use hex)",
        author="the author of the embed",
        footer="the footer of the embed",
        image="the image of the embed"
    )
    @app_commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def send_embed(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            message: str,
            title: str | None = None,
            color: str = "#0000FF",
            author: str | None = None,
            footer: str | None = None,
            image: discord.Attachment | None = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        embed: discord.Embed = discord.Embed(
            title=title,
            description=message,
            color=hex_to_int(color)
        )
        embed.set_author(name=author if author else '')
        embed.set_footer(text=footer)
        if image and image.content_type and image.content_type.startswith("image/"):
            embed.set_image(url=image.url)

        msg: discord.Message = await channel.send(embed=embed)

        finally_embed = discord.Embed(
            description=f"the embed had already send to channel {channel.jump_url}, message: {msg.jump_url}",
            timestamp=discord.utils.utcnow(),
            color=0x0000ff
        )
        await interaction.followup.send(embed=finally_embed, ephemeral=True)

    @app_commands.command(name="send_embed_extra", description="a command to send a embed with extra method")
    @app_commands.describe(
        channel="the channel the embed to send to",
        message="the message of the embed",
        title="the title of the embed",
        color="the color of the embed (use hex)",
        author="the author of the embed",
        footer="the footer of the embed",
        image="the image of the embed",
        footer_image="the footer's image of embed",
        thumbnail="the thumbnail of embed"
    )
    @app_commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def send_embed_extra(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel,
            message: str,
            title: str | None = None,
            color: str = "#0000FF",
            author: str | None = None,
            footer: str | None = None,
            image: discord.Attachment | None = None,
            footer_image: discord.Attachment | None = None,
            thumbnail: discord.Attachment | None = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        embed: discord.Embed = discord.Embed(
            title=title,
            description=message,
            color=hex_to_int(color)
        )
        embed.set_author(name=author if author else '')
        embed.set_footer(
            text=footer,
            icon_url=footer_image.url
            if footer_image
            and footer_image.content_type
            and footer_image.content_type.startswith("image/")
            else None
        )
        if image and image.content_type and image.content_type.startswith("image/"):
            embed.set_image(url=image.url)

        if thumbnail and thumbnail.content_type and thumbnail.content_type.startswith("image/"):
            embed.set_thumbnail(url=thumbnail.url)

        msg: discord.Message = await channel.send(embed=embed)

        finally_embed = discord.Embed(
            description=f"the embed had already send to channel {channel.jump_url}, message: {msg.jump_url}",
            timestamp=discord.utils.utcnow(),
            color=0x0000ff
        )
        await interaction.followup.send(embed=finally_embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EmbedsCog(bot))
