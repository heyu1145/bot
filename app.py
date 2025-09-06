from flask import Flask, jsonify, render_template_string
import threading
import time
import os
import logging
import subprocess
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

app = Flask(__name__)

# Global bot process
bot_process = None

# DARK MODE HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Discord Bot Status</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #ffffff;
        }
        
        .container {
            background: rgba(18, 18, 30, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .status-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            text-shadow: 0 0 20px rgba(79, 195, 247, 0.5);
        }
        
        .status-online {
            color: #4fc3f7;
        }
        
        .status-offline {
            color: #ff5252;
        }
        
        h1 {
            color: #e0f7fa;
            margin-bottom: 10px;
            font-size: 2rem;
            text-shadow: 0 0 10px rgba(79, 195, 247, 0.3);
        }
        
        .status-text {
            font-size: 1.1rem;
            color: #b3e5fc;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(38, 50, 56, 0.6);
            padding: 15px;
            border-radius: 12px;
            border-left: 4px solid #4fc3f7;
            backdrop-filter: blur(5px);
        }
        
        .stat-label {
            font-size: 0.85rem;
            color: #81d4fa;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 1.3rem;
            font-weight: bold;
            color: #e0f7fa;
        }
        
        .bot-status {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin-top: 10px;
            font-size: 1.1rem;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }
        
        .online {
            background: linear-gradient(135deg, #00c853 0%, #64dd17 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 200, 83, 0.4);
        }
        
        .offline {
            background: linear-gradient(135deg, #ff5252 0%, #ff1744 100%);
            color: #fff;
            box-shadow: 0 0 20px rgba(255, 82, 82, 0.4);
        }
        
        .footer {
            margin-top: 30px;
            color: #81d4fa;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .links {
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        .links a {
            color: #4fc3f7;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 15px;
            background: rgba(38, 50, 56, 0.6);
            transition: all 0.3s ease;
            border: 1px solid rgba(79, 195, 247, 0.3);
        }
        
        .links a:hover {
            background: rgba(79, 195, 247, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(79, 195, 247, 0.3);
        }
        
        /* Glow effects */
        .container {
            animation: glow 3s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
            }
            to {
                box-shadow: 0 0 30px rgba(79, 195, 247, 0.5), 
                           0 0 40px rgba(79, 195, 247, 0.2);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="status-icon">
            {{ status_icon }}
        </div>
        
        <h1>Discord Bot Status</h1>
        
        <div class="status-text">
            {{ status_message }}
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Web Server</div>
                <div class="stat-value status-online">ONLINE</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Bot Process</div>
                <div class="stat-value {% if bot_status == 'running' %}status-online{% else %}status-offline{% endif %}">
                    {{ bot_status.upper() }}
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Uptime</div>
                <div class="stat-value">{{ uptime }}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Timestamp</div>
                <div class="stat-value">{{ timestamp }}</div>
            </div>
        </div>
        
        <div class="bot-status {% if bot_status == 'running' %}online{% else %}offline{% endif %}">
            🤖 Bot is {{ bot_status.upper() }}
        </div>
        
        <div class="footer">
            <p>Powered by Flask & Render</p>
            <div class="links">
                <a href="/health">Health Check</a>
                <a href="/ping">Ping</a>
                <a href="/bot-status">Bot Status</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

def format_uptime(seconds):
    """Format uptime to human readable format"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"

# Store server start time
server_start_time = time.time()

@app.route('/')
def home():
    bot_status = "running" if bot_process and bot_process.poll() is None else "stopped"
    uptime = format_uptime(int(time.time() - server_start_time))
    
    status_icon = "🤖" if bot_status == "running" else "⚠️"
    status_message = "Your Discord bot is running successfully!" if bot_status == "running" else "Bot process is currently offline"
    
    return render_template_string(HTML_TEMPLATE, 
        status_icon=status_icon,
        status_message=status_message,
        bot_status=bot_status,
        uptime=uptime,
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/health')
def health():
    # JSON API for Render's health checks (keep this as JSON)
    if bot_process and bot_process.poll() is None:
        return jsonify({
            "status": "healthy", 
            "bot": "running",
            "timestamp": time.time(),
            "uptime": format_uptime(int(time.time() - server_start_time))
        })
    else:
        return jsonify({
            "status": "degraded", 
            "bot": "stopped",
            "timestamp": time.time(),
            "error": "Bot process not running"
        }), 503

@app.route('/ping')
def ping():
    return "pong"

@app.route('/bot-status')
def bot_status():
    # JSON endpoint for bot status
    if bot_process:
        return_code = bot_process.poll()
        if return_code is None:
            return jsonify({
                "bot": "running", 
                "pid": bot_process.pid,
                "uptime": format_uptime(int(time.time() - server_start_time))
            })
        else:
            return jsonify({
                "bot": "stopped", 
                "exit_code": return_code,
                "uptime": format_uptime(int(time.time() - server_start_time))
            })
    return jsonify({"bot": "not_started"})

def start_bot():
    """Start the Discord bot in a separate process"""
    global bot_process
    try:
        logger.info("🚀 Starting Discord bot process...")
        
        # Use the same Python executable and run bot.py
        bot_process = subprocess.Popen(
            [sys.executable, "bot.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"✅ Discord bot process started with PID: {bot_process.pid}")
        
        # Log bot output in background threads
        def log_stdout():
            while True:
                output = bot_process.stdout.readline()
                if output == '' and bot_process.poll() is not None:
                    break
                if output:
                    logger.info(f"BOT: {output.strip()}")
        
        def log_stderr():
            while True:
                error = bot_process.stderr.readline()
                if error == '' and bot_process.poll() is not None:
                    break
                if error:
                    logger.error(f"BOT-ERROR: {error.strip()}")
        
        # Start loggers
        threading.Thread(target=log_stdout, daemon=True).start()
        threading.Thread(target=log_stderr, daemon=True).start()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

def monitor_bot():
    """Monitor and restart bot if it crashes"""
    def monitor():
        while True:
            if bot_process and bot_process.poll() is not None:
                logger.warning("🤖 Bot process stopped, restarting...")
                start_bot()
            time.sleep(30)
    
    threading.Thread(target=monitor, daemon=True).start()

if __name__ == '__main__':
    # Start the bot when the web server starts
    start_bot()
    
    # Start bot monitor
    monitor_bot()
    
    # Start Flask server on Render's assigned port
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Starting web server on port {port}")
    
    # Production server - no debug messages
    from waitress import serve
    serve(app, host='0.0.0.0', port=port, threads=4, _quiet=True)