import discord
from utils.storage import load_staff_roles, is_bot_owner, is_trusted_user, data_manager
import logging

logger = logging.getLogger('discord')

def is_admin_or_owner(interaction: discord.Interaction) -> bool:
    """
    Check if user is admin or server owner
    
    Args:
        interaction: Discord interaction to check permissions for
        
    Returns:
        bool: True if user is admin or owner, False otherwise
    """
    try:
        if not interaction.guild:
            return False
        if not interaction.user:
            return False
        
        # Verify that user is part of the guild
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            return False
            
        # Check if user is owner or has admin permissions
        return interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator
    except Exception as e:
        logger.error(f"Error in is_admin_or_owner: {e}")
        return False

def has_event_access(interaction: discord.Interaction) -> bool:
    """
    Check if user has access to event management commands
    
    Args:
        interaction: Discord interaction to check permissions for
        
    Returns:
        bool: True if user has event access, False otherwise
    """
    try:
        if not interaction.guild:
            return False
        if not interaction.user:
            return False
            
        # Verify that user is part of the guild
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            return False
            
        if is_admin_or_owner(interaction):
            return True
        
        guild_id = str(interaction.guild.id)
        staff_role_ids = load_staff_roles(guild_id)
        
        # Validate that staff_role_ids is a list of strings
        if not isinstance(staff_role_ids, list):
            logger.warning(f"Invalid staff role data for guild {guild_id}")
            return False
            
        for role in member.roles:
            if str(role.id) in staff_role_ids:
                return True
        return False
    except Exception as e:
        logger.error(f"Error in has_event_access: {e}")
        return False

def has_data_access(interaction: discord.Interaction) -> bool:
    """
    Check if user has access to data management commands
    
    Args:
        interaction: Discord interaction to check permissions for
        
    Returns:
        bool: True if user has data access, False otherwise
    """
    try:
        if not interaction.user:
            return False
        return is_trusted_user(interaction.user.id)
    except Exception as e:
        logger.error(f"Error in has_data_access: {e}")
        return False

def has_owner_access(interaction: discord.Interaction) -> bool:
    """
    Check if user is the bot owner
    
    Args:
        interaction: Discord interaction to check permissions for
        
    Returns:
        bool: True if user is bot owner, False otherwise
    """
    try:
        if not interaction.user:
            return False
        return is_bot_owner(interaction.user.id)
    except Exception as e:
        logger.error(f"Error in has_owner_access: {e}")
        return False