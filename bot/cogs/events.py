"""
event manage command handler
"""

from datetime import timedelta
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View
from modals.events_modal import DeleteEventSelect, ViewEventSelect


class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    event_group = app_commands.Group(
        name="event", description="server scheduled event handler", guild_only=True
    )

    @event_group.command(name="view")
    async def channel_view(self, interaction: discord.Interaction) -> None:
        """
        view events' information
        """
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            raise app_commands.CheckFailure("this command can only used in server")

        if len(interaction.guild.scheduled_events) == 0:
            errembed = discord.Embed(
                title="Info",
                description="This server do not have any scheduled event",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow(),
            )
            await interaction.followup.send(embed=errembed, ephemeral=True)
            return

        select = ViewEventSelect(
            [event for event in interaction.guild.scheduled_events]
        )

        view = View()
        view.add_item(select)

        embed = discord.Embed(
            description="select events to show their details",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @event_group.command(name="delete")
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def event_delete(self, interaction: discord.Interaction) -> None:
        """
        delete selected event
        """
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            raise app_commands.CheckFailure("this command can only use in server")

        if len(interaction.guild.scheduled_events) == 0:
            errembed = discord.Embed(
                title="Warning",
                description="This server do not.have any scheduled event",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow(),
            )
            await interaction.followup.send(embed=errembed, ephemeral=True)
            return

        select = DeleteEventSelect(
            [event for event in interaction.guild.scheduled_events]
        )

        view = View()
        view.add_item(select)

        embed = discord.Embed(
            description="select events to delete",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    event_create_group = app_commands.Group(
        name="create",
        description="create a event by command",
        parent=event_group,
        default_permissions=discord.Permissions(manage_events=True),
    )

    @event_create_group.command(name="inplace")
    @app_commands.describe(
        channel="the channel the event at",
        name="the name of the event",
        description="the description of the event",
        start_delta="the time delta from now ( use minutes )",
        duration="the duration of the event ( use minutes )",
    )
    @app_commands.checks.bot_has_permissions(manage_events=True)
    async def channel_create_inplace(
        self,
        interaction: discord.Interaction,
        channel: discord.VoiceChannel | discord.StageChannel,
        name: str,
        description: str,
        start_delta: app_commands.Range[int, 10, 60 * 24 * 7],
        duration: app_commands.Range[int, 10, 60 * 12],
    ) -> None:
        """
        create the event that place is in this server
        """
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            raise app_commands.CheckFailure("this command can only used in server")

        if not interaction.guild.me.guild_permissions.manage_events:
            raise app_commands.BotMissingPermissions(["mamage_events"])

        start = discord.utils.utcnow() + timedelta(minutes=start_delta)
        end = start + timedelta(minutes=duration)
        event = await interaction.guild.create_scheduled_event(
            name=name,
            description=description,
            channel=channel,
            entity_type=discord.EntityType.voice
            if isinstance(channel, discord.VoiceChannel)
            else discord.EntityType.stage_instance,
            privacy_level=discord.PrivacyLevel.guild_only,
            start_time=start,
            end_time=end,
            reason=f"{interaction.user.name} called",
        )

        embed = discord.Embed(
            title="success",
            description=f"the event had created, jump_url at [here]({event.url})",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @event_create_group.command(name="external")
    @app_commands.describe(
        name="the name of the event",
        description="the description of the event",
        location="the location of the event",
        start_delta="the start delta from now ( use minutes )",
        duration="the duration of the event ( use minutes )",
    )
    @app_commands.checks.bot_has_permissions(manage_events=True)
    async def event_create_external(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str,
        location: str,
        start_delta: app_commands.Range[int, 10, 60 * 24 * 7],
        duration: app_commands.Range[int, 10, 60 * 12],
    ) -> None:
        """
        create event at external place
        """
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            raise app_commands.CheckFailure("This command can only use in server")

        if not interaction.guild.me.guild_permissions.manage_events:
            raise app_commands.BotMissingPermissions(["manage_events"])

        start = discord.utils.utcnow() + timedelta(minutes=start_delta)
        end = start + timedelta(minutes=duration)

        event = await interaction.guild.create_scheduled_event(
            name=name,
            description=description,
            location=location,
            entity_type=discord.EntityType.external,
            privacy_level=discord.PrivacyLevel.guild_only,
            start_time=start,
            end_time=end,
            reason=f"{interaction.user.name} called",
        )

        embed = discord.Embed(
            title="success",
            description=f"the event had created, jump url at [here]({event.url})",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventsCog(bot))
