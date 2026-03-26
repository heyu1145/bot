import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
import asyncio

from config.config import MESSAGE_CONFIG
from utils.storage import (
    load_ticket_configs, load_multi_ticket_configs, load_active_tickets,
    load_user_ticket_counts, load_staff_roles, load_user_timezones,
    save_json_data, backup_server_data,
    export_all_server_data, import_all_server_data,
    load_all_ticket_configs, load_all_multi_ticket_configs,
    load_all_active_tickets, load_all_user_ticket_counts,
    load_all_staff_roles, load_all_user_timezones,
    get_all_servers_data, data_manager
)
from utils.permissions import has_data_access

class DataManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="export_data", description="Export server data as JSON files")
    @app_commands.describe(data_type="Type of data to export")
    @app_commands.choices(data_type=[
        app_commands.Choice(name="📦 All Data", value="all"),
        app_commands.Choice(name="🎫 Ticket Configs", value="ticket_configs"),
        app_commands.Choice(name="🔄 Multi-Ticket Configs", value="multi_ticket_configs"),
        app_commands.Choice(name="📋 Active Tickets", value="active_tickets"),
        app_commands.Choice(name="👤 User Ticket Counts", value="user_ticket_counts"),
        app_commands.Choice(name="🛡️ Staff Roles", value="staff_roles"),
        app_commands.Choice(name="🌐 User Timezones", value="user_timezones")
    ])
    async def export_data(self, interaction: discord.Interaction, data_type: app_commands.Choice[str]):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            guild_id = str(interaction.guild.id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            files = []
            
            if data_type.value == "all" or data_type.value == "ticket_configs":
                data = load_ticket_configs(guild_id)
                filename = f"ticket_configs_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "multi_ticket_configs":
                data = load_multi_ticket_configs(guild_id)
                filename = f"multi_ticket_configs_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "active_tickets":
                data:Dict[str, Any] = load_active_tickets(guild_id)
                filename = f"active_tickets_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "user_ticket_counts":
                data:Dict[str, int] = load_user_ticket_counts(guild_id)
                filename = f"user_ticket_counts_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "staff_roles":
                data:List[str] = load_staff_roles(guild_id)
                filename = f"staff_roles_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "user_timezones":
                data:Dict[str, str] = load_user_timezones(guild_id)
                filename = f"user_timezones_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if files:
                await interaction.followup.send(
                    f"✅ Exported {data_type.name} for server {interaction.guild.name}",
                    files=files,
                    ephemeral=True
                )
                
                for file in files:
                    try:
                        os.remove(file.filename)
                    except:
                        pass
            else:
                await interaction.followup.send("❌ No data to export.", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error exporting data: {str(e)}", ephemeral=True)

    @app_commands.command(name="import_data", description="Import data from JSON files")
    @app_commands.describe(
        json_file="JSON file to import",
        data_type="Type of data being imported"
    )
    @app_commands.choices(data_type=[
        app_commands.Choice(name="🎫 Ticket Configs", value="ticket_configs"),
        app_commands.Choice(name="🔄 Multi-Ticket Configs", value="multi_ticket_configs"),
        app_commands.Choice(name="📋 Active Tickets", value="active_tickets"),
        app_commands.Choice(name="👤 User Ticket Counts", value="user_ticket_counts"),
        app_commands.Choice(name="🛡️ Staff Roles", value="staff_roles"),
        app_commands.Choice(name="🌐 User Timezones", value="user_timezones")
    ])
    async def import_data(self, interaction: discord.Interaction, json_file: discord.Attachment, data_type: app_commands.Choice[str]):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            # Enhanced security: Check file extension and content type
            if not json_file.filename.endswith('.json'):
                return await interaction.response.send_message("❌ Please upload a JSON file!", ephemeral=True)
            
            # Check file size (limit to 10MB for security)
            if json_file.size > 10 * 1024 * 1024:  # 10MB
                return await interaction.response.send_message("❌ File too large! Maximum 10MB allowed.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            content = await json_file.read()
            
            # Additional security: Check for potential code injection
            content_str = content.decode('utf-8')
            if any(pattern in content_str for pattern in ['__import__', 'exec', 'eval', 'os.', 'subprocess']):
                return await interaction.followup.send("❌ Suspicious content detected in JSON file!", ephemeral=True)
            
            data = json.loads(content_str)
            guild_id = str(interaction.guild.id)
            
            # Additional validation for each data type
            if data_type.value == "ticket_configs":
                if not isinstance(data, list):
                    return await interaction.followup.send("❌ Invalid format for ticket configs! Expected array.", ephemeral=True)
                # Validate each ticket config item
                for item in data:
                    if not isinstance(item, dict) or not all(key in item for key in ['id', 'ticket_channel_id', 'handle_channel_id']):
                        return await interaction.followup.send("❌ Invalid ticket config format!", ephemeral=True)
                save_json_data(guild_id, "ticket_configs.json", data)
                await interaction.followup.send("✅ Ticket configs imported successfully!", ephemeral=True)
            
            elif data_type.value == "multi_ticket_configs":
                if not isinstance(data, list):
                    return await interaction.followup.send("❌ Invalid format for multi-ticket configs! Expected array.", ephemeral=True)
                # Validate each multi-ticket config item
                for item in data:
                    if not isinstance(item, dict) or 'ticket_options' not in item:
                        return await interaction.followup.send("❌ Invalid multi-ticket config format!", ephemeral=True)
                save_json_data(guild_id, "multi_ticket_configs.json", data)
                await interaction.followup.send("✅ Multi-ticket configs imported successfully!", ephemeral=True)
            
            elif data_type.value == "active_tickets":
                if not isinstance(data, dict):
                    return await interaction.followup.send("❌ Invalid format for active tickets! Expected object.", ephemeral=True)
                # Validate ticket data structure
                for ticket_id, ticket_data in data.items():
                    if not isinstance(ticket_data, dict) or not isinstance(ticket_id, str):
                        return await interaction.followup.send("❌ Invalid active tickets format!", ephemeral=True)
                save_json_data(guild_id, "active_tickets.json", data)
                await interaction.followup.send("✅ Active tickets imported successfully!", ephemeral=True)
            
            elif data_type.value == "user_ticket_counts":
                if not isinstance(data, dict):
                    return await interaction.followup.send("❌ Invalid format for user ticket counts! Expected object.", ephemeral=True)
                # Validate that all keys are strings and values are integers
                for user_id, count in data.items():
                    if not isinstance(user_id, str) or not isinstance(count, int):
                        return await interaction.followup.send("❌ Invalid user ticket counts format!", ephemeral=True)
                save_json_data(guild_id, "user_ticket_counts.json", data)
                await interaction.followup.send("✅ User ticket counts imported successfully!", ephemeral=True)
            
            elif data_type.value == "staff_roles":
                if not isinstance(data, list):
                    return await interaction.followup.send("❌ Invalid format for staff roles! Expected array.", ephemeral=True)
                # Validate that all items are strings
                for role_id in data:
                    if not isinstance(role_id, str):
                        return await interaction.followup.send("❌ Invalid staff roles format!", ephemeral=True)
                save_json_data(guild_id, "staff_roles.json", data)
                await interaction.followup.send("✅ Staff roles imported successfully!", ephemeral=True)
            
            elif data_type.value == "user_timezones":
                if not isinstance(data, dict):
                    return await interaction.followup.send("❌ Invalid format for user timezones! Expected object.", ephemeral=True)
                # Validate that all keys are strings and values are strings
                for user_id, timezone in data.items():
                    if not isinstance(user_id, str) or not isinstance(timezone, str):
                        return await interaction.followup.send("❌ Invalid user timezones format!", ephemeral=True)
                save_json_data(guild_id, "user_timezones.json", data)
                await interaction.followup.send("✅ User timezones imported successfully!", ephemeral=True)
            
        except json.JSONDecodeError:
            await interaction.followup.send("❌ Invalid JSON file format!", ephemeral=True)
        except UnicodeDecodeError:
            await interaction.followup.send("❌ Invalid file encoding! Please use UTF-8.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error importing data: {str(e)}", ephemeral=True)

    @app_commands.command(name="view_data_stats", description="View server data statistics")
    async def view_data_stats(self, interaction: discord.Interaction):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            guild_id = str(interaction.guild.id)
            ticket_configs = load_ticket_configs(guild_id)
            multi_configs = load_multi_ticket_configs(guild_id)
            active_tickets = load_active_tickets(guild_id)
            user_counts = load_user_ticket_counts(guild_id)
            staff_roles = load_staff_roles(guild_id)
            timezones = load_user_timezones(guild_id)
            
            total_tickets = sum(user_counts.values()) if user_counts else 0
            
            embed = discord.Embed(
                title="📊 Server Data Statistics",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="🎫 Ticket Configs", value=f"Count: {len(ticket_configs)}", inline=True)
            embed.add_field(name="🔄 Multi-Ticket Panels", value=f"Count: {len(multi_configs)}", inline=True)
            embed.add_field(name="📋 Active Tickets", value=f"Count: {len(active_tickets)}", inline=True)
            embed.add_field(name="👤 User Ticket Counts", value=f"Users: {len(user_counts)}\nTotal: {total_tickets}", inline=True)
            embed.add_field(name="🛡️ Staff Roles", value=f"Count: {len(staff_roles)}", inline=True)
            embed.add_field(name="🌐 User Timezones", value=f"Count: {len(timezones)}", inline=True)
            
            embed.set_footer(text=f"Server ID: {guild_id}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error loading data: {str(e)}", ephemeral=True)

    @app_commands.command(name="clear_data", description="Clear specific server data (DANGEROUS)")
    @app_commands.describe(data_type="Type of data to clear")
    @app_commands.choices(data_type=[
        app_commands.Choice(name="📋 Active Tickets", value="active_tickets"),
        app_commands.Choice(name="👤 User Ticket Counts", value="user_ticket_counts"),
        app_commands.Choice(name="🌐 User Timezones", value="user_timezones")
    ])
    async def clear_data(self, interaction: discord.Interaction, data_type: app_commands.Choice[str]):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            guild_id = str(interaction.guild.id)
            
            if data_type.value == "active_tickets":
                save_json_data(guild_id, "active_tickets.json", {})
                await interaction.response.send_message("✅ Active tickets cleared successfully!", ephemeral=True)
            
            elif data_type.value == "user_ticket_counts":
                save_json_data(guild_id, "user_ticket_counts.json", {})
                await interaction.response.send_message("✅ User ticket counts cleared successfully!", ephemeral=True)
            
            elif data_type.value == "user_timezones":
                save_json_data(guild_id, "user_timezones.json", {})
                await interaction.response.send_message("✅ User timezones cleared successfully!", ephemeral=True)
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Error clearing data: {str(e)}", ephemeral=True)

    @app_commands.command(name="backup_data", description="Create a backup of all server data")
    async def backup_data(self, interaction: discord.Interaction):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            success = True
            for server_id in get_all_servers_data():
                if not backup_server_data(server_id):
                    success = False
            
            if success:
                await interaction.followup.send("✅ All server data backup created successfully!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Some backups failed. Check logs for details.", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error during backup: {str(e)}", ephemeral=True)

    @app_commands.command(name="export_all_data", description="Export ALL server data as a single JSON file")
    async def export_all_data(self, interaction: discord.Interaction):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            all_data = export_all_server_data()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_servers_data_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            file = discord.File(filename)
            await interaction.followup.send(
                f"✅ Exported data from {all_data['total_servers']} servers",
                file=file,
                ephemeral=True
            )
            
            os.remove(filename)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error exporting all server data: {str(e)}", ephemeral=True)

    @app_commands.command(name="import_all_data", description="Import data to ALL servers from JSON file")
    @app_commands.describe(json_file="JSON file containing all server data")
    async def import_all_data(self, interaction: discord.Interaction, json_file: discord.Attachment):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            if not json_file.filename.endswith('.json'):
                return await interaction.response.send_message("❌ Please upload a JSON file!", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            content = await json_file.read()
            data = json.loads(content.decode('utf-8'))
            
            success = import_all_server_data(data)
            
            if success:
                await interaction.followup.send("✅ All server data imported successfully!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Error importing data to some servers. Check logs for details.", ephemeral=True)
                
        except json.JSONDecodeError:
            await interaction.followup.send("❌ Invalid JSON file format!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error importing all server data: {str(e)}", ephemeral=True)

    @app_commands.command(name="view_all_data_stats", description="View statistics for ALL servers")
    async def view_all_data_stats(self, interaction: discord.Interaction):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            all_servers = get_all_servers_data()
            ticket_configs = load_all_ticket_configs()
            multi_configs = load_all_multi_ticket_configs()
            active_tickets = load_all_active_tickets()
            user_counts = load_all_user_ticket_counts()
            staff_roles = load_all_staff_roles()
            timezones = load_all_user_timezones()
            
            total_ticket_configs = sum(len(configs) for configs in ticket_configs.values())
            total_multi_configs = sum(len(configs) for configs in multi_configs.values())
            total_active_tickets = sum(len(tickets) for tickets in active_tickets.values())
            total_user_counts = sum(len(counts) for counts in user_counts.values())
            total_tickets_created = sum(sum(counts.values()) for counts in user_counts.values())
            total_staff_roles = sum(len(roles) for roles in staff_roles.values())
            total_timezones = sum(len(tz) for tz in timezones.values())
            
            embed = discord.Embed(
                title="📊 All Servers Data Statistics",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="🏰 Total Servers", value=str(len(all_servers)), inline=True)
            embed.add_field(name="🎫 Ticket Configs", value=f"{total_ticket_configs} across all servers", inline=True)
            embed.add_field(name="🔄 Multi-Ticket Panels", value=f"{total_multi_configs} across all servers", inline=True)
            embed.add_field(name="📋 Active Tickets", value=f"{total_active_tickets} across all servers", inline=True)
            embed.add_field(name="👤 User Ticket Counts", value=f"{total_user_counts} users\n{total_tickets_created} total tickets", inline=True)
            embed.add_field(name="🛡️ Staff Roles", value=f"{total_staff_roles} across all servers", inline=True)
            embed.add_field(name="🌐 User Timezones", value=f"{total_timezones} across all servers", inline=True)
            
            if all_servers:
                server_list = "\n".join([f"• Server `{server_id}`" for server_id in all_servers[:5]])
                if len(all_servers) > 5:
                    server_list += f"\n• ... and {len(all_servers) - 5} more"
                embed.add_field(name="📋 Servers", value=server_list, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error loading all server data: {str(e)}", ephemeral=True)

    @app_commands.command(name="clear_all_data", description="Clear specific data from ALL servers (DANGEROUS)")
    @app_commands.describe(data_type="Type of data to clear")
    @app_commands.choices(data_type=[
        app_commands.Choice(name="📋 Active Tickets", value="active_tickets"),
        app_commands.Choice(name="👤 User Ticket Counts", value="user_ticket_counts"),
        app_commands.Choice(name="🌐 User Timezones", value="user_timezones")
    ])
    async def clear_all_data(self, interaction: discord.Interaction, data_type: app_commands.Choice[str]):
        try:
            if not has_data_access(interaction):
                return await interaction.response.send_message("❌ Access denied.", ephemeral=True)
            
            await interaction.response.defer(ephemeral=True, thinking=True)
            
            cleared_servers = 0
            for server_id in get_all_servers_data():
                if data_type.value == "active_tickets":
                    save_json_data(server_id, "active_tickets.json", {})
                elif data_type.value == "user_ticket_counts":
                    save_json_data(server_id, "user_ticket_counts.json", {})
                elif data_type.value == "user_timezones":
                    save_json_data(server_id, "user_timezones.json", {})
                cleared_servers += 1
            
            await interaction.followup.send(f"✅ Cleared {data_type.name} from {cleared_servers} servers!", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Error clearing data: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DataManagement(bot))
