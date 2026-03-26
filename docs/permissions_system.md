# Permissions System Documentation

## Overview

The permissions system provides fine-grained access control for the Discord bot, allowing different levels of access based on user roles, ownership status, and trusted user status. This system ensures that sensitive commands and data operations are only accessible to authorized users.

## Core Components

### Permissions Module

The permissions system is located in `utils/permissions.py` and provides several utility functions:

```python
from utils.permissions import is_admin_or_owner, has_event_access, has_data_access
```

## Key Functions

### `is_admin_or_owner(ctx)`
Checks if a user is either an administrator of the server or the bot owner.

**Usage:**
```python
from utils.permissions import is_admin_or_owner

if is_admin_or_owner(ctx):
    # User has admin or owner privileges
    perform_admin_action()
```

**Returns:** Boolean indicating if user has admin or owner access.

### `has_event_access(ctx)`
Checks if a user has access to event management features based on configured staff roles.

**Usage:**
```python
from utils.permissions import has_event_access

if has_event_access(ctx):
    # User has event management access
    allow_event_command()
```

**Returns:** Boolean indicating if user has event access.

### `has_data_access(ctx)`
Checks if a user is trusted or the bot owner, granting access to sensitive data operations.

**Usage:**
```python
from utils.permissions import has_data_access

if has_data_access(ctx):
    # User can access sensitive data
    allow_data_operation()
```

**Returns:** Boolean indicating if user has data access.

## Implementation Examples

### Using Permissions in Cogs

#### Command with Admin/Owner Check
```python
import discord
from discord.ext import commands
from utils.permissions import is_admin_or_owner

class AdminCog(commands.Cog):
    @commands.command(name='ban_user')
    async def ban_user(self, ctx, user: discord.User):
        if not is_admin_or_owner(ctx):
            await ctx.send("❌ You don't have permission to use this command!")
            return
            
        # Perform ban operation
        await user.ban()
        await ctx.send(f"✅ {user.name} has been banned.")
```

#### Slash Command with Data Access Check
```python
@discord.app_commands.command(name="export_data", description="Export server data")
async def export_data(self, interaction: discord.Interaction):
    from utils.permissions import has_data_access
    
    if not has_data_access(interaction):
        await interaction.response.send_message("❌ You don't have permission to export data!", ephemeral=True)
        return
    
    # Export data functionality
    await interaction.response.send_message("Exporting data...", ephemeral=True)
```

### Custom Permission Decorators

You can create custom decorators using the permission functions:

```python
from functools import wraps
from utils.permissions import is_admin_or_owner

def admin_or_owner():
    def predicate(ctx):
        return is_admin_or_owner(ctx)
    
    return commands.check(predicate)

class MyCog(commands.Cog):
    @commands.command(name='admin_command')
    @admin_or_owner()
    async def admin_command(self, ctx):
        await ctx.send("This is an admin-only command!")
```

## Permission Hierarchy

The permission system follows this hierarchy:

1. **Bot Owner**: Highest level of access, granted by `OWNER_USER_ID` environment variable
2. **Server Admin**: Server administrators based on Discord's admin permissions
3. **Staff Roles**: Users with configured staff roles
4. **Trusted Users**: Users added to trusted user list
5. **Regular Users**: Default access level

## Configuration

### Trusted Users Management

Trusted users can be managed through the data management system:

```python
from utils.storage import add_trusted_user, remove_trusted_user, load_trusted_users

# Add a trusted user
add_trusted_user(guild_id, user_id)

# Remove a trusted user
remove_trusted_user(guild_id, user_id)

# Load trusted users
trusted_users = load_trusted_users(guild_id)
```

### Staff Roles Configuration

Staff roles are configured per server and used by the `has_event_access()` function:

```python
from utils.storage import load_staff_roles, save_staff_roles

# Load staff roles for a server
staff_roles = load_staff_roles(guild_id)

# Save staff roles configuration
save_staff_roles(guild_id, role_ids_list)
```

## Best Practices

### For Security
1. Always check permissions before executing sensitive operations
2. Use appropriate permission functions for different access levels
3. Don't rely solely on role names – use role IDs for accuracy
4. Log permission failures for security monitoring

### For Usability
1. Provide clear error messages when permissions are insufficient
2. Use ephemeral responses for permission errors in slash commands
3. Document permission requirements in command descriptions
4. Consider implementing a permission help command

## Error Handling

The permission system includes proper error handling:

```python
from utils.permissions import is_admin_or_owner

async def protected_command(self, ctx):
    try:
        if not is_admin_or_owner(ctx):
            await ctx.send("❌ Insufficient permissions to execute this command!")
            return
        
        # Execute command logic
        await ctx.send("✅ Command executed successfully!")
        
    except Exception as e:
        # Log error and notify user appropriately
        print(f"Error in protected command: {e}")
        await ctx.send("❌ An error occurred while executing the command.")
```

## Integration with Other Systems

### With Storage System
The permission system works closely with the storage system to control access to sensitive data operations:

```python
from utils.permissions import has_data_access
from utils.storage import load_trusted_users

async def view_trusted_users(self, ctx):
    if not has_data_access(ctx):
        await ctx.send("❌ You don't have permission to view trusted users!")
        return
    
    trusted_users = load_trusted_users(str(ctx.guild.id))
    # Display trusted users
```

### With Ticket System
The ticket system uses permissions to control access to ticket management functions:

```python
from utils.permissions import has_event_access

async def close_ticket(self, ctx):
    if not has_event_access(ctx):
        await ctx.send("❌ Only authorized staff can close tickets!")
        return
    
    # Close ticket logic
```

This permission system provides a robust and flexible way to control access to different bot features while maintaining security and usability.