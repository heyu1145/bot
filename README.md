# Discord Event Manager Bot

A Discord bot that allows server members to create, delete, and list events using slash commands.

## Setup Instructions (Replit)

1. **Create a new Replit project** with Python template
2. **Create these files**:
   - main.py (main bot code)
   - keep_alive.py (to keep the bot running)
   - .env (for your Discord token)

3. **Install required packages** in Replit's shell:
   ```
   pip install discord.py python-dotenv pytz flask
   ```

4. **Set up your .env file**:
   ```
   DISCORD_TOKEN=your_actual_discord_bot_token_here
   ```

5. **Create a Discord Bot** in the [Discord Developer Portal](https://discord.com/developers/applications):
   - Go to the Applications page
   - Create a new application
   - Go to the "Bot" tab and click "Add Bot"
   - Copy the bot token and paste it in .env
   - Enable the "Server Members" intent in the bot settings

6. **Invite the bot to your server** with these permissions:
   - Manage Events
   - Send Messages
   - Use Slash Commands

7. **Run the bot** by clicking the "Run" button in Replit

## Available Commands

- `/create_event` - Create a new event with name, description, time, and location
- `/delete_event` - Delete an event using its ID
- `/list_events` - Show all upcoming events with their IDs

## Notes

- The bot uses UTC timezone by default. You can change this in main.py
- The keep_alive.py file creates a web server to keep your bot running on Replit
- For 24/7 uptime, you can use a service like UptimeRobot to ping your Replit web server
   