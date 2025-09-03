import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, TextInput, Modal
import os
import pytz
import uuid
from datetime import datetime, timedelta
import json
import re
import asyncio
from keep_alive import keep_alive
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


# --------------------------
# Token Validation
# --------------------------
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    print("❌ ERROR: No Discord token found! Set DISCORD_TOKEN in .env")
    exit(1)

# --------------------------
# Persistent Storage Functions with Server Isolation
# --------------------------
def load_multi_ticket_configs(guild_id):
    """Load multi-ticket panel configurations for a server"""
    path = get_server_data_path(guild_id, "multi_ticket_configs.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_multi_ticket_configs(guild_id, configs):
    """Save multi-ticket panel configurations"""
    path = get_server_data_path(guild_id, "multi_ticket_configs.json")
    with open(path, 'w') as f:
        json.dump(configs, f, indent=2)

def get_multi_ticket_setup_by_id(guild_id, setup_id):
    """Get a specific multi-ticket setup by ID"""
    configs = load_multi_ticket_configs(guild_id)
    for config in configs:
        if config['id'] == setup_id:
            return config
    return None

def update_multi_ticket_config(guild_id, config):
    """Update a multi-ticket configuration"""
    all_configs = load_multi_ticket_configs(guild_id)
    # Remove old config if exists
    all_configs = [c for c in all_configs if c['id'] != config['id']]
    # Add updated config
    all_configs.append(config)
    save_multi_ticket_configs(guild_id, all_configs)
def get_server_data_path(guild_id, filename):
    """Get path to server-specific data file"""
    if not os.path.exists(f"servers/{guild_id}"):
        os.makedirs(f"servers/{guild_id}")
    return f"servers/{guild_id}/{filename}"

# User timezones (server-specific)
def load_user_timezones(guild_id):
    path = get_server_data_path(guild_id, "user_timezones.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}

def save_user_timezone(guild_id, user_id, timezone):
    timezones = load_user_timezones(guild_id)
    timezones[str(user_id)] = timezone
    with open(get_server_data_path(guild_id, "user_timezones.json"), 'w') as f:
        json.dump(timezones, f, indent=2)

# Staff roles (server-specific)
def load_staff_roles(guild_id):
    path = get_server_data_path(guild_id, "staff_roles.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_staff_roles(guild_id, staff_roles):
    with open(get_server_data_path(guild_id, "staff_roles.json"), 'w') as f:
        json.dump(staff_roles, f, indent=2)

# Ticket setups (server-specific with unique IDs)
def load_ticket_configs(guild_id):
    path = get_server_data_path(guild_id, "ticket_configs.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_ticket_configs(guild_id, configs):
    with open(get_server_data_path(guild_id, "ticket_configs.json"), 'w') as f:
        json.dump(configs, f, indent=2)

def get_ticket_setup_by_id(guild_id, setup_id):
    configs = load_ticket_configs(guild_id)
    for c in configs:
        if c['id'] == setup_id:
            return c
    return None

# Active tickets (server-specific)
def load_active_tickets(guild_id):
    path = get_server_data_path(guild_id, "active_tickets.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}

def save_active_ticket(guild_id, user_id, thread_id, handle_msg_id, setup_id):
    try:
        tickets = load_active_tickets(guild_id)
        user_id_str = str(user_id)
        tickets[user_id_str] = {
            "thread_id": thread_id,
            "handle_msg_id": handle_msg_id,
            "setup_id": setup_id,
            "created_at": datetime.utcnow().isoformat()
        }
        with open(get_server_data_path(guild_id, "active_tickets.json"), 'w') as f:
            json.dump(tickets, f, indent=2)
        print(f"✅ Saved active ticket - Server: {guild_id}, User: {user_id_str}")
        return True
    except Exception as e:
        print(f"❌ Failed to save active ticket: {str(e)}")
        return False

def get_ticket_data(guild_id, user_id):
    try:
        tickets = load_active_tickets(guild_id)
        return tickets.get(str(user_id))
    except Exception as e:
        print(f"❌ Error getting ticket data: {str(e)}")
        return None

def remove_active_ticket(guild_id, user_id):
    try:
        tickets = load_active_tickets(guild_id)
        user_id_str = str(user_id)

        if user_id_str not in tickets:
            print(f"ℹ️ Ticket for user {user_id_str} (Server: {guild_id}) already removed")
            return False

        setup_id = tickets[user_id_str].get("setup_id", "unknown")
        del tickets[user_id_str]
        with open(get_server_data_path(guild_id, "active_tickets.json"), 'w') as f:
            json.dump(tickets, f, indent=2)
        print(f"✅ Removed ticket - Server: {guild_id}, User: {user_id_str}, Setup: {setup_id}")
        return True
    except Exception as e:
        print(f"❌ Error removing active ticket: {str(e)}")
        return False

# User ticket counts (server-specific)
def load_user_ticket_counts(guild_id):
    path = get_server_data_path(guild_id, "user_ticket_counts.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}

def save_user_ticket_count(guild_id, user_id, count):
    counts = load_user_ticket_counts(guild_id)
    counts[str(user_id)] = count
    with open(get_server_data_path(guild_id, "user_ticket_counts.json"), 'w') as f:
        json.dump(counts, f, indent=2)

def increment_user_ticket_count(guild_id, user_id):
    counts = load_user_ticket_counts(guild_id)
    current = counts.get(str(user_id), 0)
    new_count = current + 1
    save_user_ticket_count(guild_id, user_id, new_count)
    return new_count

def reset_user_ticket_count(guild_id, user_id):
    save_user_ticket_count(guild_id, user_id, 0)

# --------------------------
# Permission Checks
# --------------------------
def is_admin_or_owner(interaction: discord.Interaction) -> bool:
    if not interaction.guild:
        return False
    return interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator

def has_event_access(interaction: discord.Interaction) -> bool:
    if not interaction.guild:
        return False

    if is_admin_or_owner(interaction):
        return True

    guild_id = str(interaction.guild.id)
    staff_role_ids = load_staff_roles(guild_id)
    for role in interaction.user.roles:
        if str(role.id) in staff_role_ids:
            return True
    return False

# --------------------------
# Ticket System Classes
# --------------------------
async def generate_transcript(thread: discord.Thread, close_reason: str = None, closer: discord.User = None):
    transcript = []
    transcript.append(f"=== Ticket Transcript - {thread.name} ===")
    transcript.append(f"Created: {thread.created_at.strftime('%Y-%m-%d %H:%M UTC')}")
    transcript.append(f"Creator: {thread.owner.name} (ID: {thread.owner.id})")
    transcript.append(f"Closed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    if closer:
        transcript.append(f"Closed by: {closer.name} (ID: {closer.id})")
    if close_reason:
        transcript.append(f"Close Reason: {close_reason}")
    transcript.append("\n=== Conversation ===\n")

    messages = []
    async for msg in thread.history(limit=None, oldest_first=True):
        messages.append(msg)

    for msg in messages:
        timestamp = msg.created_at.strftime('%H:%M:%S')
        transcript.append(f"[{timestamp}] {msg.author.name}: {msg.content or '[Attachment/Embed]'}")

    return "\n".join(transcript)

class TicketPanelModal(Modal, title="Create Multi-Ticket Panel"):
    panel_title = TextInput(
        label="Panel Title",
        placeholder="Enter panel title (e.g., Support Center)",
        default="Support Tickets",
        max_length=100,
        required=True
    )
    
    panel_description = TextInput(
        label="Panel Description",
        placeholder="Enter panel description",
        default="Choose the type of support you need:",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        setup_id = uuid.uuid4().hex[:8]

        config = {
            "id": setup_id,
            "panel_channel_id": str(self.channel.id),
            "panel_title": str(self.panel_title),
            "panel_description": str(self.panel_description),
            "ticket_options": [],
            "created_at": datetime.utcnow().isoformat()
        }

        all_configs = load_multi_ticket_configs(guild_id)
        all_configs.append(config)
        save_multi_ticket_configs(guild_id, all_configs)

        # 创建面板
        embed = discord.Embed(
            title=str(self.panel_title),
            description=str(self.panel_description),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Available Ticket Types",
            value="No ticket options added yet. Click 'Manage Options' below to add ticket types.",
            inline=False
        )
        embed.set_footer(text=f"Panel ID: {setup_id}")

        view = MultiTicketManagementView(guild_id, setup_id)
        await self.channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(
            f"✅ Multi-ticket panel created successfully!\n"
            f"**Panel ID:** `{setup_id}`\n"
            f"**Channel:** {self.channel.mention}\n\n"
            f"Click 'Manage Options' on the panel to add ticket types.",
            ephemeral=True
        )

class TicketOptionModal(Modal, title="Add Ticket Option"):
    button_label = TextInput(
        label="Button Label",
        placeholder="e.g., Technical Support, Billing Help",
        max_length=80,
        required=True
    )
    
    button_emoji = TextInput(
        label="Button Emoji (optional)",
        placeholder="e.g., 🛠️, 💰, ❓",
        max_length=10,
        required=False
    )
    
    title_format = TextInput(
        label="Ticket Title Format",
        placeholder="Use {username} or {userid}",
        default="ticket-{username}",
        max_length=100,
        required=True
    )
    
    open_message = TextInput(
        label="Welcome Message",
        placeholder="Message shown when ticket is opened",
        default="Please describe your issue and our team will assist you shortly.",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    def __init__(self, panel_id: str, handle_channel: discord.TextChannel, transcripts_channel: discord.TextChannel = None):
        super().__init__()
        self.panel_id = panel_id
        self.handle_channel = handle_channel
        self.transcripts_channel = transcripts_channel

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        multi_config = get_multi_ticket_setup_by_id(guild_id, self.panel_id)
        
        if not multi_config:
            await interaction.response.send_message("❌ Panel not found!", ephemeral=True)
            return

        # 创建票务选项
        ticket_option_id = uuid.uuid4().hex[:6]
        ticket_option = {
            "id": ticket_option_id,
            "button_label": str(self.button_label),
            "button_emoji": str(self.button_emoji) if self.button_emoji.value else None,
            "handle_channel_id": str(self.handle_channel.id),
            "transcripts_channel_id": str(self.transcripts_channel.id) if self.transcripts_channel else None,
            "title_format": str(self.title_format),
            "open_message": str(self.open_message),
            "created_at": datetime.utcnow().isoformat()
        }

        # 添加到配置
        if "ticket_options" not in multi_config:
            multi_config["ticket_options"] = []
        multi_config["ticket_options"].append(ticket_option)

        # 更新配置
        all_configs = load_multi_ticket_configs(guild_id)
        all_configs = [c for c in all_configs if c['id'] != self.panel_id]
        all_configs.append(multi_config)
        save_multi_ticket_configs(guild_id, all_configs)

        # 更新面板
        await update_multi_ticket_panel(interaction.guild, multi_config)

        await interaction.response.send_message(
            f"✅ Ticket option added successfully!\n"
            f"**Label:** {self.button_label.value}\n"
            f"**Handle Channel:** {self.handle_channel.mention}",
            ephemeral=True
        )

class ChannelSelectionView(View):
    def __init__(self, guild_id: str, panel_id: str, action: str):
        super().__init__(timeout=120)
        self.guild_id = guild_id
        self.panel_id = panel_id
        self.action = action
        self.select = None

    async def initialize_options(self, guild):
        """初始化频道选项"""
        options = []
        for channel in guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                options.append(discord.SelectOption(
                    label=channel.name[:25],
                    value=str(channel.id),
                    description=f"ID: {channel.id}"[:50]
                ))
        
        self.select = discord.ui.Select(
            placeholder="Select handle channel...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_handle_channel
        self.add_item(self.select)

    async def select_handle_channel(self, interaction: discord.Interaction):
        handle_channel_id = self.select.values[0]
        handle_channel = interaction.guild.get_channel(int(handle_channel_id))
        
        if not handle_channel:
            await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
            return

        # 继续流程...

class MultiTicketManagementView(View):
    def __init__(self, guild_id: str, panel_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.panel_id = panel_id

    @discord.ui.button(label="Manage Options", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def manage_options(self, interaction: discord.Interaction, button: Button):
        if not has_event_access(interaction):
            await interaction.response.send_message("❌ Only staff can manage ticket options!", ephemeral=True)
            return

        multi_config = get_multi_ticket_setup_by_id(self.guild_id, self.panel_id)
        if not multi_config:
            await interaction.response.send_message("❌ Panel not found!", ephemeral=True)
            return

        # 显示管理选项
        embed = discord.Embed(
            title="🎫 Manage Ticket Options",
            description=f"Panel: **{multi_config['panel_title']}**\nID: `{self.panel_id}`",
            color=discord.Color.blue()
        )

        if "ticket_options" in multi_config and multi_config["ticket_options"]:
            for i, option in enumerate(multi_config["ticket_options"], 1):
                emoji_str = f"{option['button_emoji']} " if option["button_emoji"] else ""
                embed.add_field(
                    name=f"{i}. {emoji_str}{option['button_label']}",
                    value=f"Handle: <#{option['handle_channel_id']}>\nID: `{option['id']}`",
                    inline=False
                )
        else:
            embed.add_field(
                name="No Options Yet",
                value="Click 'Add Option' below to create your first ticket type.",
                inline=False
            )

        view = TicketOptionsManagementView(self.guild_id, self.panel_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Refresh Panel", style=discord.ButtonStyle.success, emoji="🔄")
    async def refresh_panel(self, interaction: discord.Interaction, button: Button):
        if not has_event_access(interaction):
            await interaction.response.send_message("❌ Only staff can refresh the panel!", ephemeral=True)
            return

        multi_config = get_multi_ticket_setup_by_id(self.guild_id, self.panel_id)
        if not multi_config:
            await interaction.response.send_message("❌ Panel not found!", ephemeral=True)
            return

        await update_multi_ticket_panel(interaction.guild, multi_config)
        await interaction.response.send_message("✅ Panel refreshed successfully!", ephemeral=True)

class TicketOptionsManagementView(View):
    def __init__(self, guild_id: str, panel_id: str):
        super().__init__(timeout=120)
        self.guild_id = guild_id
        self.panel_id = panel_id

    @discord.ui.button(label="Add Option", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_option(self, interaction: discord.Interaction, button: Button):
        # 创建频道选择视图
        embed = discord.Embed(
            title="📁 Select Handle Channel",
            description="Please select the channel where staff will handle this type of ticket:",
            color=discord.Color.blue()
        )

        # 传递interaction.guild来获取频道选项
        view = ChannelSelectionView(self.guild_id, self.panel_id, "handle")
        # 需要先初始化选择器选项
        await view.initialize_options(interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TranscriptChannelView(View):
    def __init__(self, guild_id: str, panel_id: str, handle_channel: discord.TextChannel):
        super().__init__(timeout=120)
        self.guild_id = guild_id
        self.panel_id = panel_id
        self.handle_channel = handle_channel
        
        # 创建频道选择下拉菜单
        self.select = Select(
            placeholder="Select transcripts channel...",
            options=self.get_channel_options(handle_channel.guild),
            min_values=0,  # 允许不选择
            max_values=1
        )
        self.select.callback = self.select_transcript_channel
        self.add_item(self.select)
        
        # 添加跳过按钮
        self.add_item(Button(label="Skip Transcripts", style=discord.ButtonStyle.secondary, custom_id="skip_transcripts"))

    def get_channel_options(self, guild):
        """获取文本频道选项"""
        options = []
        for channel in guild.text_channels:
            if isinstance(channel, discord.TextChannel):
                options.append(SelectOption(
                    label=channel.name,
                    value=str(channel.id),
                    description=f"ID: {channel.id}"[:100]
                ))
        return options

    async def select_transcript_channel(self, interaction: discord.Interaction):
        if self.select.values:
            transcript_channel_id = self.select.values[0]
            transcript_channel = interaction.guild.get_channel(int(transcript_channel_id))
            await self.create_option(interaction, transcript_channel)
        else:
            await self.create_option(interaction, None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data.get('custom_id') == 'skip_transcripts':
            await self.create_option(interaction, None)
            return False
        return True

    async def create_option(self, interaction: discord.Interaction, transcripts_channel: discord.TextChannel = None):
        # 打开票务选项创建模态
        modal = TicketOptionModal(self.panel_id, self.handle_channel, transcripts_channel)
        await interaction.response.send_modal(modal)

class JoinTicketView(View):
    def __init__(self, thread_id: str, guild_id: str):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.guild_id = guild_id

    @discord.ui.button(
        label="Join Ticket", 
        style=discord.ButtonStyle.success, 
        emoji="🔗",
        custom_id="join_ticket_button"
    )
    async def join_ticket(self, interaction: discord.Interaction, button: Button):
        if str(interaction.guild.id) != self.guild_id:
            return await interaction.response.send_message("❌ This ticket belongs to another server!", ephemeral=True)

        if not has_event_access(interaction):
            return await interaction.response.send_message("❌ Only staff can join tickets!", ephemeral=True)

        try:
            thread = await interaction.guild.fetch_channel(int(self.thread_id))
            if not isinstance(thread, discord.Thread):
                return await interaction.response.send_message("❌ Ticket not found!", ephemeral=True)

            await thread.add_user(interaction.user)
            await interaction.response.send_message(f"✅ Added to ticket: {thread.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error joining ticket: {str(e)}", ephemeral=True)

class CloseReasonModal(Modal, title="Close Ticket with Reason"):
    reason = TextInput(
        label="Reason for closing",
        style=discord.TextStyle.short,
        placeholder="Enter reason (e.g., 'Issue resolved')",
        required=True,
        max_length=100
    )

    def __init__(self, guild_id: str):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.guild.id) != self.guild_id:
            return await interaction.response.send_message("❌ This ticket belongs to another server!", ephemeral=True)

        thread = interaction.channel
        owner = thread.owner
        owner_id = owner.id
        guild_id = self.guild_id

        ticket_data = get_ticket_data(guild_id, owner_id)
        if not ticket_data:
            return await interaction.response.send_message("❌ Ticket data not found!", ephemeral=True)

        setup_id = ticket_data["setup_id"]
        setup = get_ticket_setup_by_id(guild_id, setup_id)
        if not setup:
            return await interaction.response.send_message("❌ Ticket setup not found!", ephemeral=True)

        # Delete staff join message
        handle_msg_id = ticket_data["handle_msg_id"]
        if handle_msg_id and setup.get("handle_channel_id"):
            try:
                handle_channel = await interaction.guild.fetch_channel(int(setup["handle_channel_id"]))
                handle_msg = await handle_channel.fetch_message(int(handle_msg_id))
                await handle_msg.delete()
                print(f"✅ Deleted staff join message (ID: {handle_msg_id})")
            except discord.NotFound:
                print(f"ℹ️ Staff join message (ID: {handle_msg_id}) already deleted")
            except Exception as e:
                print(f"❌ Error deleting staff join message: {str(e)}")

        # Generate and save transcript
        transcript = await generate_transcript(thread, self.reason.value, interaction.user)
        if setup.get("transcripts_channel_id"):
            try:
                transcripts_channel = await interaction.guild.fetch_channel(int(setup["transcripts_channel_id"]))
                if isinstance(transcripts_channel, discord.TextChannel):
                    with open(f"transcript_{thread.id}.txt", "w", encoding="utf-8") as f:
                        f.write(transcript)

                    await transcripts_channel.send(
                        f"📄 Transcript for {thread.name} (closed by {interaction.user.mention})",
                        file=discord.File(f"transcript_{thread.id}.txt")
                    )
                    os.remove(f"transcript_{thread.id}.txt")
            except Exception as e:
                await interaction.response.send_message(f"⚠️ Could not save transcript: {str(e)}", ephemeral=True)

        # Clean up
        reset_user_ticket_count(guild_id, owner_id)
        remove_active_ticket(guild_id, owner_id)

        await interaction.response.send_message(
            f"Closing ticket. Reason: {self.reason.value}", 
            ephemeral=True
        )
        await thread.send(
            f"Ticket closed by {interaction.user.mention}. Reason: {self.reason.value}\n"
            f"Closing in 5 seconds..."
        )

        await asyncio.sleep(5)
        await thread.delete()

class TicketOpenButton(View):
    def __init__(self, setup_id: str, guild_id: str):
        super().__init__(timeout=None)
        self.setup_id = setup_id
        self.guild_id = guild_id

    @discord.ui.button(
        label="Open Ticket", 
        style=discord.ButtonStyle.primary, 
        emoji="🎫",
        custom_id="open_ticket_button"
    )
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        if str(interaction.guild.id) != self.guild_id:
            return await interaction.response.send_message("❌ This ticket setup belongs to another server!", ephemeral=True)

        user_id = interaction.user.id
        user_id_str = str(user_id)
        guild_id = self.guild_id
        active_tickets = load_active_tickets(guild_id)

        if user_id_str in active_tickets:
            return await interaction.response.send_message(
                "❌ You already have an active ticket!", ephemeral=True
            )

        setup = get_ticket_setup_by_id(guild_id, self.setup_id)
        if not setup:
            return await interaction.response.send_message(
                "❌ Ticket setup not found! Ask an admin to recreate it.", ephemeral=True
            )

        try:
            handle_channel = await interaction.guild.fetch_channel(int(setup["handle_channel_id"]))
            if not isinstance(handle_channel, discord.TextChannel):
                raise ValueError("Handle channel is invalid")
        except Exception as e:
            return await interaction.response.send_message(f"❌ Ticket handle channel error: {str(e)}", ephemeral=True)

        try:
            title = setup["title_format"].replace("{username}", interaction.user.name).replace("{userid}", user_id_str)[:100]
            thread = await interaction.channel.create_thread(
                name=title,
                type=discord.ChannelType.private_thread,
                invitable=False
            )

            # Apply permissions
            staff_role_ids = load_staff_roles(guild_id)
            for role_id in staff_role_ids:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    await thread.set_permissions(role, view_channel=True, send_messages=True)

            handle_embed = discord.Embed(
                title="New Ticket",
                description=f"Creator: {interaction.user.mention}\nTicket: {thread.mention}\nSetup ID: {self.setup_id}",
                color=discord.Color.blue()
            )
            handle_msg = await handle_channel.send(
                embed=handle_embed, 
                view=JoinTicketView(str(thread.id), guild_id)
            )

            # Save ticket
            save_success = save_active_ticket(
                guild_id, 
                user_id, 
                str(thread.id), 
                str(handle_msg.id), 
                self.setup_id
            )
            if not save_success:
                await thread.delete()
                return await interaction.response.send_message(
                    "❌ Failed to create ticket (database error). Please try again.", ephemeral=True
                )

            increment_user_ticket_count(guild_id, user_id)

            open_msg = setup["open_message"] or "Please describe your issue and our team will assist you shortly."
            await thread.send(
                f"Hello {interaction.user.mention}!\n{open_msg}", 
                view=CloseTicketView(guild_id)
            )
            await interaction.response.send_message(f"✅ Ticket created: {thread.mention}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating ticket: {str(e)}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self, guild_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(
        label="Close Ticket", 
        style=discord.ButtonStyle.danger, 
        emoji="🔒",
        custom_id="close_ticket_button"
    )
    async def close_confirm(self, interaction: discord.Interaction, button: Button):
        if str(interaction.guild.id) != self.guild_id:
            return await interaction.response.send_message("❌ This ticket belongs to another server!", ephemeral=True)

        if not has_event_access(interaction) and interaction.user.id != interaction.channel.owner_id:
            return await interaction.response.send_message("❌ Only staff or the ticket owner can close this!", ephemeral=True)
        await interaction.response.send_message(
            "Are you sure you want to close this ticket?", 
            view=ConfirmCloseView(self.guild_id), 
            ephemeral=True
        )

    @discord.ui.button(
        label="Close with Reason", 
        style=discord.ButtonStyle.grey, 
        emoji="📝",
        custom_id="close_with_reason_button"
    )
    async def close_with_reason(self, interaction: discord.Interaction, button: Button):
        if str(interaction.guild.id) != self.guild_id:
            return await interaction.response.send_message("❌ This ticket belongs to another server!", ephemeral=True)

        if not has_event_access(interaction):
            return await interaction.response.send_message("❌ Only staff can close with a reason!", ephemeral=True)
        await interaction.response.send_modal(CloseReasonModal(self.guild_id))

class ConfirmCloseView(View):
    def __init__(self, guild_id: str):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(
        label="Confirm Close", 
        style=discord.ButtonStyle.red,
        custom_id="confirm_close_button"
    )
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if str(interaction.guild.id) != self.guild_id:
            return await interaction.response.send_message("❌ This ticket belongs to another server!", ephemeral=True)

        thread = interaction.channel
        owner = thread.owner
        owner_id = owner.id
        guild_id = self.guild_id

        ticket_data = get_ticket_data(guild_id, owner_id)
        if not ticket_data:
            return await interaction.response.send_message("❌ Ticket data not found!", ephemeral=True)

        setup_id = ticket_data["setup_id"]
        setup = get_ticket_setup_by_id(guild_id, setup_id)
        if not setup:
            return await interaction.response.send_message("❌ Ticket setup not found!", ephemeral=True)

        # Delete staff join message
        handle_msg_id = ticket_data["handle_msg_id"]
        if handle_msg_id and setup.get("handle_channel_id"):
            try:
                handle_channel = await interaction.guild.fetch_channel(int(setup["handle_channel_id"]))
                handle_msg = await handle_channel.fetch_message(int(handle_msg_id))
                await handle_msg.delete()
                print(f"✅ Deleted staff join message (ID: {handle_msg_id})")
            except discord.NotFound:
                print(f"ℹ️ Staff join message (ID: {handle_msg_id}) already deleted")
            except Exception as e:
                print(f"❌ Error deleting staff join message: {str(e)}")

        # Generate and save transcript
        transcript = await generate_transcript(thread, closer=interaction.user)
        if setup.get("transcripts_channel_id"):
            try:
                transcripts_channel = await interaction.guild.fetch_channel(int(setup["transcripts_channel_id"]))
                if isinstance(transcripts_channel, discord.TextChannel):
                    with open(f"transcript_{thread.id}.txt", "w", encoding="utf-8") as f:
                        f.write(transcript)
                    await transcripts_channel.send(
                        f"📄 Transcript for {thread.name} (closed by {interaction.user.mention})",
                        file=discord.File(f"transcript_{thread.id}.txt")
                    )
                    os.remove(f"transcript_{thread.id}.txt")
            except Exception as e:
                await interaction.response.send_message(f"⚠️ Could not save transcript: {str(e)}", ephemeral=True)

        # Clean up
        reset_user_ticket_count(guild_id, owner_id)
        remove_active_ticket(guild_id, owner_id)

        await interaction.response.send_message("Closing ticket in 5 seconds...", ephemeral=True)
        await thread.send(f"Ticket closed by {interaction.user.mention}. Closing in 5 seconds...")

        await asyncio.sleep(5)
        await thread.delete()

    @discord.ui.button(
        label="Cancel", 
        style=discord.ButtonStyle.secondary,
        custom_id="cancel_close_button"
    )
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)

# --------------------------
# Bot Initialization and Commands
# --------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_scheduled_events = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --------------------------
# All Slash Commands with Server Isolation
# --------------------------
@bot.tree.command(name="ping", description="Check the bot's response time")
async def ping(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    # Calculate latency in milliseconds
    latency = round(bot.latency * 1000)

    # Send response with latency information
    await interaction.response.send_message(
        f"🏓 Pong! Response time: {latency}ms", 
        ephemeral=True
    )
    
@bot.tree.command(name="sendmessage", description="Send a message with optional image/file to a channel (Staff only)")
@app_commands.describe(
    channel="The channel to send the message to",
    message="Message content (can include links)",
    file="Optional: Image or file to upload (max 8MB)"
)
async def sendmessage(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str = None,
    file: discord.Attachment = None
):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    if not has_event_access(interaction):
        return await interaction.response.send_message(
            "❌ Only staff, administrators, or owners can use this command!", 
            ephemeral=True
        )

    if not message and not file:
        return await interaction.response.send_message(
            "❌ Please provide either a message, a file, or both!", 
            ephemeral=True
        )

    try:
        discord_file = None
        if file:
            if file.size > 8 * 1024 * 1024:
                return await interaction.response.send_message(
                    "❌ File too large! Max size is 8MB.", 
                    ephemeral=True
                )

            file_bytes = await file.read()
            discord_file = discord.File(fp=file_bytes, filename=file.filename)

        await channel.send(content=message, file=discord_file)
        await interaction.response.send_message(
            f"✅ Message sent to {channel.mention}", 
            ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to send message: {str(e)}", 
            ephemeral=True
        )

@bot.tree.command(name="setup_ticket", description="Set up a ticket system with unique ID (Admin only)")
@app_commands.describe(
    ticket_channel="Channel where users open tickets (button goes here)",
    handle_channel="Channel for staff to see/join active tickets",
    transcripts_channel="Channel to store ticket transcripts (leave empty for no transcripts)",
    ticket_category="Category to organize ticket threads (optional)",
    title_format="Format for ticket titles (use {username} or {userid})",
    open_message="Message shown when a ticket is opened (leave empty for default)",
    embed_title="Custom title for the ticket button embed",
    # New: Custom embed title
    embed_description="Custom description for the ticket button embed"
    # New: Custom embed description
)
async def setup_ticket(
    interaction: discord.Interaction,
    ticket_channel: discord.TextChannel,
    handle_channel: discord.TextChannel,
    transcripts_channel: discord.TextChannel = None,
    ticket_category: discord.CategoryChannel = None,
    title_format: str = "ticket-{username}",
    open_message: str = "",
    embed_title: str = "Support Tickets", 
    # Default title (can be customized)
    embed_description: str = "Click the button below to open a new support ticket"
    # Default description (can be customized)
):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)
    if not is_admin_or_owner(interaction):
        return await interaction.response.send_message("❌ Admin only!", ephemeral=True)
    # Validate title format (retain original check)
    if "{username}" not in title_format and "{userid}" not in title_format:
        return await interaction.response.send_message(
            "❌ Title format must include {username} or {userid}!", ephemeral=True)
    
    guild_id = str(interaction.guild.id)
    setup_id = uuid.uuid4().hex[:8]
    # Update config to save custom embed title/description (new fields added)
    config = {
        "id": setup_id,
        "ticket_channel_id": ticket_channel.id,
        "handle_channel_id": handle_channel.id,
        "transcripts_channel_id": transcripts_channel.id if transcripts_channel else None,
        "category_id": ticket_category.id if ticket_category else None,
        "title_format": title_format,
        "open_message": open_message,
        "embed_title": embed_title,  # New: Save custom embed title
        "embed_description": embed_description,  # New: Save custom embed description
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Load, update, and save ticket configs (retain original logic)
    all_configs = load_ticket_configs(guild_id)
    all_configs.append(config)
    save_ticket_configs(guild_id, all_configs)
    
    # Send embed with CUSTOM title/description (core change from original fixed text)
    embed = discord.Embed(
        title=embed_title,  # Use user's custom title
        description=embed_description,  # Use user's custom description (no extra content)
        color=discord.Color.green()
    )
    await ticket_channel.send(embed=embed, view=TicketOpenButton(setup_id, guild_id))
    
    # Update response to show custom embed settings (for admin verification)
    response = f"✅ Ticket system set up with ID: `{setup_id}`\n"
    response += f"- Ticket channel: {ticket_channel.mention}\n"
    response += f"- Handle channel: {handle_channel.mention}\n"
    response += f"- Transcripts channel: {transcripts_channel.mention if transcripts_channel else 'None'}\n"
    response += f"- Embed Title: {embed_title}\n"  # Show custom title
    response += f"- Embed Description: {embed_description}"  # Show custom description
    await interaction.response.send_message(response, ephemeral=True)

@bot.tree.command(name="delticketsetup", description="Delete a ticket setup by ID (Admin only)")
@app_commands.describe(setup_id="ID of the ticket setup to delete (from /list_ticket_setups)")
async def delticketsetup(interaction: discord.Interaction, setup_id: str):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    if not is_admin_or_owner(interaction):
        return await interaction.response.send_message("❌ Admin only!", ephemeral=True)

    guild_id = str(interaction.guild.id)
    all_configs = load_ticket_configs(guild_id)
    setup = get_ticket_setup_by_id(guild_id, setup_id)

    if not setup:
        return await interaction.response.send_message(
            f"❌ No ticket setup found with ID: `{setup_id}` in this server", ephemeral=True
        )

    updated_configs = [c for c in all_configs if c['id'] != setup_id]
    save_ticket_configs(guild_id, updated_configs)

    await interaction.response.send_message(
        f"✅ Ticket setup `{setup_id}` has been deleted from this server", ephemeral=True
    )

@bot.tree.command(name="create_ticket_panel", description="Create an interactive multi-ticket panel")
@app_commands.describe(channel="Channel where the ticket panel will be created")
async def create_ticket_panel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.guild:
        await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)
        return
    if not is_admin_or_owner(interaction):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return

    # 打开面板创建模态
    modal = TicketPanelModal(channel)
    await interaction.response.send_modal(modal)

@bot.tree.command(name="list_ticket_setups", description="List all ticket setups for this server (Admin only)")
async def list_ticket_setups(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    if not is_admin_or_owner(interaction):
        return await interaction.response.send_message("❌ Admin only!", ephemeral=True)

    guild_id = str(interaction.guild.id)
    setups = load_ticket_configs(guild_id)
    if not setups:
        return await interaction.response.send_message("ℹ️ No ticket setups found for this server", ephemeral=True)

    response = "📋 Current ticket setups:\n"
    for setup in setups:
        ticket_channel = interaction.guild.get_channel(int(setup["ticket_channel_id"]))
        response += f"- ID: `{setup['id']}`\n"
        response += f"  Ticket Channel: {ticket_channel.mention if ticket_channel else 'Unknown'}\n"
        response += f"  Created: {datetime.fromisoformat(setup['created_at']).strftime('%Y-%m-%d')}\n"

    await interaction.response.send_message(response, ephemeral=True)

@bot.tree.command(name="set_timezone", description="Set your timezone (e.g., UTC+3)")
@app_commands.describe(timezone="Your timezone in UTC±X format")
async def set_timezone(interaction: discord.Interaction, timezone: str):
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

@bot.tree.command(name="addstaffrole", description="Add a role to the staff list (Admin/Owner only)")
@app_commands.describe(role="The role to add as staff (ping the role)")
async def addstaffrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    if not is_admin_or_owner(interaction):
        return await interaction.response.send_message(
            "❌ Only server owners or administrators can use this command!", ephemeral=True)

    guild_id = str(interaction.guild.id)
    current_staff = load_staff_roles(guild_id)
    role_id = str(role.id)

    if role_id in current_staff:
        return await interaction.response.send_message(
            f"❌ Role **{role.name}** is already a staff role!", ephemeral=True)

    current_staff.append(role_id)
    save_staff_roles(guild_id, current_staff)

    await interaction.response.send_message(
        f"✅ Added **{role.name}** to the staff list.", ephemeral=True)

@bot.tree.command(name="delstaffrole", description="Remove a role from the staff list (Admin/Owner only)")
@app_commands.describe(role="The role to remove from staff (ping the role)")
async def delstaffrole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    if not is_admin_or_owner(interaction):
        return await interaction.response.send_message(
            "❌ Only server owners or administrators can use this command!", ephemeral=True)

    guild_id = str(interaction.guild.id)
    current_staff = load_staff_roles(guild_id)
    role_id = str(role.id)

    if role_id not in current_staff:
        return await interaction.response.send_message(
            f"❌ Role **{role.name}** is not a staff role!", ephemeral=True)

    current_staff.remove(role_id)
    save_staff_roles(guild_id, current_staff)

    await interaction.response.send_message(
        f"✅ Removed **{role.name}** from the staff list.", ephemeral=True)

@bot.tree.command(name="getstaffrole", description="List all current staff roles")
async def getstaffrole(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    guild_id = str(interaction.guild.id)
    staff_role_ids = load_staff_roles(guild_id)

    if not staff_role_ids:
        return await interaction.response.send_message(
            "ℹ️ No staff roles have been set up yet.", ephemeral=True)

    staff_roles = []
    for role_id in staff_role_ids:
        role = interaction.guild.get_role(int(role_id))
        if role:
            staff_roles.append(f"• {role.mention}")

    await interaction.response.send_message(
        "📋 Current staff roles:\n" + "\n".join(staff_roles), ephemeral=True)

@bot.tree.command(name="create_event", description="Create an event (Staff, Admin, or Owner only)")
@app_commands.describe(
    name="Event name",
    description="Event description",
    local_time="Time (YYYY-MM-DD HH:MM)",
    location="Event location"
)
async def create_event(interaction: discord.Interaction, name: str, description: str, local_time: str, location: str):
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

        try:
            local_start = user_timezone.localize(datetime.strptime(local_time, "%Y-%m-%d %H:%M"))
        except ValueError:
            return await interaction.response.send_message(
                "❌ Use time format: YYYY-MM-DD HH:MM", ephemeral=True)

        now_local = datetime.now(user_timezone)
        if local_start < now_local:
            return await interaction.response.send_message(
                "❌ Can't create past events", ephemeral=True)
        if local_start < now_local + timedelta(minutes=30):
            return await interaction.response.send_message(
                "❌ Events need 30+ minutes lead time", ephemeral=True)

        local_end = local_start + timedelta(minutes=90)
        utc_start = local_start.astimezone(pytz.UTC)
        utc_end = local_end.astimezone(pytz.UTC)

        event = await interaction.guild.create_scheduled_event(
            name=name,
            description=description,
            start_time=utc_start,
            end_time=utc_end,
            location=location,
            privacy_level=discord.PrivacyLevel.guild_only,
            entity_type=discord.EntityType.external
        )

        await interaction.response.send_message(
            f"✅ Event created! ID: `{event.id}`", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"❌ Error creating event: {str(e)}", ephemeral=True)

@bot.tree.command(name="list_events", description="List all upcoming events")
async def list_events(interaction: discord.Interaction):
    """全新的列表事件命令"""
    try:
        print(f"📅 List events called by {interaction.user.name}")
        
        # 立即响应防止超时
        await interaction.response.defer(ephemeral=True)
        
        if not interaction.guild:
            await interaction.followup.send("❌ Server only command!")
            return

        # 获取事件
        try:
            events = await interaction.guild.fetch_scheduled_events()
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to fetch events: {e}")
            return

        if not events:
            await interaction.followup.send("📭 No events found")
            return

        # 发送结果
        event_list = []
        for event in events:
            event_list.append(f"**{event.name}** (ID: `{event.id}`) - {event.start_time.strftime('%m/%d %H:%M')}")
        
        response = "\n".join(event_list)
        await interaction.followup.send(response)
        print(f"✅ Listed {len(events)} events")

    except Exception as e:
        print(f"❌ list_events error: {e}")
        try:
            await interaction.followup.send("❌ Command failed")
        except:
            pass

@bot.tree.command(name="delete_event", description="Delete an event")
@app_commands.describe(event_id="Event ID to delete")
async def delete_event(interaction: discord.Interaction, event_id: str):
    """全新的事件删除命令"""
    try:
        print(f"🗑️ Delete event called: {event_id} by {interaction.user.name}")
        
        # 立即响应
        await interaction.response.defer(ephemeral=True)
        
        if not interaction.guild:
            await interaction.followup.send("❌ Server only command!")
            return

        # 验证权限
        if not has_event_access(interaction):
            await interaction.followup.send("❌ Permission denied!")
            return

        # 查找事件
        try:
            event = await interaction.guild.fetch_scheduled_event(int(event_id))
        except:
            await interaction.followup.send("❌ Event not found!")
            return

        # 删除事件
        try:
            await event.delete()
            await interaction.followup.send(f"✅ Deleted event: {event.name}")
            print(f"✅ Event deleted: {event.name}")
        except Exception as e:
            await interaction.followup.send(f"❌ Delete failed: {e}")

    except Exception as e:
        print(f"❌ delete_event error: {e}")
        try:
            await interaction.followup.send("❌ Command failed")
        except:
            pass

# Helper command to debug events
@bot.tree.command(name="event_info", description="Get detailed information about an event")
@app_commands.describe(event_id="The ID of the event to inspect")
async def event_info(interaction: discord.Interaction, event_id: str):
    """Get detailed information about a specific event"""
    try:
        if not interaction.guild:
            await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
            return

        try:
            event_id_int = int(event_id.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid event ID format.", ephemeral=True)
            return

        try:
            event = await interaction.guild.fetch_scheduled_event(event_id_int)
            
            embed = discord.Embed(
                title=f"📊 Event Info: {event.name}",
                color=discord.Color.gold()
            )
            embed.add_field(name="ID", value=f"`{event.id}`", inline=True)
            embed.add_field(name="Status", value=str(event.status).split('.')[-1], inline=True)
            embed.add_field(name="Type", value=str(event.entity_type).split('.')[-1], inline=True)
            embed.add_field(name="Start Time", value=event.start_time.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
            embed.add_field(name="End Time", value=event.end_time.strftime("%Y-%m-%d %H:%M UTC"), inline=True)
            embed.add_field(name="Location", value=event.location or "Not specified", inline=True)
            embed.add_field(name="Creator", value=f"<@{event.creator_id}>" if event.creator_id else "Unknown", inline=True)
            embed.add_field(name="Subscribers", value=str(event.subscriber_count), inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.NotFound:
            await interaction.response.send_message("❌ Event not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ No permission to view events.", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="bot_status", description="Check if bot is online and working")
async def bot_status(interaction: discord.Interaction):
    """简单的机器人状态检查"""
    try:
        # 计算运行时间
        uptime = datetime.now() - bot.start_time
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # 创建状态消息
        status_message = (
            "🤖 **Bot Status**\n"
            f"• **Status**: ✅ Online\n"
            f"• **Username**: {bot.user.name}\n"
            f"• **Ping**: {round(bot.latency * 1000)}ms\n"
            f"• **Uptime**: {uptime_str}\n"
            f"• **Servers**: {len(bot.guilds)}\n"
            f"• **Commands**: {len(bot.tree.get_commands())} loaded\n"
            "\n"
            "🟢 **All systems operational**"
        )
        
        await interaction.response.send_message(status_message, ephemeral=True)
        print(f"✅ Status checked by {interaction.user.name}")
        
    except Exception as e:
        # 简化错误处理
        error_message = "❌ Failed to check status"
        try:
            await interaction.response.send_message(error_message, ephemeral=True)
        except:
            # 如果响应失败，尝试发送普通消息
            try:
                await interaction.channel.send(f"{interaction.user.mention} {error_message}", delete_after=10)
            except:
                pass
        print(f"❌ Status command error: {e}")

@bot.tree.command(name="debug_commands", description="Check if commands are registered")
async def debug_commands(interaction: discord.Interaction):
    """检查所有命令的注册状态"""
    try:
        # 获取所有已注册的命令
        all_commands = bot.tree.get_commands()
        registered_names = [cmd.name for cmd in all_commands]
        
        embed = discord.Embed(
            title="🔧 Command Debug Info",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Registered Commands", 
            value="\n".join([f"• /{name}" for name in registered_names]) or "None",
            inline=False
        )
        embed.add_field(
            name="Guild Info",
            value=f"Server: {interaction.guild.name}\n"
                  f"ID: {interaction.guild.id}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Debug error: {str(e)}", ephemeral=True)

@bot.tree.command(name="get_ticket_count", description="Check how many tickets a user has open")
@app_commands.describe(user="The user to check (defaults to yourself)")
async def get_ticket_count(interaction: discord.Interaction, user: discord.User = None):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

    target_user = user or interaction.user
    guild_id = str(interaction.guild.id)
    counts = load_user_ticket_counts(guild_id)
    count = counts.get(str(target_user.id), 0)
    await interaction.response.send_message(
        f"📊 {target_user.mention} has {count} active ticket(s) open in this server.", 
        ephemeral=True
    )

# --------------------------
# Bot Events
# --------------------------
@bot.event
async def on_ready():
    # 记录启动时间
    bot.start_time = datetime.now()
    
    print(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f'🔗 Connected to {len(bot.guilds)} server(s)')
    
    # 简化的同步
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"⚠️ Sync note: {e}")
    # Register views for all servers and setups
    for guild in bot.guilds:
        guild_id = str(guild.id)
        setups = load_ticket_configs(guild_id)
        for setup in setups:
            bot.add_view(TicketOpenButton(setup['id'], guild_id))
            bot.add_view(CloseTicketView(guild_id))
            bot.add_view(ConfirmCloseView(guild_id))
            bot.add_view(JoinTicketView("", guild_id))

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s) across all servers")
    except Exception as e:
        print(f"❌ Command sync failed: {e}")

# 命令执行跟踪
command_usage = {}

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """监控所有交互"""
    if interaction.type == discord.InteractionType.application_command:
        command_name = interaction.data.get('name', 'unknown')
        command_usage[command_name] = command_usage.get(command_name, 0) + 1
        print(f"⚡ Command executed: /{command_name} by {interaction.user.name}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandNotFound):
        print(f"❌ Command not found: {interaction.command_name}")
        await interaction.response.send_message(
            "❌ Command not synced yet. Please wait or restart bot.",
            ephemeral=True
        )
    else:
        print(f"❌ Command error: {error}")

@bot.tree.command(name="test_response", description="Test response mechanisms")
async def test_response(interaction: discord.Interaction):
    """测试所有响应方式"""
    try:
        print(f"🧪 Testing response for user: {interaction.user.name}")
        
        # 测试立即响应
        await interaction.response.send_message("✅ Immediate response received!", ephemeral=True)
        print("✅ Immediate response sent")
        
        # 测试延迟响应
        await asyncio.sleep(1)
        await interaction.followup.send("✅ Follow-up message also works!", ephemeral=True)
        print("✅ Follow-up sent")
        
    except Exception as e:
        print(f"❌ Response test failed: {e}")
        # 尝试原始消息发送作为备用
        try:
            await interaction.channel.send("❌ Response failed, but bot is alive!")
        except:
            pass

# --------------------------
# Run Bot
# --------------------------
keep_alive()
try:
    bot.run(TOKEN)
except discord.LoginFailure:
    print("❌ Invalid token! Check your .env file")
except Exception as e:
    print(f"❌ Critical error: {str(e)}")
