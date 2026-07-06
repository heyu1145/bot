"""common checks"""
import discord


def is_guild_owner(interaction: discord.Interaction) -> bool:
    """Check if the user is the owner of the guild."""
    return interaction.user.id == interaction.guild.owner_id if interaction.guild else False


def is_admin(interaction: discord.Interaction) -> bool:
    """Check if the user has administrator permissions."""
    guild = interaction.guild
    if guild is None:
        return False

    member = guild.get_member(interaction.user.id)
    if member is None:
        return False

    return member.guild_permissions.administrator


def is_weekday(interaction: discord.Interaction) -> bool:
    """Check if the command is used on a weekday."""
    return interaction.created_at.weekday() < 5  # 0-4 are weekdays


def is_weekend(interaction: discord.Interaction) -> bool:
    """Check if the command is used on a weekend."""
    return interaction.created_at.weekday() >= 5  # 5-6 are weekends
