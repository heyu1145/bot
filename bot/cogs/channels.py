"""
channels helper
"""
import discord
from discord import app_commands
from discord.ext import commands
from utils.utils import multi_set_fields


class ChannelsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    channels_group = app_commands.Group(
        name="channels",
        description="channels options",
        guild_only=True
    )

    @channels_group.command(name="view")
    @app_commands.describe(channel="the channel to view")
    async def channel_view(
            self,
            interaction: discord.Interaction,
            channel: discord.abc.GuildChannel
    ) -> None:
        """
        view the channel's status
        """
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            raise app_commands.CheckFailure(
                "Thid command can only used in server")

        if not channel.permissions_for(channel.guild.me).view_channel:
            raise app_commands.BotMissingPermissions(["view_channel"])

        basic_embed = discord.Embed(
            title=f"{channel.name}'s info",
            color=0xff,
            timestamp=discord.utils.utcnow()
        )

        multi_set_fields(
            basic_embed,
            channel_type=channel.type.name,
            created_at=discord.utils.format_dt(channel.created_at, "F"),
            from_now=discord.utils.format_dt(channel.created_at, "R")
        )
        match channel:
            case discord.TextChannel(
                    nsfw=nsfw,
                    members=members,
                    slowmode_delay=slowmode_delay
            ):
                multi_set_fields(
                    basic_embed,
                    is_nsfw=nsfw,
                    members=len(members),
                    slowmode=f"{slowmode_delay} sec",
                )
            case discord.VoiceChannel(
                nsfw=nsfw,
                members=members,
                bitrate=bitrate
            ):
                multi_set_fields(
                    basic_embed,
                    is_nsfw=nsfw,
                    members=len(members),
                    bitrate=bitrate,
                )

        await interaction.followup.send(embed=basic_embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChannelsCog(bot))
