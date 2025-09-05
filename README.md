# Discord Ticket & Events Bot

A feature-rich Discord bot for handling support tickets, event management, and server administration with a modern slash command interface.

## 🚀 Features

### 🎫 Ticket System
- **Multi-Ticket Panels**: Create panels with multiple ticket options
- **Single Ticket Setup**: Simple one-button ticket creation
- **Auto Thread Creation**: Private threads for each ticket
- **Staff Management**: Role-based access control
- **Transcripts**: Automatic conversation logging
- **User Limits**: Prevent ticket spam with user limits

### 📅 Event Management
- **Smart Time Parsing**: Supports multiple time formats:
  - `YYYY-MM-DD HH:MM` (2024-12-25 14:30)
  - `MM-DD HH:MM` (12-25 14:30) 
  - `HH:MM` (14:30) - auto-detects today/tomorrow
- **Timezone Support**: User-specific timezone configuration
- **Voice/Text Events**: Support for both voice channel and external events
- **Event Modifications**: Change event times easily

### 🔐 Permission System
- **Trusted Users**: Bot owner can designate trusted users
- **Role-Based Access**: Staff roles for ticket and event management
- **Admin Protection**: Commands hidden from unauthorized users

### 📊 Data Management
- **JSON Export/Import**: Backup and restore server data
- **Server Isolation**: Data separated per server
- **Statistics**: View server data metrics

## 🛠️ Setup

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Discord Server with appropriate permissions

### Step 1: Create a Discord Bot

1. **Go to Discord Developer Portal**
   - Visit https://discord.com/developers/applications
   - Click "New Application" and give it a name

2. **Create Bot User**
   - Go to the "Bot" section in your application
   - Click "Add Bot" and confirm

3. **Get Bot Token**
   - Under the "Token" section, click "Copy" to get your bot token
   - This is your `TOKEN`
   - ⚠️ **Never share this token with anyone!**

4. **Enable Privileged Intents**
   - Enable both "PRESENCE INTENT" and "SERVER MEMBERS INTENT"
   - Enable "MESSAGE CONTENT INTENT"

### Step 2: Get Your User ID

1. **Enable Developer Mode in Discord**
   - Open Discord Settings → Advanced → Enable Developer Mode

2. **Find Your User ID**
   - Right-click on your username → "Copy User ID"
   - This is your `OWNER_USER_ID`

### Step 3: Environment File Setup

Create a `.env` file in the root directory with the following content:

```env
# Required: Your bot token from Discord Developer Portal
TOKEN=your_discord_bot_token_here

# Required: Your Discord User ID (enable developer mode to get this)
OWNER_USER_ID=your_discord_user_id_here
```

## ❌ Errors

### The helper to handle errors

1. **No Discord token found!**
   - Check your .env file added TOKEN value
   - Check you copied current Discord bot token
     
2. **No Owner ID found!**
   - Check your .env file added OWNER_USER_ID value
   - Check you copied current Discord user ID
     
3. **Failed to load cogs!**
   - restart bot to try again
   - Check you added all file in github if didnt work

## 🚩 Upgrade bot

### The tips when Github file update

1. **Save you server datas by /export_data to import later**
2. **ReDeploy your bot to update file**
3. **Load your data by /import_data so that your data wont lost**

## 🏢 Project edits

You can editing to add/delete commands by recommend ways

## Codes you can edit or delete
**Codes in cogs without data_management**

## Code add example
```Python
import discord
from discord import app_commands
from discord.ext import commands
import logging

logger=logging.getLogger('discord')

class Example(command.Cog):
   def __init__(self, bot):
      self.bot = bot

   def ExampleFunction(UserInput):
      logger.info(f"Output: User Inputed: {UserInput}")

@app_commands.command(name="ExampleCommand",description="Example Command for test")
@app_commands.describe(
   Input="Input anything and see it in logs"
)
async def CommandFunction(self, intersection: discord.intersection, Input: str)
    ExampleFunction(Input)
    return await intersection.response.sentmessage(f"Sent Successfully! UserInput: {Input}")

async def setup(bot)
    await bot.add_cog(Example(bot))
 ```