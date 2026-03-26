import discord
from discord import app_commands
from discord.ext import commands
import pytz
from datetime import datetime, timedelta, timezone
import re
from typing import Optional
import logging

from config.config import MESSAGE_CONFIG
from utils.storage import load_user_timezones, save_user_timezone, data_manager
from utils.permissions import has_event_access

logger = logging.getLogger('discord')

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_time_input(self, time_str: str, user_timezone: pytz.FixedOffset) -> Optional[datetime]:
        """Parse various time formats and return localized datetime"""
        now = datetime.now(user_timezone)
        
        # Try YYYY-MM-DD HH:MM format
        try:
            return user_timezone.localize(datetime.strptime(time_str, "%Y-%m-%d %H:%M"))
        except ValueError:
            pass
        
        # Try MM-DD HH:MM format (assume current year)
        try:
            time_with_year = f"{now.year}-{time_str}"
            return user_timezone.localize(datetime.strptime(time_with_year, "%Y-%m-%d %H:%M"))
        except ValueError:
            pass
        
        # Try HH:MM format (assume today or tomorrow if time has passed)
        try:
            time_only = datetime.strptime(time_str, "%H:%M").time()
            candidate = user_timezone.localize(datetime.combine(now.date(), time_only))
            
            # If time has passed today, assume tomorrow
            if candidate <= now:
                candidate = user_timezone.localize(datetime.combine(now.date() + timedelta(days=1), time_only))
            
            return candidate
        except ValueError:
            pass
        
        return None

    @app_commands.command(name="set_timezone", description="Set your timezone for event creation")
    @app_commands.describe(timezone="Your timezone in UTC±X format (e.g., UTC+3)")
    async def set_timezone(self, interaction: discord.Interaction, timezone: str):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

        if not re.match(r'^UTC[+-]\d{1,2}$', timezone):
            return await interaction.response.send_message(
                "❌ Use format: UTC±X (e.g., UTC+2, UTC-7)", ephemeral=True)

        try:
            offset = int(timezone[3:])
            if not (-12 <= offset <= 14):
                raise ValueError
        except ValueError:
            return await interaction.response.send_message(
                "❌ Offset must be between -12 and 14", ephemeral=True)

        save_user_timezone(str(interaction.guild.id), interaction.user.id, timezone)
        await interaction.response.send_message(
            f"✅ Timezone set to {timezone} for this server", ephemeral=True)

    @app_commands.command(name="create_event", description="Create a scheduled event")
    @app_commands.describe(
        name="Event name",
        description="Event description",
        time="Event time (YYYY-MM-DD HH:MM, MM-DD HH:MM, or HH:MM)",
        location="Event location or voice channel",
        duration_minutes="Duration in minutes (default: 90)"
    )
    async def create_event(self, interaction: discord.Interaction, name: str, description: str, 
                          time: str, location: str, duration_minutes: int = 90):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

        if not has_event_access(interaction):
            return await interaction.response.send_message(
                "❌ Only staff, administrators, or owners can create events!", ephemeral=True)

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_timezones = load_user_timezones(guild_id)

        if user_id not in user_timezones:
            return await interaction.response.send_message(
                "❌ Set your timezone first with `/set_timezone UTC±X`", ephemeral=True)

        try:
            timezone_str = user_timezones[user_id]
            offset = int(timezone_str[3:])
            user_timezone = pytz.FixedOffset(offset * 60)

            # Parse the time input
            local_start = self.parse_time_input(time, user_timezone)
            if not local_start:
                return await interaction.response.send_message(
                    "❌ Invalid time format! Use:\n"
                    "• YYYY-MM-DD HH:MM (2024-12-25 14:30)\n"
                    "• MM-DD HH:MM (12-25 14:30)\n" 
                    "• HH:MM (14:30)",
                    ephemeral=True
                )

            # Validate time
            now_local = datetime.now(user_timezone)
            if local_start < now_local:
                return await interaction.response.send_message(
                    "❌ Can't create past events", ephemeral=True)
            if local_start < now_local + timedelta(minutes=30):
                return await interaction.response.send_message(
                    "❌ Events need 30+ minutes lead time", ephemeral=True)

            # Calculate end time
            local_end = local_start + timedelta(minutes=duration_minutes)
            utc_start = local_start.astimezone(pytz.UTC)
            utc_end = local_end.astimezone(pytz.UTC)

            # Check if location is a voice channel mention
            voice_channel = None
            if location.startswith('<#') and location.endswith('>'):
                try:
                    channel_id = int(location[2:-1])
                    voice_channel = interaction.guild.get_channel(channel_id)
                    if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
                        location = voice_channel.name
                except:
                    pass

            # Create event
            event = await interaction.guild.create_scheduled_event(
                name=name[:MESSAGE_CONFIG['MAX_TITLE_LENGTH']],
                description=description[:MESSAGE_CONFIG['MAX_DESCRIPTION_LENGTH']],
                start_time=utc_start,
                end_time=utc_end,
                location=location[:MESSAGE_CONFIG['MAX_TITLE_LENGTH']],
                privacy_level=discord.PrivacyLevel.guild_only,
                entity_type=discord.EntityType.voice if voice_channel else discord.EntityType.external
            )

            embed = discord.Embed(
                title="✅ Event Created",
                description=f"**{name}** has been scheduled successfully!",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Start Time", value=local_start.strftime('%Y-%m-%d %H:%M (%Z)'), inline=True)
            embed.add_field(name="Duration", value=f"{duration_minutes} minutes", inline=True)
            embed.add_field(name="Location", value=location, inline=False)
            embed.add_field(name="Event ID", value=f"`{event.id}`", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error creating event: {e}")
            await interaction.response.send_message(f"❌ Error creating event: {str(e)}", ephemeral=True)

    @app_commands.command(name="change_event_time", description="Change the time of an existing event")
    @app_commands.describe(
        event_id="The ID of the event to modify",
        new_time="New event time (YYYY-MM-DD HH:MM, MM-DD HH:MM, or HH:MM)"
    )
    async def change_event_time(self, interaction: discord.Interaction, event_id: str, new_time: str):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)

        if not has_event_access(interaction):
            return await interaction.response.send_message("❌ Permission denied!", ephemeral=True)

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_timezones = load_user_timezones(guild_id)

        if user_id not in user_timezones:
            return await interaction.response.send_message(
                "❌ Set your timezone first with `/set_timezone UTC±X`", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        try:
            event_id_int = int(event_id.strip())
        except ValueError:
            return await interaction.followup.send("❌ Invalid event ID format.", ephemeral=True)

        try:
            # Get the event
            event = await interaction.guild.fetch_scheduled_event(event_id_int)
            
            # Parse the new time
            timezone_str = user_timezones[user_id]
            offset = int(timezone_str[3:])
            user_timezone = pytz.FixedOffset(offset * 60)
            
            new_local_start = self.parse_time_input(new_time, user_timezone)
            if not new_local_start:
                return await interaction.followup.send(
                    "❌ Invalid time format! Use:\n"
                    "• YYYY-MM-DD HH:MM (2024-12-25 14:30)\n"
                    "• MM-DD HH:MM (12-25 14:30)\n" 
                    "• HH:MM (14:30)",
                    ephemeral=True
                )

            # Validate new time
            now_local = datetime.now(user_timezone)
            if new_local_start < now_local:
                return await interaction.followup.send("❌ Can't set event to past time!", ephemeral=True)
            if new_local_start < now_local + timedelta(minutes=30):
                return await interaction.followup.send("❌ Events need 30+ minutes lead time!", ephemeral=True)

            # Calculate new end time (preserve original duration)
            original_duration = event.end_time - event.start_time
            new_utc_start = new_local_start.astimezone(pytz.UTC)
            new_utc_end = new_utc_start + original_duration

            # Update the event
            await event.edit(start_time=new_utc_start, end_time=new_utc_end)
            
            embed = discord.Embed(
                title="✅ Event Time Updated",
                description=f"**{event.name}** has been rescheduled!",
                color=discord.Color.green()
            )
            
            embed.add_field(name="New Start Time", value=new_local_start.strftime('%Y-%m-%d %H:%M (%Z)'), inline=True)
            embed.add_field(name="Original Duration", value=f"{int(original_duration.total_seconds() / 60)} minutes", inline=True)
            embed.add_field(name="Event ID", value=f"`{event.id}`", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except discord.NotFound:
            await interaction.followup.send("❌ Event not found!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error changing event time: {e}")
            await interaction.followup.send(f"❌ Failed to change event time: {e}", ephemeral=True)

    @app_commands.command(name="list_events", description="List all upcoming events")
    async def list_events(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        try:
            events = await interaction.guild.fetch_scheduled_events()
            if not events:
                return await interaction.followup.send("📭 No upcoming events found", ephemeral=True)

            # Sort events by start time
            events = sorted(events, key=lambda x: x.start_time)
            
            embed = discord.Embed(title="📅 Upcoming Events", color=discord.Color.blue())
            
            for event in events[:8]:
                status_emoji = "🟢" if event.status == discord.EventStatus.scheduled else "🟡" if event.status == discord.EventStatus.active else "🔴"
                
                # Convert to user's timezone if available
                time_display = event.start_time.strftime('%b %d, %Y %H:%M UTC')
                guild_id = str(interaction.guild.id)
                user_id = str(interaction.user.id)
                user_timezones = load_user_timezones(guild_id)
                
                if user_id in user_timezones:
                    try:
                        timezone_str = user_timezones[user_id]
                        offset = int(timezone_str[3:])
                        user_timezone = pytz.FixedOffset(offset * 60)
                        local_time = event.start_time.astimezone(user_timezone)
                        time_display = f"{local_time.strftime('%b %d, %Y %H:%M')} ({timezone_str})"
                    except:
                        pass
                
                embed.add_field(
                    name=f"{status_emoji} {event.name}",
                    value=f"**When:** {time_display}\n"
                          f"**Where:** {event.location or 'TBA'}\n"
                          f"**ID:** `{event.id}`",
                    inline=False
                )
            
            if len(events) > 8:
                embed.set_footer(text=f"Showing 8 of {len(events)} events. Use /event_info for details.")
                
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error listing events: {e}")
            await interaction.followup.send(f"❌ Failed to fetch events: {e}", ephemeral=True)

    @app_commands.command(name="event_info", description="Get detailed information about an event")
    @app_commands.describe(event_id="The ID of the event")
    async def event_info(self, interaction: discord.Interaction, event_id: str):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)

        try:
            event_id_int = int(event_id.strip())
        except ValueError:
            return await interaction.response.send_message("❌ Invalid event ID format.", ephemeral=True)

        try:
            event = await interaction.guild.fetch_scheduled_event(event_id_int)
            
            embed = discord.Embed(
                title=f"📊 Event Info: {event.name}",
                color=discord.Color.gold()
            )
            
            status_map = {
                discord.EventStatus.scheduled: "🟢 Scheduled",
                discord.EventStatus.active: "🟡 Active",
                discord.EventStatus.completed: "✅ Completed",
                discord.EventStatus.canceled: "❌ Canceled"
            }
            
            # Convert times to user's timezone if available
            start_time_display = event.start_time.strftime('%Y-%m-%d %H:%M UTC')
            end_time_display = event.end_time.strftime('%Y-%m-%d %H:%M UTC')
            
            guild_id = str(interaction.guild.id)
            user_id = str(interaction.user.id)
            user_timezones = load_user_timezones(guild_id)
            
            if user_id in user_timezones:
                try:
                    timezone_str = user_timezones[user_id]
                    offset = int(timezone_str[3:])
                    user_timezone = pytz.FixedOffset(offset * 60)
                    
                    start_local = event.start_time.astimezone(user_timezone)
                    end_local = event.end_time.astimezone(user_timezone)
                    
                    start_time_display = f"{start_local.strftime('%Y-%m-%d %H:%M')} ({timezone_str})"
                    end_time_display = f"{end_local.strftime('%Y-%m-%d %H:%M')} ({timezone_str})"
                except:
                    pass
            
            embed.add_field(name="Status", value=status_map.get(event.status, "Unknown"), inline=True)
            embed.add_field(name="Start Time", value=start_time_display, inline=False)
            embed.add_field(name="End Time", value=end_time_display, inline=False)
            embed.add_field(name="Location", value=event.location or "Not specified", inline=True)
            embed.add_field(name="Subscribers", value=str(event.subscriber_count), inline=True)
            
            if event.creator:
                embed.add_field(name="Creator", value=event.creator.mention, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.NotFound:
            await interaction.response.send_message("❌ Event not found.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error getting event info: {e}")
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="delete_event", description="Delete an event")
    @app_commands.describe(event_id="The ID of the event to delete")
    async def delete_event(self, interaction: discord.Interaction, event_id: str):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)

        if not has_event_access(interaction):
            return await interaction.response.send_message("❌ Permission denied!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        try:
            event_id_int = int(event_id.strip())
        except ValueError:
            return await interaction.followup.send("❌ Invalid event ID format.", ephemeral=True)

        try:
            event = await interaction.guild.fetch_scheduled_event(event_id_int)
            event_name = event.name
            await event.delete()
            await interaction.followup.send(f"✅ Deleted event: **{event_name}**", ephemeral=True)
            
        except discord.NotFound:
            await interaction.followup.send("❌ Event not found!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            await interaction.followup.send(f"❌ Delete failed: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Events(bot))