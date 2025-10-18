___🌐 ONLINE/PRODUCTION BRANCH - Optimized for cloud deployment___  
___For local development and testing, visit the [offline branch](https://github.com/heyu1145/bot/tree/offline)___

# 🤖 Discord Bot

A feature-rich Discord Bot built with Python.

## 🚀 Features

- **Web Preview** - Flask web dashboard for quick status monitoring
- **Custom Errors** - Custom error handling for easier debugging
- **Admin and Trusted Users** - Simple permission system for data access
- **Ticket System** - Feature-rich ticket system for administration

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
- **Poetry**

## ⚙️ Installation

### Prerequisites
- A cloud platform (Replit, Heroku, etc.)
- Your bot token and user ID

### How to Get Your Bot Token and User ID

**Bot Token:**
1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" or select an existing one
3. Go to "Bot" → "Token"
4. Click "Reset Token" and copy your new token
5. **⚠️ Never share your token with anyone!**

**User ID:**
1. Open Discord
2. Right-click your profile → "Copy User ID"

### Setup Steps

1. **Environment Variables:**
```bash
TOKEN=your_bot_token_here
OWNER_USER_ID=your_user_id_here
```

2. **Install Dependencies:**
```bash
poetry install
```

3. **Start the Bot:**
```bash
python3 app.py
```
**Note:** Start `app.py` (not `bot.py`) for web preview functionality.

## 🔧 Self Development

### Option 1: Develop Yourself
- **Compile commands by yourself**
- **Benefits:** High customization
- **Requirements:** Advanced programming skills

### Option 2: Get Help
- **Discuss with me in [Issues](https://github.com/heyu1145/bot/issues)**
- **Benefits:** Lower programming requirements
- **Limitations:** Less customization

## 👥 Authors

- **heyu1145** - *Initial work* - [GitHub](https://github.com/heyu1145)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- **GitHub:** [Issues Page](https://github.com/heyu1145/bot/issues)
- **Email:** [heyu12366@outlook.com](mailto:heyu12366@outlook.com)

---

**⭐ Please star this repo if you find it helpful!**