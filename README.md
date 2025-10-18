___🧪 OFFLINE/TESTING BRANCH - For local development and testing___  
___For cloud deployment, visit the [online branch](https://github.com/heyu1145/bot/tree/online)___

# 🤖 Discord Bot

A feature-rich Discord Bot built with Python.

## 🚀 Features

- **Web Preview** - Flask web dashboard for real-time status monitoring
- **Custom Errors** - Custom error handling for easier debugging
- **Admin & Trusted Users** - Simple permission system for data access
- **Ticket System** - Complete ticket system for user support

## 🏗️ Project Structure

```
bot/
├── app.py              # Flask web dashboard
├── bot.py              # Discord bot core
├── cogs/               # Bot command modules
│   ├── admin.py        # Admin commands
│   ├── tickets.py      # Ticket system
│   ├── events.py       # Event handlers
│   ├── data_management.py # Data handling
│   ├── debug.py        # Debug utilities
│   └── helper.py       # Utility commands
├── utils/              # Utility modules
│   ├── storage.py      # Data management
│   ├── permissions.py  # Access control
│   └── helper.py       # Common utilities
├── config/             # Configuration files
└── customerror.py      # Custom exceptions
```

## 📋 Requirements

- **Python 3.10+**
- **Discord.py**
- **Flask**
- **Poetry** (optional - for virtual environment)

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

## 🔧 Development

### Option 1: Self Development
- **Write custom commands yourself**
- **Benefits:** Maximum customization
- **Requirements:** Advanced programming skills

### Option 2: Get Assistance
- **Open an [issue](https://github.com/heyu1145/bot/issues) for help**
- **Benefits:** Lower programming barrier
- **Limitations:** Less customization control

## 👥 Authors

- **heyu1145** - *Initial work* - [GitHub](https://github.com/heyu1145)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- **GitHub:** [Issues Page](https://github.com/heyu1145/bot/issues)
- **Email:** [heyu12366@outlook.com](mailto:heyu12366@outlook.com)

---

**⭐ If this project helps you, please give it a star!**