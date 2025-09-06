from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import json
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('keep_alive')

# Global variables to track bot status
bot_status = {
    "online": False,
    "start_time": None,
    "servers": 0,
    "commands_loaded": 0,
    "users": 0,
    "last_update": None
}

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Calculate uptime
            uptime = "N/A"
            if bot_status["start_time"]:
                uptime_seconds = int(time.time() - bot_status["start_time"])
                hours, remainder = divmod(uptime_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime = f"{hours}h {minutes}m {seconds}s"
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Discord Bot Status</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 20px;
                        color: #333;
                    }}
                    .container {{
                        max-width: 1000px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 15px;
                        padding: 30px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .status-indicator {{
                        display: inline-block;
                        width: 15px;
                        height: 15px;
                        border-radius: 50%;
                        margin-right: 10px;
                        background: {'#4CAF50' if bot_status['online'] else '#f44336'};
                    }}
                    .stats-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }}
                    .stat-card {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        border-left: 4px solid #667eea;
                    }}
                    .stat-number {{
                        font-size: 2.5em;
                        font-weight: bold;
                        color: #667eea;
                        margin: 10px 0;
                    }}
                    .stat-label {{
                        font-size: 0.9em;
                        color: #666;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }}
                    .features {{
                        background: #e8f5e8;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    }}
                    .feature-list {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                    }}
                    .feature-item {{
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 0.9em;
                    }}
                    h1 {{
                        color: #333;
                        margin-bottom: 10px;
                    }}
                    .last-update {{
                        color: #666;
                        font-size: 0.9em;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Discord Bot Status</h1>
                        <div class="status">
                            <span class="status-indicator"></span>
                            Status: <strong>{'ONLINE' if bot_status['online'] else 'OFFLINE'}</strong>
                        </div>
                        <div class="last-update">
                            Last updated: {bot_status['last_update'] or 'N/A'}
                        </div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Servers</div>
                            <div class="stat-number">{bot_status['servers']}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Users</div>
                            <div class="stat-number">{bot_status['users']}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Commands Loaded</div>
                            <div class="stat-number">{bot_status['commands_loaded']}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Uptime</div>
                            <div class="stat-number">{uptime}</div>
                        </div>
                    </div>

                    <div class="features">
                        <h2>🎯 Bot Features</h2>
                        <div class="feature-list">
                            <div class="feature-item">🎫 Multi-Ticket System</div>
                            <div class="feature-item">📅 Smart Event Management</div>
                            <div class="feature-item">🔐 Advanced Permissions</div>
                            <div class="feature-item">💾 Data Management</div>
                            <div class="feature-item">📊 Analytics & Stats</div>
                            <div class="feature-item">⏰ Timezone Support</div>
                        </div>
                    </div>

                    <div class="footer">
                        <p>Powered by Discord.py • Running on Render</p>
                        <p>Bot started at: {datetime.fromtimestamp(bot_status['start_time']).strftime('%Y-%m-%d %H:%M:%S') if bot_status['start_time'] else 'N/A'}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(bot_status).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 - Not Found')
    
    def log_message(self, format, *args):
        logger.info(f"HTTP {self.command} {self.path} - {args}")

def update_bot_status(online=False, servers=0, commands_loaded=0, users=0):
    bot_status.update({
        "online": online,
        "servers": servers,
        "commands_loaded": commands_loaded,
        "users": users,
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    if online and not bot_status["start_time"]:
        bot_status["start_time"] = time.time()
    logger.info(f"Updated bot status: {bot_status}")

def keep_alive():
    server = HTTPServer(('0.0.0.0', 8080), StatusHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    logger.info("🌐 Status server started on http://0.0.0.0:8080")