import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime, timezone
from typing import List

from utils.storage import (
    load_ticket_configs, load_multi_ticket_configs, load_active_tickets,
    load_user_ticket_counts, load_staff_roles, load_user_timezones,
    save_json_data, backup_server_data
)
from utils.permissions import has_data_access

class DataManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="backup_data", description="Create a backup of all server data")
    async def backup_data(self, interaction: discord.Interaction):
        if not has_data_access(interaction):
            return await interaction.response.send_message("❌ Access denied. Trusted users only.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild.id)
        success = backup_server_data(guild_id)
        
        if success:
            await interaction.followup.send("✅ Server data backup created successfully!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to create backup. Check logs for details.", ephemeral=True)

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
        if not has_data_access(interaction):
            return await interaction.response.send_message("❌ Access denied. Trusted users only.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files = []
        
        try:
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
                data = load_active_tickets(guild_id)
                filename = f"active_tickets_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "user_ticket_counts":
                data = load_user_ticket_counts(guild_id)
                filename = f"user_ticket_counts_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "staff_roles":
                data = load_staff_roles(guild_id)
                filename = f"staff_roles_{timestamp}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                files.append(discord.File(filename))
            
            if data_type.value == "all" or data_type.value == "user_timezones":
                data = load_user_timezones(guild_id)
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
                
                # Clean up temporary files
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
        if not has_data_access(interaction):
            return await interaction.response.send_message("❌ Access denied. Trusted users only.", ephemeral=True)
        
        if not json_file.filename.endswith('.json'):
            return await interaction.response.send_message("❌ Please upload a JSON file!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            content = await json_file.read()
            data = json.loads(content.decode('utf-8'))
            guild_id = str(interaction.guild.id)
            
            if data_type.value == "ticket_configs":
                if not isinstance(data, list):
                    return await interaction.followup.send("❌ Invalid format for ticket configs! Expected array.", ephemeral=True)
                save_json_data(guild_id, "ticket_configs.json", data)
                await interaction.followup.send("✅ Ticket configs imported successfully!", ephemeral=True)
            
            elif data_type.value == "multi_ticket_configs":
                if not isinstance(data, list):
                    return await interaction.followup.send("❌ Invalid format for multi-ticket configs! Expected array.", ephemeral=True)
                save_json_data(guild_id, "multi_ticket_configs.json", data)
                await interaction.followup.send("✅ Multi-ticket configs imported successfully!", ephemeral=True)
            
            elif data_type.value == "active_tickets":
                if not isinstance(data, dict):
                    return await interaction.followup.send("❌ Invalid format for active tickets! Expected object.", ephemeral=True)
                save_json_data(guild_id, "active_tickets.json", data)
                await interaction.followup.send("✅ Active tickets imported successfully!", ephemeral=True)
            
            elif data_type.value == "user_ticket_counts":
                if not isinstance(data, dict):
                    return await interaction.followup.send("❌ Invalid format for user ticket counts! Expected object.", ephemeral=True)
                save_json_data(guild_id, "user_ticket_counts.json", data)
                await interaction.followup.send("✅ User ticket counts imported successfully!", ephemeral=True)
            
            elif data_type.value == "staff_roles":
                if not isinstance(data, list):
                    return await interaction.followup.send("❌ Invalid format for staff roles! Expected array.", ephemeral=True)
                save_json_data(guild_id, "staff_roles.json", data)
                await interaction.followup.send("✅ Staff roles imported successfully!", ephemeral=True)
            
            elif data_type.value == "user_timezones":
                if not isinstance(data, dict):
                    return await interaction.followup.send("❌ Invalid format for user timezones! Expected object.", ephemeral=True)
                save_json_data(guild_id, "user_timezones.json", data)
                await interaction.followup.send("✅ User timezones imported successfully!", ephemeral=True)
            
        except json.JSONDecodeError:
            await interaction.followup.send("❌ Invalid JSON file format!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error importing data: {str(e)}", ephemeral=True)

    @app_commands.command(name="view_data_stats", description="View server data statistics")
    async def view_data_stats(self, interaction: discord.Interaction):
        if not has_data_access(interaction):
            return await interaction.response.send_message("❌ Access denied. Trusted users only.", ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        
        embed = discord.Embed(
            title="📊 Server Data Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        try:
            ticket_configs = load_ticket_configs(guild_id)
            multi_configs = load_multi_ticket_configs(guild_id)
            active_tickets = load_active_tickets(guild_id)
            user_counts = load_user_ticket_counts(guild_id)
            staff_roles = load_staff_roles(guild_id)
            timezones = load_user_timezones(guild_id)
            
            total_tickets = sum(user_counts.values())
            
            embed.add_field(name="🎫 Ticket Configs", value=f"Count: {len(ticket_configs)}", inline=True)
            embed.add_field(name="🔄 Multi-Ticket Panels", value=f"Count: {len(multi_configs)}", inline=True)
            embed.add_field(name="📋 Active Tickets", value=f"Count: {len(active_tickets)}", inline=True)
            embed.add_field(name="👤 User Ticket Counts", value=f"Users: {len(user_counts)}\nTotal: {total_tickets}", inline=True)
            embed.add_field(name="🛡️ Staff Roles", value=f"Count: {len(staff_roles)}", inline=True)
            embed.add_field(name="🌐 User Timezones", value=f"Count: {len(timezones)}", inline=True)
            
            embed.set_footer(text=f"Server ID: {guild_id}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error loading data: {str(e)}", ephemeral=True)

    @app_commands.command(name="clear_data", description="Clear specific server data (DANGEROUS)")
    @app_commands.describe(data_type="Type of data to clear")
    @app_commands.choices(data_type=[
        app_commands.Choice(name="📋 Active Tickets", value="active_tickets"),
        app_commands.Choice(name="👤 User Ticket Counts", value="user_ticket_counts"),
        app_commands.Choice(name="🌐 User Timezones", value="user_timezones")
    ])
    async def clear_data(self, interaction: discord.Interaction, data_type: app_commands.Choice[str]):
        if not has_data_access(interaction):
            return await interaction.response.send_message("❌ Access denied. Trusted users only.", ephemeral=True)
        
        guild_id = str(interaction.guild.id)
        
        try:
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

async def setup(bot):
    await bot.add_cog(DataManagement(bot))