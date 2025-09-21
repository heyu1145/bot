import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, TextInput, Modal, Select
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import asyncio
import re
import io
from utils.storage import (
    load_multi_ticket_configs, save_multi_ticket_configs, get_multi_ticket_setup_by_id,
    load_ticket_configs, save_ticket_configs, get_ticket_setup_by_id,
    load_active_tickets, save_active_ticket, get_ticket_data, remove_active_ticket,
    load_staff_roles, increment_user_ticket_count, reset_user_ticket_count,
    load_user_ticket_counts, update_ticket_data
)
from utils.permissions import is_admin_or_owner, has_event_access

# JoinTicketView class
class JoinTicketView(View):
    def __init__(self, thread_id: str, guild_id: str, handle_msg_id: str):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.guild_id = guild_id
        self.handle_msg_id = handle_msg_id

    @discord.ui.button(label="Join Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="join_ticket")
    async def join_ticket(self, interaction: discord.Interaction, button: Button):
        try:
            thread = interaction.guild.get_thread(int(self.thread_id))
            if thread:
                await thread.add_user(interaction.user)
                
                # Update the handle message to show who joined
                try:
                    ticket_data = get_ticket_data(self.guild_id, self.thread_id)
                    if ticket_data and 'handle_channel_id' in ticket_data:
                        handle_channel = interaction.guild.get_channel(int(ticket_data['handle_channel_id']))
                        if handle_channel:
                            handle_msg = await handle_channel.fetch_message(int(self.handle_msg_id))
                            
                            # Get current joined staff list or initialize empty list
                            joined_staff = ticket_data.get('joined_staff', [])
                            
                            # Add current staff if not already in list
                            staff_info = {
                                'id': str(interaction.user.id),
                                'name': interaction.user.display_name,
                                'joined_at': datetime.now(timezone.utc).isoformat()
                            }
                            
                            if not any(staff['id'] == str(interaction.user.id) for staff in joined_staff):
                                joined_staff.append(staff_info)
                                ticket_data['joined_staff'] = joined_staff
                                update_ticket_data(self.guild_id, self.thread_id, ticket_data)
                            
                            # Update the embed with joined staff information
                            embed = handle_msg.embeds[0] if handle_msg.embeds else discord.Embed()
                            
                            # Clear existing fields and rebuild
                            embed.clear_fields()
                            
                            # Add basic info
                            embed.add_field(
                                name="Ticket Information",
                                value=f"**Creator:** {ticket_data.get('user_mention', 'Unknown')}\n**Ticket:** {thread.mention}",
                                inline=False
                            )
                            
                            # Add joined staff information
                            if joined_staff:
                                staff_list = "\n".join([f"• {staff['name']} (<t:{int(datetime.fromisoformat(staff['joined_at']).timestamp())}:R>)" for staff in joined_staff])
                                embed.add_field(
                                    name=f"Joined Staff ({len(joined_staff)})",
                                    value=staff_list,
                                    inline=False
                                )
                            else:
                                embed.add_field(
                                    name="Joined Staff (0)",
                                    value="No staff members have joined yet",
                                    inline=False
                                )
                            
                            await handle_msg.edit(embed=embed)
                except Exception as e:
                    print(f"Error updating handle message: {e}")
                
                await interaction.response.send_message(f"✅ Joined ticket: {thread.mention}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Ticket not found!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error joining ticket: {str(e)}", ephemeral=True)

# CloseReasonModal class
class CloseReasonModal(Modal, title="🔒 Close Ticket"):
    reason = TextInput(label="Reason for closing", placeholder="Optional reason for closing...", style=discord.TextStyle.paragraph, required=False, max_length=500)

    def __init__(self, guild_id: str, thread_id: str, ticket_data: dict):
        super().__init__()
        self.guild_id = guild_id
        self.thread_id = thread_id
        self.ticket_data = ticket_data

    async def on_submit(self, interaction: discord.Interaction):
        reason = str(self.reason) if self.reason.value else "No reason provided"
        view = ConfirmCloseView(self.guild_id, self.thread_id, reason, self.ticket_data)
        await interaction.response.send_message(f"**Are you sure you want to close this ticket?**\nReason: {reason}", view=view, ephemeral=True)

# ConfirmCloseView class
class ConfirmCloseView(View):
    def __init__(self, guild_id: str, thread_id: str, reason: str, ticket_data: dict):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.thread_id = thread_id
        self.reason = reason
        self.ticket_data = ticket_data

    @discord.ui.button(label="Confirm Close", style=discord.ButtonStyle.danger, emoji="🔒")
    async def confirm_close(self, interaction: discord.Interaction, button: Button):
        try:
            thread = interaction.guild.get_thread(int(self.thread_id))
            if thread:
                # Get ticket data
                ticket_data = get_ticket_data(self.guild_id, self.thread_id)
                if not ticket_data:
                    await interaction.response.send_message("❌ Ticket data not found!", ephemeral=True)
                    return
                
                # Create transcript
                await self.create_transcript(interaction.guild, thread, self.reason, ticket_data)
                
                # Archive the thread
                await thread.edit(archived=True, locked=True)
                
                # Remove from active tickets
                remove_active_ticket(self.guild_id, self.thread_id)
                
                await interaction.response.send_message("✅ Ticket closed and archived!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Ticket not found!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error closing ticket: {str(e)}", ephemeral=True)

    async def create_transcript(self, guild: discord.Guild, thread: discord.Thread, reason: str, ticket_data: dict):
        """Create a transcript of the ticket and send it to the transcripts channel"""
        try:
            # Get the ticket config to find transcripts channel
            panel_id = ticket_data.get('panel_id', '')
            option_id = ticket_data.get('option_id', '')
            
            if not panel_id:
                return  # No panel ID, can't find transcripts channel
            
            # Get the multi-ticket config
            multi_config = get_multi_ticket_setup_by_id(self.guild_id, panel_id)
            if not multi_config:
                return  # Config not found
            
            # Find the specific option to get transcripts channel
            transcripts_channel_id = None
            for option in multi_config.get("ticket_options", []):
                if option.get("id") == option_id:
                    transcripts_channel_id = option.get("transcripts_channel_id")
                    break
            
            if not transcripts_channel_id:
                return  # No transcripts channel configured
            
            # Get the transcripts channel
            transcripts_channel = guild.get_channel(int(transcripts_channel_id))
            if not transcripts_channel:
                return  # Channel not found
            
            # Create transcript content
            transcript_content = await self.generate_transcript(thread, reason, ticket_data)
            
            # Send transcript to transcripts channel
            transcript_file = discord.File(
                io.BytesIO(transcript_content.encode('utf-8')),
                filename=f"transcript-{thread.name}.txt"
            )
            
            # Create a summary of staff participation
            joined_staff = ticket_data.get('joined_staff', [])
            staff_summary = "\n".join([f"• {staff['name']}" for staff in joined_staff]) if joined_staff else "No staff joined"
            
            embed = discord.Embed(
                title=f"Transcript: {thread.name}",
                description=f"Ticket closed by {ticket_data.get('closer_name', 'Unknown')}",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Created by", value=ticket_data.get('user_mention', 'Unknown'), inline=True)
            embed.add_field(name="Created at", value=ticket_data.get('created_at', 'Unknown'), inline=True)
            embed.add_field(name=f"Staff Joined ({len(joined_staff)})", value=staff_summary, inline=False)
            
            await transcripts_channel.send(embed=embed, file=transcript_file)
            
        except Exception as e:
            print(f"Error creating transcript: {e}")

    async def generate_transcript(self, thread: discord.Thread, reason: str, ticket_data: dict) -> str:
        """Generate a text transcript of the ticket"""
        transcript = []
        transcript.append(f"Ticket Transcript: {thread.name}")
        transcript.append("=" * 50)
        transcript.append(f"Created by: {ticket_data.get('user_mention', 'Unknown')}")
        transcript.append(f"Created at: {ticket_data.get('created_at', 'Unknown')}")
        transcript.append(f"Closed by: {ticket_data.get('closer_name', 'Unknown')}")
        transcript.append(f"Closed at: {datetime.now(timezone.utc).isoformat()}")
        transcript.append(f"Reason: {reason}")
        
        # Add staff participation info
        joined_staff = ticket_data.get('joined_staff', [])
        transcript.append(f"Staff Joined: {len(joined_staff)}")
        for staff in joined_staff:
            transcript.append(f"  • {staff['name']} (Joined: {staff.get('joined_at', 'Unknown')})")
        
        transcript.append("=" * 50)
        transcript.append("MESSAGES:")
        transcript.append("=" * 50)
        
        # Fetch all messages in the thread
        try:
            async for message in thread.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = message.author.display_name
                content = message.clean_content
                
                # Handle attachments
                attachments = ""
                if message.attachments:
                    attachments = " [Attachments: " + ", ".join(a.url for a in message.attachments) + "]"
                
                transcript.append(f"[{timestamp}] {author}: {content}{attachments}")
        except Exception as e:
            transcript.append(f"Error fetching messages: {e}")
        
        return "\n".join(transcript)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Ticket closure cancelled.", view=None)

# CloseTicketView class
class CloseTicketView(View):
    def __init__(self, guild_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        if not interaction.channel or not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message("❌ This can only be used in ticket threads!", ephemeral=True)
            return
        
        # Get ticket data
        ticket_data = get_ticket_data(self.guild_id, str(interaction.channel.id))
        if not ticket_data:
            await interaction.response.send_message("❌ This doesn't appear to be a valid ticket!", ephemeral=True)
            return
        
        # Store who is closing the ticket
        ticket_data['closer_id'] = str(interaction.user.id)
        ticket_data['closer_name'] = interaction.user.display_name
        
        modal = CloseReasonModal(self.guild_id, str(interaction.channel.id), ticket_data)
        await interaction.response.send_modal(modal)

# TicketTypeModal class
class TicketTypeModal(Modal, title="🎫 Ticket Panel Setup"):
    panel_title = TextInput(label="Panel Title", placeholder="e.g., Support Center", default="Support Tickets", max_length=100, required=True)
    panel_description = TextInput(label="Panel Description", placeholder="Describe what this panel is for...", default="Click the button below to create a ticket", style=discord.TextStyle.paragraph, max_length=1000, required=True)
    
    def __init__(self, channel: discord.TextChannel, is_multi: bool = False):
        super().__init__()
        self.channel = channel
        self.is_multi = is_multi

    async def on_submit(self, interaction: discord.Interaction):
        if self.is_multi:
            view = MultiTicketSetupView(self.channel, str(self.panel_title), str(self.panel_description))
            await interaction.response.send_message("🎛️ **Multi-Ticket Panel Setup**\nAdd ticket options below:", view=view, ephemeral=True)
        else:
            view = SingleTicketSetupView(self.channel, str(self.panel_title), str(self.panel_description))
            await interaction.response.send_message("🎛️ **Single Ticket Panel Setup**\nConfigure your ticket options:", view=view, ephemeral=True)

# SingleTicketSetupView class
class SingleTicketSetupView(View):
    def __init__(self, channel: discord.TextChannel, panel_title: str, panel_description: str):
        super().__init__(timeout=300)
        self.channel = channel
        self.panel_title = panel_title
        self.panel_description = panel_description
        self.config_data = None

    @discord.ui.button(label="Configure Ticket", style=discord.ButtonStyle.primary, emoji="⚙️", row=0)
    async def configure_ticket(self, interaction: discord.Interaction, button: Button):
        modal = TicketConfigModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if hasattr(modal, 'config_data'):
            self.config_data = modal.config_data
            # Enable the create panel button
            self.create_panel.disabled = False
            await interaction.edit_original_response(
                content=f"✅ Configuration saved! Click 'Create Panel' to create the ticket panel.\n**Option:** {self.config_data['button_label']}",
                view=self
            )

    @discord.ui.button(label="Create Panel", style=discord.ButtonStyle.success, emoji="🚀", row=1, disabled=True)
    async def create_panel(self, interaction: discord.Interaction, button: Button):
        if not self.config_data:
            await interaction.response.send_message("❌ Please configure the ticket options first!", ephemeral=True)
            return

        await self.create_single_ticket_panel(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="❌ Cancelled panel creation.", view=None)

    async def create_single_ticket_panel(self, interaction: discord.Interaction):
        try:
            if not self.config_data or 'handle_channel_id' not in self.config_data:
                await interaction.response.send_message("❌ Please configure the ticket options first!", ephemeral=True)
                return

            guild_id = str(interaction.guild.id)
            setup_id = uuid.uuid4().hex[:8]
            
            # Create single ticket config
            ticket_config = {
                "id": setup_id,
                "ticket_channel_id": str(self.channel.id),
                "handle_channel_id": self.config_data['handle_channel_id'],
                "transcripts_channel_id": self.config_data.get('transcripts_channel_id'),
                "title_format": self.config_data['title_format'],
                "open_message": self.config_data['open_message'],
                "button_label": self.config_data['button_label'],
                "button_emoji": self.config_data.get('button_emoji'),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to both systems for compatibility
            all_configs = load_ticket_configs(guild_id)
            all_configs.append(ticket_config)
            save_ticket_configs(guild_id, all_configs)
            
            # Create multi-ticket config with single option for unified system
            multi_config = {
                "id": setup_id,
                "panel_channel_id": str(self.channel.id),
                "panel_title": self.panel_title,
                "panel_description": self.panel_description,
                "ticket_options": [{
                    'id': uuid.uuid4().hex[:6],
                    'button_label': self.config_data['button_label'],
                    'button_emoji': self.config_data.get('button_emoji'),
                    'title_format': self.config_data['title_format'],
                    'open_message': self.config_data['open_message'],
                    'handle_channel_id': self.config_data['handle_channel_id'],
                    'transcripts_channel_id': self.config_data.get('transcripts_channel_id'),
                    'created_at': datetime.now(timezone.utc).isoformat()
                }],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            multi_configs = load_multi_ticket_configs(guild_id)
            multi_configs.append(multi_config)
            save_multi_ticket_configs(guild_id, multi_configs)

            # Create and send the panel
            embed = discord.Embed(
                title=self.panel_title,
                description=self.panel_description,
                color=discord.Color.green()
            )
            
            emoji_str = f"{self.config_data.get('button_emoji', '')} " if self.config_data.get('button_emoji') else ""
            embed.add_field(
                name="📋 Support Option",
                value=f"• {emoji_str}**{self.config_data['button_label']}**",
                inline=False
            )
            
            view = MultiTicketView(guild_id, setup_id)
            message = await self.channel.send(embed=embed, view=view)

            await interaction.response.edit_message(
                content=f"✅ Single ticket panel created successfully!\n**ID:** `{setup_id}`\n**Channel:** {self.channel.mention}\n**Message:** {message.jump_url}",
                view=None
            )
            
        except Exception as e:
            await interaction.response.edit_message(
                content=f"❌ Error creating panel: {str(e)}",
                view=None
            )

# MultiTicketSetupView class
class MultiTicketSetupView(View):
    def __init__(self, channel: discord.TextChannel, panel_title: str, panel_description: str):
        super().__init__(timeout=300)
        self.channel = channel
        self.panel_title = panel_title
        self.panel_description = panel_description
        self.ticket_options = []

    @discord.ui.button(label="Add Ticket Option", style=discord.ButtonStyle.primary, emoji="➕", row=0)
    async def add_option(self, interaction: discord.Interaction, button: Button):
        modal = TicketConfigModal()
        modal.interaction = interaction
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if hasattr(modal, 'config_data') and modal.config_data:
            self.ticket_options.append(modal.config_data)
            await modal.interaction.followup.send(
                f"✅ Option '{modal.config_data['button_label']}' added successfully!",
                ephemeral=True
            )

    @discord.ui.button(label="Create Panel", style=discord.ButtonStyle.success, emoji="🚀", row=1)
    async def create_panel(self, interaction: discord.Interaction, button: Button):
        if not self.ticket_options:
            await interaction.response.send_message("❌ Please add at least one ticket option!", ephemeral=True)
            return

        try:
            guild_id = str(interaction.guild.id)
            setup_id = uuid.uuid4().hex[:8]

            # Prepare multi-ticket options
            multi_options = []
            for option in self.ticket_options:
                if 'handle_channel_id' not in option:
                    await interaction.response.send_message(f"❌ Option '{option['button_label']}' is missing handle channel!", ephemeral=True)
                    return
                    
                multi_options.append({
                    'id': uuid.uuid4().hex[:6],
                    'button_label': option['button_label'],
                    'button_emoji': option.get('button_emoji'),
                    'title_format': option['title_format'],
                    'open_message': option['open_message'],
                    'handle_channel_id': option['handle_channel_id'],
                    'transcripts_channel_id': option.get('transcripts_channel_id'),
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            config = {
                "id": setup_id,
                "panel_channel_id": str(self.channel.id),
                "panel_title": self.panel_title,
                "panel_description": self.panel_description,
                "ticket_options": multi_options,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            all_configs = load_multi_ticket_configs(guild_id)
            all_configs.append(config)
            save_multi_ticket_configs(guild_id, all_configs)

            # Create embed
            embed = discord.Embed(
                title=self.panel_title,
                description=self.panel_description,
                color=discord.Color.green()
            )
            
            options_text = []
            for option in self.ticket_options:
                emoji_str = f"{option.get('button_emoji', '')} " if option.get('button_emoji') else ""
                options_text.append(f"• {emoji_str}**{option['button_label']}**")
            
            embed.add_field(
                name="📋 Available Support Options",
                value="\n".join(options_text),
                inline=False
            )
            
            view = MultiTicketView(guild_id, setup_id)
            await self.channel.send(embed=embed, view=view)

            await interaction.response.send_message(
                f"✅ Multi-ticket panel created successfully!\n**ID:** `{setup_id}`\n**Channel:** {self.channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌", row=1)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("❌ Cancelled panel creation.", ephemeral=True)

# TicketConfigModal class
class TicketConfigModal(Modal, title="🎫 Configure Ticket Option"):
    button_label = TextInput(label="Button Label", placeholder="e.g., Technical Support", max_length=80, required=True)
    button_emoji = TextInput(label="Button Emoji (optional)", placeholder="e.g., 🛠️", max_length=10, required=False)
    title_format = TextInput(label="Ticket Title Format", placeholder="Use {username} or {userid}", default="ticket-{username}", max_length=100, required=True)
    open_message = TextInput(label="Welcome Message", placeholder="Message shown when ticket is opened", default="Please describe your issue...", style=discord.TextStyle.paragraph, max_length=1000, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        self.config_data = {
            'button_label': str(self.button_label),
            'button_emoji': str(self.button_emoji) if self.button_emoji.value else None,
            'title_format': str(self.title_format),
            'open_message': str(self.open_message)
        }
        
        # Show channel selection view
        view = ChannelSelectView(self.config_data, interaction.guild)
        await interaction.response.send_message(
            f"✅ Basic info saved! Now select handle channel for: **{self.button_label.value}**",
            view=view,
            ephemeral=True
        )

# ChannelSelectView class
class ChannelSelectView(View):
    def __init__(self, config_data: dict, guild: discord.Guild):
        super().__init__(timeout=120)
        self.config_data = config_data
        self.guild = guild
        
        self.select = Select(
            placeholder="Select handle channel...",
            options=self.get_channel_options(),
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_channel_callback
        self.add_item(self.select)

    def get_channel_options(self):
        options = []
        for channel in self.guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                channel_name = channel.name
                if len(channel_name) > 25:
                    channel_name = channel_name[:22] + "..."
                options.append(discord.SelectOption(
                    label=channel_name,
                    value=str(channel.id),
                    description=f"ID: {channel.id}"[:50]
                ))
        return options

    async def select_channel_callback(self, interaction: discord.Interaction):
        handle_channel_id = self.select.values[0]
        handle_channel = self.guild.get_channel(int(handle_channel_id))
        
        if not handle_channel:
            await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
            return

        self.config_data['handle_channel_id'] = str(handle_channel.id)
        
        # Show transcript channel selection
        view = TranscriptSelectView(self.config_data, self.guild)
        await interaction.response.edit_message(
            content=f"✅ Handle channel set! Now select transcripts channel for **{self.config_data['button_label']}** (optional):",
            view=view
        )

# TranscriptSelectView class
class TranscriptSelectView(View):
    def __init__(self, config_data: dict, guild: discord.Guild):
        super().__init__(timeout=120)
        self.config_data = config_data
        self.guild = guild
        
        self.select = Select(
            placeholder="Select transcripts channel (optional)...",
            options=self.get_channel_options(),
            min_values=0,
            max_values=1
        )
        self.select.callback = self.select_transcript_callback
        self.add_item(self.select)
        
        skip_button = Button(label="Skip Transcripts", style=discord.ButtonStyle.secondary)
        skip_button.callback = self.skip_transcripts_callback
        self.add_item(skip_button)

    def get_channel_options(self):
        options = []
        for channel in self.guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                channel_name = channel.name
                if len(channel_name) > 25:
                    channel_name = channel_name[:22] + "..."
                options.append(discord.SelectOption(
                    label=channel_name,
                    value=str(channel.id),
                    description=f"ID: {channel.id}"[:50]
                ))
        return options

    async def select_transcript_callback(self, interaction: discord.Interaction):
        if self.select.values:
            transcript_channel_id = self.select.values[0]
            self.config_data['transcripts_channel_id'] = str(transcript_channel_id)
        else:
            self.config_data['transcripts_channel_id'] = None
        
        await self.finish_config(interaction)

    async def skip_transcripts_callback(self, interaction: discord.Interaction):
        self.config_data['transcripts_channel_id'] = None
        await self.finish_config(interaction)

    async def finish_config(self, interaction: discord.Interaction):
        option_str = f"**{self.config_data['button_label']}** → <#{self.config_data['handle_channel_id']}>"
        if self.config_data['transcripts_channel_id']:
            option_str += f" (Transcripts: <#{self.config_data['transcripts_channel_id']}>)"
        
        await interaction.response.edit_message(
            content=f"✅ Option configured: {option_str}",
            view=None
        )

# Unified Ticket View (works for both single and multi-ticket panels)
class MultiTicketView(View):
    def __init__(self, guild_id: str, panel_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.panel_id = panel_id
        self.load_buttons()

    def load_buttons(self):
        self.clear_items()
        multi_config = get_multi_ticket_setup_by_id(self.guild_id, self.panel_id)
        
        if multi_config and "ticket_options" in multi_config:
            for option in multi_config["ticket_options"]:
                button = Button(
                    label=option["button_label"],
                    emoji=option["button_emoji"] if option.get("button_emoji") else None,
                    style=discord.ButtonStyle.primary,
                    custom_id=f"ticket_{self.panel_id}_{option['id']}"
                )
                button.callback = self.create_callback(option)
                self.add_item(button)

    def create_callback(self, option):
        async def callback(interaction: discord.Interaction):
            await self.open_ticket(interaction, option)
        return callback
    async def open_ticket(self, interaction: discord.Interaction, option):
        user_id = interaction.user.id
        guild_id = self.guild_id
    
        if str(interaction.guild.id) != guild_id:
            return await interaction.response.send_message("❌ Invalid server!", ephemeral=True)

        if str(user_id) in load_active_tickets(guild_id):
            return await interaction.response.send_message("❌ You already have an active ticket!", ephemeral=True)

        try:
            handle_channel = await interaction.guild.fetch_channel(int(option["handle_channel_id"]))
            title = option["title_format"].replace("{username}", interaction.user.name).replace("{userid}", str(user_id))
        
            thread = await interaction.channel.create_thread(
                name=title[:100],
                type=discord.ChannelType.private_thread,
                invitable=False
            )
        
            staff_roles = load_staff_roles(guild_id)
            for role_id in staff_roles:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    await thread.set_permissions(role, view_channel=True, send_messages=True)
                    
           # Create a proper embed for the handle message
            handle_embed = discord.Embed(
                title=f"New Ticket: {option['button_label']}",
                description=f"**Creator:** {interaction.user.mention}\n**Ticket:** {thread.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            handle_embed.add_field(
                name="Joined Staff (0)",
                value="No staff members have joined yet",
                inline=False
            )
            handle_embed.set_footer(text=f"User ID: {interaction.user.id} | Ticket ID: {thread.id}")
        
            # First create the message
            handle_msg = await handle_channel.send(embed=handle_embed)
        
            # Then create the view with the message ID
            join_view = JoinTicketView(str(thread.id), guild_id, str(handle_msg.id))
            await handle_msg.edit(view=join_view)

            # Store ticket data with panel and option IDs for transcript functionality
            ticket_data = {
                'user_id': str(user_id),
                'user_name': interaction.user.name,
                'user_mention': interaction.user.mention,
                'thread_id': str(thread.id),
                'handle_msg_id': str(handle_msg.id),
                'handle_channel_id': str(handle_channel.id),
                'panel_id': self.panel_id,
                'option_id': option['id'],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'joined_staff': []  # Initialize empty list for staff who join
            }
        
            save_active_ticket(guild_id, user_id, str(thread.id), str(handle_msg.id), f"multi_{self.panel_id}_{option['id']}", ticket_data)
            increment_user_ticket_count(guild_id, user_id)

        # Create a proper welcome embed instead of plain text
            welcome_embed = discord.Embed(
                title=f"Welcome to your {option['button_label']} ticket!",
                description=option['open_message'],
                color=discord.Color.green()
            )
        welcome_embed.add_field(name="Support Team", value="Our staff will be with you shortly.", inline=False)
        welcome_embed.set_footer(text="Click the button below to close this ticket")
        
            await thread.send(interaction.user.mention, embed=welcome_embed, view=CloseTicketView(guild_id))
        
            await interaction.response.send_message(f"✅ Ticket created: {thread.mention}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

# Tickets Cog
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_ticket_panel", description="Create a ticket panel (single or multi-option)")
    @app_commands.describe(
        channel="Channel where the panel will be created",
        panel_type="Type of ticket panel to create"
    )
    @app_commands.choices(panel_type=[
        app_commands.Choice(name="Single Option", value="single"),
        app_commands.Choice(name="Multiple Options", value="multi")
    ])
    async def create_ticket_panel(self, interaction: discord.Interaction, channel: discord.TextChannel, panel_type: app_commands.Choice[str]):
        if not interaction.guild: 
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)
        if not is_admin_or_owner(interaction): 
            return await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        
        is_multi = panel_type.value == "multi"
        modal = TicketTypeModal(channel, is_multi)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="list_ticket_panels", description="List all ticket panels in this server")
    async def list_ticket_panels(self, interaction: discord.Interaction):
        if not interaction.guild: 
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        multi_configs = load_multi_ticket_configs(guild_id)
        
        if not multi_configs:
            return await interaction.response.send_message("ℹ️ No ticket panels found for this server", ephemeral=True)

        embed = discord.Embed(title="📋 Ticket Panels", color=discord.Color.blue())
        
        for config in multi_configs:
            channel = interaction.guild.get_channel(int(config["panel_channel_id"]))
            options_count = len(config.get("ticket_options", []))
            embed.add_field(
                name=f"Panel ID: `{config['id']}`",
                value=f"Channel: {channel.mention if channel else 'Unknown'}\nOptions: {options_count}\nCreated: {datetime.fromisoformat(config['created_at']).strftime('%Y-%m-%d')}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="delete_ticket_panel", description="Delete a ticket panel by ID")
    @app_commands.describe(panel_id="ID of the ticket panel to delete")
    async def delete_ticket_panel(self, interaction: discord.Interaction, panel_id: str):
        if not interaction.guild: 
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)
        if not is_admin_or_owner(interaction): 
            return await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        
        # Delete from multi-ticket configs
        multi_configs = load_multi_ticket_configs(guild_id)
        multi_configs = [c for c in multi_configs if c['id'] != panel_id]
        save_multi_ticket_configs(guild_id, multi_configs)
        
        # Delete from single ticket configs
        ticket_configs = load_ticket_configs(guild_id)
        ticket_configs = [c for c in ticket_configs if c['id'] != panel_id]
        save_ticket_configs(guild_id, ticket_configs)
        
        await interaction.response.send_message(f"✅ Ticket panel `{panel_id}` has been deleted", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
