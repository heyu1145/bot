___🧪 FEATURE OFFLINE/TESTING BRANCH - For local development and testing, with beta feature___
- **Use [offline branch](https://github.com/heyu1145/bot.git/tree/offline) for better stability**

___For cloud deployment, visit the [online branch](https://github.com/heyu1145/bot/tree/online)___

# 🤖 Discord Bot

A feature-rich Discord Bot built with Python, now with Auto-Cog Loading capability.

## 🚀 Features

- **Web Preview** - Flask web dashboard for real-time status monitoring
- **Custom Errors** - Custom error handling for easier debugging
- **Admin & Trusted Users** - Simple permission system for data access
- **Ticket System** - Complete ticket system for user support
- **Auto-Cog Loading** - Automatically discovers and loads all extension modules in the cogs directory

## 󰂺 Docs for Customize

- **Directory** - You can look for [docs](docs) for all document
- **Initial File** - Look for [Initial file](docs/index.md) for status and docs describe

## 🏗️ Project Structure

```text
bot/
├── app.py              # Flask web dashboard
├── bot.py              # Discord bot core
├── CHANGELOG.md        # Project changelog
├── IFLOW.md            # iFlow documentation
├── README.md           # Project overview and setup
├── cogs/               # Bot command modules
│   ├── admin.py        # Admin commands
│   ├── tickets.py      # Ticket system
│   ├── events.py       # Event handlers
│   ├── data_management.py # Data handling
│   ├── debug.py        # Debug utilities
│   ├── helper.py       # Utility commands
│   └── dynamic_messages.py # Dynamic message handling
├── config/             # Configuration files
│   ├── config.py       # Main configuration
│   └── __init__.py     # Module initialization
├── docs/               # Documentation files
│   ├── api_reference.md    # API reference documentation
│   ├── auto_cog_loading.md # Auto-cog loading system documentation
│   ├── configuration.md    # Configuration guide
│   ├── index.md            # Documentation index
│   ├── permissions_system.md # Permissions system documentation
│   ├── storage_abstraction.md # Storage abstraction layer documentation
│   └── user_custom_modules.md # User custom modules guide
├── static/             # Web assets (CSS/JS)
│   ├── css/            # Stylesheets
│   │   └── dashboard.css
│   └── js/             # JavaScript files
│       └── dashboard.js
├── templates/          # HTML templates
│   └── bot_dashboard.html
├── servers/            # Server-specific data storage
├── temp/               # Temporary files
├── utils/              # Utility modules
│   ├── auto_refresh.py # Auto refresh tasks
│   ├── cog_loader.py   # Auto-cog loading system
│   ├── data_storage.py # Data storage utilities
│   ├── helper.py       # Common utilities
│   ├── permissions.py  # Access control
│   ├── storage.py      # Data management
│   └── __init__.py     # Module initialization
├── config.json         # Additional configuration
├── customerror.py      # Custom exceptions
├── LICENSE.txt         # License information
├── poetry.lock         # Poetry dependency lock file
├── pyproject.toml      # Poetry project configuration
└── requirements.txt    # Python dependencies
```

## ⚙️ Installation

### Prerequisites

- Your Discord bot token
- Your Discord user ID

### How to Get Your Credentials

**Bot Token:**
1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application or select existing one
3. Go to **Bot** → **Token**
4. Click **Reset Token** and copy your token
5. **⚠️ Never share your token with anyone!**

**User ID:**
1. Open Discord
2. Right-click your profile → **Copy User ID**

### Installation Methods

#### Option A: Using Poetry (Recommended)

```bash
# Install Poetry if not available
pip install poetry

# Create virtual environment and install dependencies
poetry install

# Activate virtual environment
poetry shell

# Or manually activate
source $(poetry env info --path)/bin/activate
```

#### Option B: Using requirement.txt

```bash
# Install dependencies directly
pip install -r requirement.txt

# Or using pipx
pipx install -r requirement.txt
```

### Running the Bot

```bash
python3 app.py
```
**Note:** Run `app.py` (not `bot.py`) for full web preview functionality.

## 🔧 Auto-Cog Loading System

The bot now features an automatic cog loading system that dynamically discovers and loads all extension modules in the `cogs/` directory.

### How It Works

- Automatically discovers all `.py` files in the `cogs/` directory (excluding `__init__.py`)
- Loads each module as a cog extension when the bot starts
- Provides detailed logging of loading status and errors

### Adding New Cogs

To add new functionality:
1. Create a new Python file in the `cogs/` directory
2. Follow the standard cog structure with a setup function
3. The bot will automatically discover and load it on restart

### Excluding Specific Cogs

To exclude specific cogs from loading, modify the `load_cogs` function in `bot.py`:
```python
load_result = await cog_loader.load_all_cogs(exclude_cogs=['cogs.debug'])
```

## 📋 Requirements

- **Python 3.10+**
- **Discord.py**
- **Flask**
- **Poetry** (optional - for virtual environment)

## 👥 Authors

- **heyu1145** - *Initial work* - [GitHub](https://github.com/heyu1145)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- **GitHub:** [Issues Page](https://github.com/heyu1145/bot/issues)
- **Email:** [heyu12366@outlook.com](mailto:heyu12366@outlook.com)

---

**⭐ If this project helps you, please give it a star!**
