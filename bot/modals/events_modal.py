"""
file stores event modal
"""

import discord
from discord.ui import Select


class BaseEventSelect(Select):
    def __init__(self, events: list[discord.ScheduledEvent]) -> None:
        self.events = events
        super().__init__(
            placeholder="please select a event...",
            min_values=1,
            max_values=max(len(events), 1),
            options=[
                discord.SelectOption(
                    label=event.name, value=str(i), description=event.description
                )
                for i, event in enumerate(events)
            ],
        )


class DeleteEventSelect(BaseEventSelect):
    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        selected = [int(v) for v in self.values]
        self.disabled = True
        for index in selected:
            event = self.events[index]
            await event.cancel(reason=f"request by user {interaction.user.name}")
            embed = discord.Embed(
                description=f"event '{event.name}' cancelled",
                color=discord.Color.blue(), timestamp=discord.utils.utcnow()
            )
            embed.set_footer(text=f"request by {interaction.user.name}")
            await interaction.followup.send(embed=embed, ephemeral=True)


event_view_embed = discord.Embed(
    color=discord.Color.blue(), timestamp=discord.utils.utcnow()
)


class ViewEventSelect(BaseEventSelect):
    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        selected = [int(v) for v in self.values]
        self.disabled = True
        for index in selected:
            event = self.events[index]
            embed = event_view_embed.copy()
            embed.title = f"{event.name}'s info"
            embed.description = f"event description: {event.description}"
            embed.add_field(
                name="event type:", value=event.entity_type.name, inline=False
            )
            embed.add_field(
                name="event duration:",
                value=(
                    discord.utils.format_dt(event.start_time)
                    + "~"
                    + discord.utils.format_dt(event.end_time)
                    if event.end_time
                    else "Unknown Endtime"
                ),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
