import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger('discord')

def get_server_data_path(guild_id: str, filename: str) -> str:
    """Get path to server-specific data file"""
    if not os.path.exists(f"servers/{guild_id}"):
        os.makedirs(f"servers/{guild_id}")
    return f"servers/{guild_id}/{filename}"

# Trusted Users System
def load_trusted_users() -> List[int]:
    try:
        if os.path.exists("trusted_users.json"):
            with open("trusted_users.json", "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading trusted users: {e}")
    return []

def save_trusted_users(trusted_users: List[int]) -> bool:
    try:
        with open("trusted_users.json", "w") as f:
            json.dump(trusted_users, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving trusted users: {e}")
        return False

def is_bot_owner(user_id: int) -> bool:
    from bot import OWNER_USER_ID
    try:
        return user_id == int(OWNER_USER_ID)
    except ValueError:
        logger.error(f"Invalid OWNER_USER_ID format: {OWNER_USER_ID}")
        return False

def is_trusted_user(user_id: int) -> bool:
    return is_bot_owner(user_id) or user_id in load_trusted_users()

# Multi-Ticket Configs
def load_multi_ticket_configs(guild_id: str) -> List[Dict[str, Any]]:
    path = get_server_data_path(guild_id, "multi_ticket_configs.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_multi_ticket_configs(guild_id: str, configs: List[Dict[str, Any]]) -> None:
    path = get_server_data_path(guild_id, "multi_ticket_configs.json")
    with open(path, 'w') as f:
        json.dump(configs, f, indent=2)

def get_multi_ticket_setup_by_id(guild_id: str, setup_id: str) -> Optional[Dict[str, Any]]:
    configs = load_multi_ticket_configs(guild_id)
    for config in configs:
        if config['id'] == setup_id:
            return config
    return None

# User Timezones
def load_user_timezones(guild_id: str) -> Dict[str, str]:
    path = get_server_data_path(guild_id, "user_timezones.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}

def save_user_timezone(guild_id: str, user_id: int, timezone: str) -> None:
    timezones = load_user_timezones(guild_id)
    timezones[str(user_id)] = timezone
    with open(get_server_data_path(guild_id, "user_timezones.json"), 'w') as f:
        json.dump(timezones, f, indent=2)

# Staff Roles
def load_staff_roles(guild_id: str) -> List[str]:
    path = get_server_data_path(guild_id, "staff_roles.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_staff_roles(guild_id: str, staff_roles: List[str]) -> None:
    with open(get_server_data_path(guild_id, "staff_roles.json"), 'w') as f:
        json.dump(staff_roles, f, indent=2)

# Ticket Setups
def load_ticket_configs(guild_id: str) -> List[Dict[str, Any]]:
    path = get_server_data_path(guild_id, "ticket_configs.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump([], f)
        return []

def save_ticket_configs(guild_id: str, configs: List[Dict[str, Any]]) -> None:
    with open(get_server_data_path(guild_id, "ticket_configs.json"), 'w') as f:
        json.dump(configs, f, indent=2)

def get_ticket_setup_by_id(guild_id: str, setup_id: str) -> Optional[Dict[str, Any]]:
    configs = load_ticket_configs(guild_id)
    for c in configs:
        if c['id'] == setup_id:
            return c
    return None

# Active Tickets
def load_active_tickets(guild_id: str) -> Dict[str, Any]:
    path = get_server_data_path(guild_id, "active_tickets.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}

def update_ticket_data(guild_id: str, thread_id: str, ticket_data: Dict[str, Any]) -> bool:
    """Update ticket data for a specific thread"""
    try:
        # Load all active tickets
        tickets = load_active_tickets(guild_id)
        
        # Find the ticket by thread_id
        for user_id, data in tickets.items():
            if data.get('thread_id') == thread_id:
                # Update the ticket data
                tickets[user_id] = ticket_data
                
                # Save the updated tickets
                with open(get_server_data_path(guild_id, "active_tickets.json"), 'w') as f:
                    json.dump(tickets, f, indent=2)
                
                logger.info(f"✅ Updated ticket data - Server: {guild_id}, Thread: {thread_id}")
                return True
        
        logger.warning(f"⚠️ Ticket not found for update - Server: {guild_id}, Thread: {thread_id}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error updating ticket data: {str(e)}")
        return False

def save_active_ticket(guild_id: str, user_id: int, thread_id: str, handle_msg_id: str, setup_id: str, ticket_data: Optional[Dict[str, Any]] = None) -> bool:
    try:
        tickets = load_active_tickets(guild_id)
        user_id_str = str(user_id)
        
        if ticket_data is None:
            # Create basic ticket data if not provided
            ticket_data = {
                "thread_id": thread_id,
                "handle_msg_id": handle_msg_id,
                "setup_id": setup_id,
                "created_at": datetime.utcnow().isoformat(),
                "user_id": user_id_str
            }
        else:
            # Ensure required fields are present
            ticket_data.update({
                "thread_id": thread_id,
                "handle_msg_id": handle_msg_id,
                "setup_id": setup_id,
                "user_id": user_id_str
            })
        
        tickets[user_id_str] = ticket_data
        with open(get_server_data_path(guild_id, "active_tickets.json"), 'w') as f:
            json.dump(tickets, f, indent=2)
        
        logger.info(f"✅ Saved active ticket - Server: {guild_id}, User: {user_id_str}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save active ticket: {str(e)}")
        return False

def get_ticket_data(guild_id: str, identifier: str) -> Optional[Dict[str, Any]]:
    """
    Get ticket data by user_id or thread_id
    identifier: can be either user_id (str) or thread_id (str)
    """
    try:
        tickets = load_active_tickets(guild_id)
        
        # Check if identifier is a user_id
        if identifier in tickets:
            return tickets[identifier]
        
        # Search by thread_id
        for user_id, data in tickets.items():
            if data.get('thread_id') == identifier:
                return data
        
        return None
    except Exception as e:
        logger.error(f"❌ Error getting ticket data: {str(e)}")
        return None

def remove_active_ticket(guild_id: str, identifier: str) -> bool:
    """
    Remove active ticket by user_id or thread_id
    identifier: can be either user_id (str) or thread_id (str)
    """
    try:
        tickets = load_active_tickets(guild_id)
        
        # Check if identifier is a user_id
        if identifier in tickets:
            setup_id = tickets[identifier].get("setup_id", "unknown")
            del tickets[identifier]
            with open(get_server_data_path(guild_id, "active_tickets.json"), 'w') as f:
                json.dump(tickets, f, indent=2)
            logger.info(f"✅ Removed ticket - Server: {guild_id}, User: {identifier}, Setup: {setup_id}")
            return True
        
        # Search by thread_id
        for user_id, data in tickets.items():
            if data.get('thread_id') == identifier:
                setup_id = data.get("setup_id", "unknown")
                del tickets[user_id]
                with open(get_server_data_path(guild_id, "active_tickets.json"), 'w') as f:
                    json.dump(tickets, f, indent=2)
                logger.info(f"✅ Removed ticket - Server: {guild_id}, Thread: {identifier}, Setup: {setup_id}")
                return True
        
        logger.info(f"ℹ️ Ticket not found for removal - Server: {guild_id}, Identifier: {identifier}")
        return False
    except Exception as e:
        logger.error(f"❌ Error removing active ticket: {str(e)}")
        return False

# User Ticket Counts
def load_user_ticket_counts(guild_id: str) -> Dict[str, int]:
    path = get_server_data_path(guild_id, "user_ticket_counts.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(path, 'w') as f:
            json.dump({}, f)
        return {}

def save_user_ticket_count(guild_id: str, user_id: int, count: int) -> None:
    counts = load_user_ticket_counts(guild_id)
    counts[str(user_id)] = count
    with open(get_server_data_path(guild_id, "user_ticket_counts.json"), 'w') as f:
        json.dump(counts, f, indent=2)

def increment_user_ticket_count(guild_id: str, user_id: int) -> int:
    counts = load_user_ticket_counts(guild_id)
    current = counts.get(str(user_id), 0)
    new_count = current + 1
    save_user_ticket_count(guild_id, user_id, new_count)
    return new_count

def reset_user_ticket_count(guild_id: str, user_id: int) -> None:
    save_user_ticket_count(guild_id, user_id, 0)

# Helper functions
def save_json_data(guild_id: str, filename: str, data: Any) -> None:
    path = get_server_data_path(guild_id, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def backup_server_data(guild_id: str) -> bool:
    try:
        # Implementation would go here
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

# ==================== Get all datas functions ===================
# ==================== GLOBAL DATA FUNCTIONS ====================

def get_all_servers_data() -> List[str]:
    """Get list of all server directories"""
    if not os.path.exists("servers"):
        return []
    return [d for d in os.listdir("servers") if os.path.isdir(os.path.join("servers", d))]

def load_all_ticket_configs() -> Dict[str, List[Dict[str, Any]]]:
    """Load ticket configs from ALL servers"""
    all_data = {}
    for server_id in get_all_servers_data():
        all_data[server_id] = load_ticket_configs(server_id)
    return all_data

def load_all_multi_ticket_configs() -> Dict[str, List[Dict[str, Any]]]:
    """Load multi-ticket configs from ALL servers"""
    all_data = {}
    for server_id in get_all_servers_data():
        all_data[server_id] = load_multi_ticket_configs(server_id)
    return all_data

def load_all_active_tickets() -> Dict[str, Dict[str, Any]]:
    """Load active tickets from ALL servers"""
    all_data = {}
    for server_id in get_all_servers_data():
        all_data[server_id] = load_active_tickets(server_id)
    return all_data

def load_all_user_ticket_counts() -> Dict[str, Dict[str, int]]:
    """Load user ticket counts from ALL servers"""
    all_data = {}
    for server_id in get_all_servers_data():
        all_data[server_id] = load_user_ticket_counts(server_id)
    return all_data

def load_all_staff_roles() -> Dict[str, List[str]]:
    """Load staff roles from ALL servers"""
    all_data = {}
    for server_id in get_all_servers_data():
        all_data[server_id] = load_staff_roles(server_id)
    return all_data

def load_all_user_timezones() -> Dict[str, Dict[str, str]]:
    """Load user timezones from ALL servers"""
    all_data = {}
    for server_id in get_all_servers_data():
        all_data[server_id] = load_user_timezones(server_id)
    return all_data

# ==================== GLOBAL EXPORT/IMPORT ====================

def export_all_server_data() -> Dict[str, Dict[str, Any]]:
    """Export all data from all servers"""
    return {
        "ticket_configs": load_all_ticket_configs(),
        "multi_ticket_configs": load_all_multi_ticket_configs(),
        "active_tickets": load_all_active_tickets(),
        "user_ticket_counts": load_all_user_ticket_counts(),
        "staff_roles": load_all_staff_roles(),
        "user_timezones": load_all_user_timezones(),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_servers": len(get_all_servers_data())
    }

def import_all_server_data(data: Dict[str, Any]) -> bool:
    """Import data to all servers"""
    try:
        # Import each server's data
        for server_id, server_data in data.get("ticket_configs", {}).items():
            save_ticket_configs(server_id, server_data)
        
        for server_id, server_data in data.get("multi_ticket_configs", {}).items():
            save_multi_ticket_configs(server_id, server_data)
        
        for server_id, server_data in data.get("active_tickets", {}).items():
            save_json_data(server_id, "active_tickets.json", server_data)
        
        for server_id, server_data in data.get("user_ticket_counts", {}).items():
            save_json_data(server_id, "user_ticket_counts.json", server_data)
        
        for server_id, server_data in data.get("staff_roles", {}).items():
            save_staff_roles(server_id, server_data)
        
        for server_id, server_data in data.get("user_timezones", {}).items():
            save_json_data(server_id, "user_timezones.json", server_data)
        
        return True
    except Exception as e:
        logger.error(f"Error importing all server data: {e")
        return False
