"""
event manage command handler
"""
from typing import Literal
import discord
from discord.enums import EntityType, PrivacyLevel
from discord.ext import commands
from discord import app_commands
from datetime import timedelta


class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="create_event")
    @app_commands.describe(
        name="the name of event",
        description="the description of the event",
        start_time="the delta from now of the event (minutes)",
        duration="the duration of the event (minutes)",
        location="the location of event ( warn! use channel instead for voice and stage )",
        channel="the channel of event ( warn! use location instead for external )",
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_events=True)
    @app_commands.checks.bot_has_permissions(manage_events=True)
    async def create_event(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str,
        start_time: app_commands.Range[int, 10, 1440*3],
        duration: app_commands.Range[int, 10, 360*12],
        location: str | None = None,
        channel: discord.VoiceChannel | discord.StageChannel | None = None
    ) -> None:
        """
        create a scheduled event from this guild
        """
        if not interaction.guild:
            await interaction.response.send_message("only can use it within a server!")
            return

        if bool(channel) == bool(location):
            await interaction.response.send_message(
                f"conflict, {
                    'only need location or channel, but given both'
                    if location
                    else 'needed location or channel, but have None'
                }")
            return

        await interaction.response.defer(ephemeral=True)

        entity: dict = {
            "channel": channel,
            "entity_type": EntityType.voice
            if isinstance(channel, discord.VoiceChannel)
            else EntityType.stage_instance
        } if channel else {
            "location": location,
            "entity_type": EntityType.external
        }

        event = await interaction.guild.create_scheduled_event(
            name=name,
            description=description,
            **entity,
            start_time=discord.utils.utcnow() +
            timedelta(minutes=start_time),
            end_time=discord.utils.utcnow() + timedelta(minutes=start_time) +
            timedelta(minutes=duration),
            privacy_level=PrivacyLevel.guild_only
        )

        finally_embed = discord.Embed(
            description=f"successfully created the scheduled event: {event.url}",
            timestamp=discord.utils.utcnow(),
            color=0x0000ff
        )
        await interaction.followup.send(embed=finally_embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventsCog(bot))
