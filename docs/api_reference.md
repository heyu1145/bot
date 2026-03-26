# API Reference

## Overview

This document provides a comprehensive reference to the main classes, functions, and modules available in the Discord Bot framework.

## Main Bot Module (`bot.py`)

### Main Components

#### `load_cogs()`
Asynchronously loads all cogs using the Auto-Cog Loading system.

**Returns:** None

#### `get_uptime()`
Calculates and returns the bot's uptime since startup.

**Returns:** String with uptime in format "Xd Xh Xm" or "Xh Xm Xs" or "Xm Xs"

#### `main()`
The main async function that starts the bot.

**Returns:** None

## Auto-Cog Loading System (`utils/cog_loader.py`)

### CogLoader Class

#### Constructor: `CogLoader(bot, cogs_directory="cogs")`
Creates a new CogLoader instance.

**Parameters:**
- `bot`: Discord bot instance
- `cogs_directory`: Path to cogs directory (default: "cogs")

#### `discover_cogs()`
Discovers all cog modules in the specified directory.

**Returns:** List of discovered cog module names

#### `load_all_cogs(exclude_cogs=None)`
Automatically loads all discovered cogs.

**Parameters:**
- `exclude_cogs`: List of cogs to exclude from loading

**Returns:** Dictionary containing load results

#### `reload_cog(cog_name)`
Reloads a specific cog.

**Parameters:**
- `cog_name`: Name of the cog to reload

**Returns:** Boolean indicating success

#### `unload_cog(cog_name)`
Unloads a specific cog.

**Parameters:**
- `cog_name`: Name of the cog to unload

**Returns:** Boolean indicating success

#### `get_loaded_cogs()`
Gets the list of loaded cogs.

**Returns:** List of loaded cog names

#### `get_failed_cogs()`
Gets the list of failed cogs.

**Returns:** List of failed cog names

#### `get_cogs_status()`
Gets comprehensive status information about all cogs.

**Returns:** Dictionary with status information

### Utility Functions

#### `setup_cogs(bot, cogs_directory="cogs", exclude_cogs=None)`
Convenience function to set up and load all cogs.

**Parameters:**
- `bot`: Discord bot instance
- `cogs_directory`: Path to cogs directory
- `exclude_cogs`: List of cogs to exclude

**Returns:** CogLoader instance

## Storage System (`utils/storage.py`)

### DataManager Class

#### `get_data(guild_id, data_type)`
Retrieves data of specified type for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `data_type`: Type of data to retrieve

**Returns:** Data for the specified guild and type

#### `save_data(guild_id, data_type, data)`
Saves data of specified type for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `data_type`: Type of data to save
- `data`: Data to save

**Returns:** Boolean indicating success

### Ticket Functions

#### `load_active_tickets(guild_id)`
Loads all active tickets for a guild.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** Dictionary of active tickets

#### `save_active_ticket(guild_id, thread_id, ticket_data)`
Saves a ticket as active for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `thread_id`: ID of the ticket thread
- `ticket_data`: Data for the ticket

**Returns:** Boolean indicating success

#### `remove_active_ticket(guild_id, thread_id)`
Removes an active ticket for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `thread_id`: ID of the ticket thread

**Returns:** Boolean indicating success

#### `get_ticket_data(guild_id, thread_id)`
Retrieves data for a specific ticket.

**Parameters:**
- `guild_id`: ID of the guild
- `thread_id`: ID of the ticket thread

**Returns:** Ticket data or None if not found

#### `update_ticket_data(guild_id, thread_id, new_data)`
Updates data for a specific ticket.

**Parameters:**
- `guild_id`: ID of the guild
- `thread_id`: ID of the ticket thread
- `new_data`: New data to update with

**Returns:** Boolean indicating success

### Configuration Functions

#### `load_ticket_configs(guild_id)`
Loads ticket configurations for a guild.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** List of ticket configurations

#### `save_ticket_configs(guild_id, configs)`
Saves ticket configurations for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `configs`: List of configurations to save

**Returns:** Boolean indicating success

#### `get_ticket_setup_by_id(guild_id, setup_id)`
Retrieves a specific ticket setup by ID.

**Parameters:**
- `guild_id`: ID of the guild
- `setup_id`: ID of the setup

**Returns:** Setup configuration or None if not found

### Multi-Ticket Functions

#### `load_multi_ticket_configs(guild_id)`
Loads multi-ticket configurations for a guild.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** List of multi-ticket configurations

#### `save_multi_ticket_configs(guild_id, configs)`
Saves multi-ticket configurations for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `configs`: List of configurations to save

**Returns:** Boolean indicating success

#### `get_multi_ticket_setup_by_id(guild_id, setup_id)`
Retrieves a specific multi-ticket setup by ID.

**Parameters:**
- `guild_id`: ID of the guild
- `setup_id`: ID of the setup

**Returns:** Setup configuration or None if not found

### User Management Functions

#### `load_trusted_users(guild_id)`
Loads trusted user IDs for a guild.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** List of trusted user IDs

#### `add_trusted_user(guild_id, user_id)`
Adds a user to the trusted list for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `user_id`: ID of the user to add

**Returns:** Boolean indicating success

#### `remove_trusted_user(guild_id, user_id)`
Removes a user from the trusted list for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `user_id`: ID of the user to remove

**Returns:** Boolean indicating success

#### `load_user_timezones(guild_id)`
Loads user timezone information for a guild.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** Dictionary of user ID to timezone

#### `set_user_timezone(guild_id, user_id, timezone)`
Sets a user's timezone for a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `user_id`: ID of the user
- `timezone`: Timezone to set

**Returns:** Boolean indicating success

### Ticket Count Functions

#### `load_user_ticket_counts(guild_id)`
Loads ticket counts for users in a guild.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** Dictionary of user ID to ticket count

#### `increment_user_ticket_count(guild_id, user_id)`
Increments the ticket count for a user in a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `user_id`: ID of the user

**Returns:** New ticket count for the user

#### `reset_user_ticket_count(guild_id, user_id)`
Resets the ticket count for a user in a guild.

**Parameters:**
- `guild_id`: ID of the guild
- `user_id`: ID of the user

**Returns:** Boolean indicating success

### Data Management Functions

#### `export_server_data(guild_id)`
Exports all data for a server.

**Parameters:**
- `guild_id`: ID of the guild

**Returns:** Complete server data dictionary

#### `import_server_data(guild_id, data)`
Imports data for a server with validation.

**Parameters:**
- `guild_id`: ID of the guild
- `data`: Data to import

**Returns:** Boolean indicating success

## Permissions System (`utils/permissions.py`)

#### `is_admin_or_owner(ctx)`
Checks if a user is an admin of the server or the bot owner.

**Parameters:**
- `ctx`: Discord command context

**Returns:** Boolean indicating if user is admin or owner

#### `has_event_access(ctx)`
Checks if a user has event access through staff roles.

**Parameters:**
- `ctx`: Discord command context

**Returns:** Boolean indicating if user has event access

#### `has_data_access(ctx)`
Checks if a user has data access through trusted status or ownership.

**Parameters:**
- `ctx`: Discord command context

**Returns:** Boolean indicating if user has data access