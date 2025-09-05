import discord
from discord import app_commands
from discord.ext import commands
from typing import List

from utils.storage import load_trusted_users, save_trusted_users, is_bot_owner
from utils.permissions import is_admin_or_owner, has_event_access
from utils.storage import load_staff_roles, save_staff_roles

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_trusted_user", description="Add a user to trusted list (Bot Owner Only)")
    @app_commands.describe(user="The user to add as trusted")
    async def add_trusted_user(self, interaction: discord.Interaction, user: discord.User):
        if not is_bot_owner(interaction.user.id):
            return await interaction.response.send_message("❌ Only the bot owner can use this command!", ephemeral=True)
        
        trusted_users = load_trusted_users()
        if user.id in trusted_users:
            return await interaction.response.send_message(f"❌ {user.mention} is already trusted!", ephemeral=True)
        
        trusted_users.append(user.id)
        save_trusted_users(trusted_users)
        await interaction.response.send_message(f"✅ Added {user.mention} to trusted users!", ephemeral=True)

    @app_commands.command(name="remove_trusted_user", description="Remove a user from trusted list (Bot Owner Only)")
    @app_commands.describe(user="The user to remove from trusted")
    async def remove_trusted_user(self, interaction: discord.Interaction, user: discord.User):
        if not is_bot_owner(interaction.user.id):
            return await interaction.response.send_message("❌ Only the bot owner can use this command!", ephemeral=True)
        
        trusted_users = load_trusted_users()
        if user.id not in trusted_users:
            return await interaction.response.send_message(f"❌ {user.mention} is not in the trusted list!", ephemeral=True)
        
        trusted_users.remove(user.id)
        save_trusted_users(trusted_users)
        await interaction.response.send_message(f"✅ Removed {user.mention} from trusted users!", ephemeral=True)

    @app_commands.command(name="list_trusted_users", description="List all trusted users (Bot Owner Only)")
    async def list_trusted_users(self, interaction: discord.Interaction):
        if not is_bot_owner(interaction.user.id):
            return await interaction.response.send_message("❌ Only the bot owner can use this command!", ephemeral=True)
        
        trusted_users = load_trusted_users()
        if not trusted_users:
            return await interaction.response.send_message("ℹ️ No trusted users found.", ephemeral=True)
        
        users_list = []
        for user_id in trusted_users:
            try:
                user = await self.bot.fetch_user(user_id)
                users_list.append(f"• {user.mention} (ID: {user_id})")
            except:
                users_list.append(f"• Unknown User (ID: {user_id})")
        
        embed = discord.Embed(title="🤝 Trusted Users", color=discord.Color.blue())
        embed.description = "\n".join(users_list)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="add_staff_role", description="Add a role to the staff list")
    @app_commands.describe(role="The role to add as staff")
    async def add_staff_role(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)
        if not is_admin_or_owner(interaction):
            return await interaction.response.send_message("❌ Only server owners or administrators can use this command!", ephemeral=True)

        guild_id = str(interaction.guild.id)
        current_staff = load_staff_roles(guild_id)
        role_id = str(role.id)

        if role_id in current_staff:
            return await interaction.response.send_message(f"❌ Role **{role.name}** is already a staff role!", ephemeral=True)

        current_staff.append(role_id)
        save_staff_roles(guild_id, current_staff)
        await interaction.response.send_message(f"✅ Added **{role.name}** to the staff list.", ephemeral=True)

    @app_commands.command(name="remove_staff_role", description="Remove a role from the staff list")
    @app_commands.describe(role="The role to remove from staff")
    async def remove_staff_role(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)
        if not is_admin_or_owner(interaction):
            return await interaction.response.send_message("❌ Only server owners or administrators can use this command!", ephemeral=True)

        guild_id = str(interaction.guild.id)
        current_staff = load_staff_roles(guild_id)
        role_id = str(role.id)

        if role_id not in current_staff:
            return await interaction.response.send_message(f"❌ Role **{role.name}** is not a staff role!", ephemeral=True)

        current_staff.remove(role_id)
        save_staff_roles(guild_id, current_staff)
        await interaction.response.send_message(f"✅ Removed **{role.name}** from the staff list.", ephemeral=True)

    @app_commands.command(name="list_staff_roles", description="List all current staff roles")
    async def list_staff_roles(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("❌ This command must be used in a server!", ephemeral=True)

        guild_id = str(interaction.guild.id)
        staff_role_ids = load_staff_roles(guild_id)

        if not staff_role_ids:
            return await interaction.response.send_message("ℹ️ No staff roles have been set up yet.", ephemeral=True)

        staff_roles = []
        for role_id in staff_role_ids:
            role = interaction.guild.get_role(int(role_id))
            if role:
                staff_roles.append(f"• {role.mention}")

        await interaction.response.send_message("📋 Current staff roles:\n" + "\n".join(staff_roles), ephemeral=True)

    @app_commands.command(name="botstatus", description="Check bot status and permissions")
    async def botstatus(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)

        guild = interaction.guild
        bot_member = guild.me
        bot_perms = bot_member.guild_permissions
        
        embed = discord.Embed(title="🤖 Bot Status", color=discord.Color.blue())
        embed.add_field(name="Server", value=guild.name, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        # Key permissions check
        key_perms = []
        if bot_perms.administrator:
            key_perms.append("✅ Administrator")
        else:
            for perm, name in [
                ('manage_roles', 'Manage Roles'),
                ('manage_channels', 'Manage Channels'),
                ('manage_events', 'Manage Events'),
                ('manage_messages', 'Manage Messages')
            ]:
                if getattr(bot_perms, perm, False):
                    key_perms.append(f"✅ {name}")
        
        embed.add_field(name="Key Permissions", value="\n".join(key_perms) or "❌ Limited permissions", inline=False)
        embed.add_field(name="Bot Role", value=bot_member.top_role.mention, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="send_embed", description="Send an embed message to a channel")
    @app_commands.describe(
        channel="The channel to send the message to",
        title="Embed title (optional)",
        message="Embed message",
        color="Embed color (hex code without #, e.g., FF0000,Color3 to hex: 64(Color3) = 40(hex):4*16+0=64,200(Color3) = C8(hex):12*16+8=200(C = 12)",
        footer="Embed footer text (optional)",
        image_url="Image URL (optional)"
    )
    async def send_embed(self, interaction: discord.Interaction, channel: discord.TextChannel, 
                        message: str, title: str = None, color: str = "0000FF", 
                        footer: str = None, image_url: str = None):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Server only command!", ephemeral=True)
        if not has_event_access(interaction):
            return await interaction.response.send_message("❌ Permission denied!", ephemeral=True)
        
        try:
            embed = discord.Embed(
                title=title[:256] if title else "",
                description=message[:4096],
                color=discord.Color(int(color, 16)) if color != "0000FF" else discord.Color.default()
            )

            if footer:
                embed.set_footer(text=footer[:2048])
            
            if image_url:
                embed.set_image(url=image_url)

            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Embed sent to {channel.mention}", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("❌ Invalid color format! Use hex like FF0000", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))