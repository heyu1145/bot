"""
channel manager of the bot
"""
import discord
from discord import app_commands
from discord.ext import commands
from discord.abc import GuildChannel

class ChannelCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="channel_info")
    @app_commands.describe(
            channel="the channel you want to view"
            )
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(view_channel=True)
    async def view_channel(
            self,
            interaction: discord.Interaction,
            channel: GuildChannel | None = None
            ) -> None:
        """
        shows the info of the channel(default this channel)
        """
        if not channel:
            if not isinstance(interaction.channel, GuildChannel):
                errembed = discord.Embed(
                        description="Cannot use it in dm!",
                        color=0xff0000,
                        timestamp=discord.utils.utcnow()
                    )
                await interaction.response.send_message(embed=errembed, ephemeral=True)
                return
            
            channel = interaction.channel

        bot_member = channel.guild.me
        bot_perm = channel.permissions_for(bot_member)

        if not bot_perm.view_channel:
            errembed = discord.Embed(
                    description="I have no enough Permission for the channel {channel.jump_url}",
                    color=0xff0000,
                    timestamp=discord.utils.utcnow()
                    )
            await interaction.response.send_message(embed=errembed)
            return

        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
                title=f"the info of {channel.jump_url}",
                color=0xff8800,
                timestamp=discord.utils.utcnow()
            )

        embed.set_footer(text=f"Request by {interaction.user.name}")

        match channel:
            case discord.TextChannel(nsfw=nsfw, 
                                     slowmode_delay=slowmode, 
                                     topic=topic):
                embed.add_field(
                        name="is nsfw (not safe for work)",
                        value=nsfw,
                        inline=True
                        )

                embed.add_field(
                        name="slowmode delay",
                        value=slowmode,
                        inline=True
                        )

                embed.add_field(
                        name='topic',
                        value=topic,
                        inline=True
                         )

            case discord.VoiceChannel(
                    nsfw=nsfw, 
                    bitrate=bitrate, 
                    user_limit=limit, 
                    slowmode_delay=slowmode):

                embed.add_field(
                        name="is nsfw (not safe for work)",
                        value=nsfw,
                        inline=True
                        )
                
                embed.add_field(
                        name='slowmode delay',
                        value=slowmode,
                        inline=True
                        )

                embed.add_field(
                        name='voice bitrate',
                        value=bitrate,
                        inline=True
                        )

                embed.add_field(
                        name='user count',
                        value=f"count: {len(channel.members)}, limit: {limit}'m",
                        inline=True
                        )

            case discord.CategoryChannel(nsfw=nsfw):
                embed.add_field(
                        name="is nsfw (not safe for work)",
                        value=nsfw,
                        inline=True
                        )

            case discord.StageChannel(
                    nsfw=nsfw,
                    bitrate=bitrate, 
                    topic=topic, 
                    slowmode_delay=slowmode,
                    user_limit=limit):

                embed.add_field(
                        name="is nsfw (not safe for work)",
                        value=nsfw,
                        inline=True
                        )

                embed.add_field(
                        name='slowmode delay',
                        value=slowmode,
                        inline=True
                        )

                embed.add_field(
                        name='topic',
                        value=topic,
                        inline=True
                        )

                embed.add_field(
                        name='bitrate',
                        value=bitrate,
                        inline=True
                        )

                embed.add_field(
                        name='user',
                        value=f"count: {len(channel.members)}, limit: {limit},",
                        inline=True
                        )

            case discord.ForumChannel(topic=topic):
                embed.add_field(
                        name='topic',
                        value=topic,
                        inline=True
                        )

        await interaction.followup.send(embed=embed,ephemeral=True)

            

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChannelCog(bot))
