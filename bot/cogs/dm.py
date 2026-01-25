"""
dm action editing command
"""
from enum import Enum
import discord
from discord import app_commands
from discord.ext import commands

Messageable = (discord.TextChannel | discord.StageChannel
               | discord.VoiceChannel | discord.Thread)


class Action(Enum):
    to_channel = 0b001
    to_user = 0b010
    disable_all = 0b100


class DMEditCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="dm_action")
    @app_commands.describe(
        action="the action when dm",
        user="the user of action ( default requester )",
        channel="the channel of action ( default this channel )"
    )
    async def dm_action(
            self,
            interaction: discord.Interaction,
            action: Action,
            user: discord.User | discord.Member | None = None,
            channel: Messageable | None = None
    ) -> None:
        if not interaction.guild:
            errembed = discord.Embed(
                title="error",
                description="cannot use it in server!",
                color=0x0000ff,
                timestamp=discord.utils.utcnow()
            )

            await interaction.response.send_message(embed=errembed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        if not channel:
            if not isinstance(interaction.channel, Messageable):
                errembed = discord.Embed(
                    title="error",
                    description="no channel provided and this channel not messageable",
                    color=0x0000ff
                )
                await interaction.followup.send(embed=errembed, ephemeral=True)
                return

            channel = interaction.channel

        if not user:
            user = interaction.user

        bot_user: discord.Member = interaction.guild.me
        bot_perm: discord.Permissions = channel.permissions_for(bot_user)

        if not bot_perm.send_messages:
            ...

        ...


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DMEditCog(bot))
