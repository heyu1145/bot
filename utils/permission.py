import discord
from utils.storage import load_staff_roles, is_bot_owner, is_trusted_user

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

def has_data_access(interaction: discord.Interaction) -> bool:
    return is_trusted_user(interaction.user.id)