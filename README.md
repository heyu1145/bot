# 🤖 Discord Bot with Vue.js Dashboard

A feature-rich Discord Bot built with Python, featuring a modern Vue.js dashboard for real-time monitoring and control.

## 🚀 Features

- **Vue.js Dashboard** - Modern web interface for real-time bot status monitoring and control
- **Auto-Cog Loading** - Automatically discovers and loads all extension modules in the cogs directory
- **FastAPI Service** - RESTful API for frontend integration and external control
- **System Monitoring** - Real-time CPU, memory, and disk usage tracking
- **Custom Errors** - Custom error handling for easier debugging
- **Dynamic Activity** - Support for multiple activity types with time-based switching

## 🛠️ Tech Stack

### Backend
- **Python 3.12+**
- **discord.py 2.6.2** - Discord API wrapper
- **FastAPI 0.125.0** - Modern web framework
- **Poetry** - Dependency management

### Frontend
- **Vue 3.5.26** - Progressive JavaScript framework
- **TypeScript 5.9.3** - Type-safe development
- **Vite 7.3.0** - Next-generation frontend tooling
- **Pinia 3.0.4** - State management
- **Vue Router 4.6.4** - Routing

## 🏗️ Project Structure

```text
.
├── bot/                    # Python backend
│   ├── main.py            # Discord bot entry point
│   ├── config/            # Configuration files
│   ├── cogs/              # Bot command modules
│   │   ├── channels.py    # Channel management
│   │   ├── messages.py    # Message handling
│   │   ├── events.py      # Event management
│   │   ├── embeds.py      # Embed messages
│   │   └── cogs_finder.py # Auto-cog loading system
│   ├── utils/             # Utility modules
│   │   ├── service.py     # FastAPI service
│   │   ├── logger.py      # Logging utilities
│   │   └── hex_helper.py  # Color conversion
│   └── custom_errors.py   # Custom exceptions
├── front/                 # Vue.js frontend
│   ├── src/
│   │   ├── App.vue        # Root component
│   │   ├── main.ts        # Entry point
│   │   ├── router/        # Vue Router configuration
│   │   ├── stores/        # Pinia stores
│   │   └── views/         # Page components
│   └── vite.config.ts     # Vite configuration
├── pyproject.toml         # Python dependencies (Poetry)
├── requirements.txt       # Python dependencies ( pip, uv, etc. )
├── CHANGELOG.md           # Version history
└── README.md              # This file
```

## ⚙️ Installation

### Prerequisites

- Python 3.12 or higher
- Node.js 20.19.0 or higher
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

### Backend Installation

#### Option A: Using Poetry (Recommended)

```bash
# Install Poetry if not available
pip install poetry

# Create virtual environment and install dependencies
poetry install

# Activate virtual environment
poetry shell
```

#### Option B: Using pip

```bash
# Install dependencies
pip install -r requirements.txt
```

### Frontend Installation

```bash
cd front

# Install dependencies
pnpm install
# or
npm install
```

### Environment Configuration

Create a `.env` file in the project root:

```env
TOKEN=your_discord_bot_token_here
```

## 🚀 Running the Bot

### Start Backend

```bash
# From project root
python bot/main.py
```

The FastAPI service will run on `http://localhost:4100`

### Start Frontend (Development)

```bash
cd front

# Start development server
pnpm dev
# or
npm run dev
```

The Vue dashboard will run on `http://localhost:3000`

## 🎮 Discord Commands

Use the `/help` command in Discord to view all available commands.

The help command automatically discovers and displays all commands from:
- Built-in commands (ping, help, listcogs)
- All loaded cogs (channels, messages, events, embeds)

Simply type `/help` in any server where the bot is active to see the complete command list with descriptions.

## 🔌 API Endpoints

The FastAPI service provides the following endpoints:

### `GET /ping`
Health check endpoint.

**Response:**
```json
{
  "reply": "pong!",
  "timestamp": "timestamp",
  "client_host": "host of client",
  "random_bytes": "8 random string"
}
```

### `POST /bot-control` ⚠️ Work in Progress
Bot control interface (currently under development).

**Request:**
```json
{
  "message": "your message"
}
```

**Response:**
```json
{
  "reply": "Received your message: your message"
}
```

### `GET /status`
System status information including CPU, memory, disk usage, and bot latency.

**Response:**
```json
{
  "bot_status": "running",
  "disk_usage": {...},
  "memory_usage": {...},
  "cpu_usage": 15.5,
  "thread_count": 8,
  "bot_latency_ms": 250
}
```

### `POST /`
Special teapot endpoint (HTTP 418).

### `GET /`
Root endpoint with welcome message.

## 🔧 Auto-Cog Loading System

The bot features an automatic cog loading system that dynamically discovers and loads all extension modules in the `bot/cogs/` directory.

### How It Works

- Automatically discovers all `.py` files in the `bot/cogs/` directory (excluding files starting with `_` and `it self` (`cogs_finder.py`) )
- Loads each module as a cog extension when the bot starts
- Provides detailed logging of loading status and errors

### Adding New Cogs

To add new functionality:
1. Create a new Python file in the `bot/cogs/` directory
2. Follow the standard cog structure with a setup function
3. The bot will automatically discover and load it on restart

## 📋 Requirements

- **Python**: 3.12 or higher
- **Node.js**: 20.19.0 or higher
- **Discord Bot Token**
- **Poetry** (optional - for virtual environment)

## 👥 Authors

- **heyu1145** - *Initial work* - [GitHub](https://github.com/heyu1145)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## 💬 Support

- **GitHub:** [Issues Page](https://github.com/heyu1145/bot/issues)
- **Email:** [heyu12366@outlook.com](mailto:heyu12366@outlook.com)

---

**⭐ If this project helps you, please give it a star!**


