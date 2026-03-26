# Configuration Guide

## Environment Variables Configuration

### Required Environment Variables
- `TOKEN`: Discord bot token
- `OWNER_USER_ID`: Discord user ID of the bot owner

### How to Obtain Environment Variables

#### Bot Token (TOKEN)
1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select an existing one
3. Go to "Bot" → "Token"
4. Click "Reset Token" and copy your token
5. **⚠️ Never share your token with anyone!**

#### User ID (OWNER_USER_ID)
1. Open Discord
2. Right-click your profile → "Copy User ID"

## Configuration File Structure

The project uses configuration files in the `config/` directory to manage bot settings:

```
config/
├── config.py          # Main configuration file
└── __init__.py        # Module initialization
```

### Main Configuration Items

#### DISCORD_CONFIG
Contains Discord bot related configurations:
- `TOKEN`: Discord bot token
- `OWNER_USER_ID`: Bot owner ID
- `COMMAND_PREFIX`: Command prefix
- `INTENTS`: Discord bot intents configuration

#### TIME_CONFIG
Contains time-related configurations:
- Time display formats
- Uptime calculation parameters

#### TICKET_CONFIG
Contains ticket system related configurations:
- Default title format
- Maximum character limits
- Other ticket options

## Configuration File Example

```python
# config/config.py

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_CONFIG = {
    'TOKEN': os.getenv('TOKEN'),
    'OWNER_USER_ID': int(os.getenv('OWNER_USER_ID', 0)),
    'COMMAND_PREFIX': '!',
    'INTENTS': {
        'guilds': True,
        'members': True,
        'messages': True,
        'reactions': True,
        'message_content': True,
    }
}

TIME_CONFIG = {
    'UPTIME_DIVISORS': {
        'day_seconds': 86400,
        'hour_seconds': 3600,
        'minute_seconds': 60
    }
}

TICKET_CONFIG = {
    'DEFAULT_TITLE_FORMAT': '{username}\'s Ticket',
    'MAX_TITLE_LENGTH': 50,
    'MAX_DESCRIPTION_LENGTH': 1000,
    'MAX_EMOJI_LENGTH': 2,
}
```

## Environment Configuration

### Using Poetry (Recommended)
```bash
# Install Poetry if not already installed
pip install poetry

# Create virtual environment and install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using requirements.txt
```bash
# Install dependencies directly
pip install -r requirements.txt
```

## Runtime Configuration

### Running the Bot
```bash
python3 app.py
```

**Note:** Run `app.py` (not `bot.py`) for full web preview functionality.

The web dashboard will be available at http://localhost:10000 by default, providing real-time status updates and system monitoring.

## Configuration Validation

The system validates the following configurations at startup:
- Whether the bot token exists
- Whether the owner user ID exists
- Whether required intents are enabled

