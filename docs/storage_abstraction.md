# Storage Abstraction Layer Documentation

## Overview

The storage abstraction layer provides a unified interface for managing data persistence in the Discord bot. It handles server-specific data storage using JSON files and provides utilities for various data types including tickets, configurations, user data, and more.

## Directory Structure

```
servers/
└── {guild_id}/              # Each server has its own directory
    ├── tickets.json         # Active tickets data
    ├── configs.json         # Server configurations
    ├── timezones.json       # User timezone data
    ├── trusted_users.json   # Trusted user IDs
    └── ticket_counts.json   # User ticket count tracking
```

## Core Components

### DataManager Class
The main class that manages all data operations:

```python
from utils.storage import data_manager

# Access the global data manager instance
data_manager.get_data(guild_id, data_type)
data_manager.save_data(guild_id, data_type, data)
```

### Data Types Supported
- `tickets`: Active ticket data with thread IDs, user info, and status
- `configs`: Server-specific configurations and settings
- `timezones`: User timezone information for time-based features
- `trusted_users`: List of users with elevated permissions
- `ticket_counts`: Track how many tickets each user has opened
- `multi_ticket_configs`: Configuration for multi-ticket panels

## Key Functions

### Ticket Management
```python
from utils.storage import (
    load_active_tickets, save_active_ticket, remove_active_ticket,
    get_ticket_data, update_ticket_data
)

# Load all active tickets for a server
tickets = load_active_tickets(guild_id)

# Save a new ticket
save_active_ticket(guild_id, thread_id, ticket_data)

# Get specific ticket data
ticket = get_ticket_data(guild_id, thread_id)

# Update ticket data
update_ticket_data(guild_id, thread_id, new_data)
```

### Configuration Management
```python
from utils.storage import (
    load_ticket_configs, save_ticket_configs,
    load_multi_ticket_configs, save_multi_ticket_configs,
    get_ticket_setup_by_id, get_multi_ticket_setup_by_id
)

# Load ticket configurations
configs = load_ticket_configs(guild_id)

# Save multi-ticket configurations
save_multi_ticket_configs(guild_id, configs)

# Get specific setup by ID
setup = get_ticket_setup_by_id(guild_id, setup_id)
```

### User Data Management
```python
from utils.storage import (
    load_trusted_users, add_trusted_user, remove_trusted_user,
    load_user_timezones, set_user_timezone,
    load_user_ticket_counts, increment_user_ticket_count
)

# Manage trusted users
trusted_users = load_trusted_users(guild_id)
add_trusted_user(guild_id, user_id)

# Track user ticket counts
count = increment_user_ticket_count(guild_id, user_id)
user_counts = load_user_ticket_counts(guild_id)
```

## Data Structure Examples

### Ticket Data Structure
```json
{
  "thread_id": "1234567890",
  "user_id": "9876543210",
  "user_mention": "<@9876543210>",
  "created_at": "2023-12-01T10:00:00Z",
  "handle_channel_id": "5555555555",
  "handle_msg_id": "6666666666",
  "joined_staff": [
    {
      "id": "1111111111",
      "name": "Staff Member",
      "joined_at": "2023-12-01T10:05:00Z"
    }
  ],
  "closer_name": "Closing Staff",
  "closer_id": "1111111111",
  "closed_at": "2023-12-01T11:00:00Z",
  "panel_id": "panel123",
  "option_id": "option456"
}
```

### Configuration Data Structure
```json
{
  "id": "config123",
  "ticket_channel_id": "1111111111",
  "handle_channel_id": "2222222222",
  "transcripts_channel_id": "3333333333",
  "title_format": "{username} support",
  "open_message": "Welcome to your support ticket!",
  "button_label": "Support",
  "button_emoji": "🎫",
  "created_at": "2023-12-01T10:00:00Z"
}
```

## Error Handling

The storage layer includes proper error handling for common issues:

- File I/O errors are caught and logged
- Missing directories are created automatically
- Invalid JSON data is handled gracefully
- Permissions errors are reported appropriately

## Best Practices

### For Developers
1. Always use the provided utility functions rather than direct file access
2. Handle potential None returns from data loading functions
3. Use appropriate data types when saving/loading
4. Implement proper error handling when using storage functions

### For Performance
1. Batch operations when possible to reduce file I/O
2. Cache frequently accessed data in memory when appropriate
3. Use specific functions for specific operations rather than loading entire files

## Migration and Backup

The system supports data export/import functionality for backup and migration purposes:

```python
from utils.storage import export_server_data, import_server_data

# Export all server data
export_data = export_server_data(guild_id)

# Import server data (with validation)
success = import_server_data(guild_id, export_data)
```