from flask import Flask, jsonify, render_template_string
import threading
import time
import os
import logging
import subprocess
import sys
import psutil
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

app = Flask(__name__)

# Global bot process
bot_process = None

# DARK MODE HTML template (Updated without health check button)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Discord Bot Status Dashboard</title>
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
            max-width: 600px;
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
            font-size: 2.2rem;
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
            text-align: center;
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
        
        .stat-subvalue {
            font-size: 0.9rem;
            color: #b3e5fc;
            margin-top: 3px;
        }
        
        .bot-status {
            display: inline-block;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: bold;
            margin-top: 15px;
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
        
        .system-info {
            background: rgba(38, 50, 56, 0.6);
            padding: 15px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 4px solid #ff9800;
        }
        
        .system-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .system-stat {
            text-align: center;
        }
        
        .system-label {
            font-size: 0.8rem;
            color: #ffcc80;
            margin-bottom: 3px;
        }
        
        .system-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #fff;
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
        
        .loading {
            color: #ff9800;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="status-icon">
            {{ status_icon }}
        </div>
        
        <h1>Discord Bot Dashboard</h1>
        
        <div class="status-text">
            {{ status_message }}
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Web Server</div>
                <div class="stat-value status-online">ONLINE</div>
                <div class="stat-subvalue">Port: {{ port }}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Bot Process</div>
                <div class="stat-value {% if bot_status == 'running' %}status-online{% else %}status-offline{% endif %}">
                    {{ bot_status.upper() }}
                </div>
                <div class="stat-subvalue">PID: {{ bot_pid }}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Uptime</div>
                <div class="stat-value">{{ uptime }}</div>
                <div class="stat-subvalue">Since: {{ start_time }}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">System</div>
                <div class="stat-value">{{ cpu_usage }}% CPU</div>
                <div class="stat-subvalue">{{ memory_usage }}% RAM</div>
            </div>
        </div>
        
        <div class="system-info">
            <div class="stat-label">System Resources</div>
            <div class="system-stats">
                <div class="system-stat">
                    <div class="system-label">CPU Cores</div>
                    <div class="system-value">{{ cpu_cores }}</div>
                </div>
                <div class="system-stat">
                    <div class="system-label">Memory</div>
                    <div class="system-value">{{ memory_mb }} MB</div>
                </div>
                <div class="system-stat">
                    <div class="system-label">Threads</div>
                    <div class="system-value">{{ thread_count }}</div>
                </div>
                <div class="system-stat">
                    <div class="system-label">Disk</div>
                    <div class="system-value">{{ disk_usage }}%</div>
                </div>
            </div>
        </div>
        
        <div class="bot-status {% if bot_status == 'running' %}online{% else %}offline{% endif %}">
            🤖 Bot is {{ bot_status.upper() }}
        </div>
        
        <div class="footer">
            <p>Powered by Flask & Render • {{ response_time }}ms response</p>
            <div class="links">
                <a href="/ping">Ping Test</a>
                <a href="/bot-status">JSON API</a>
                <a href="/health">Health Check</a>
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

def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_cores = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = round(memory.used / (1024 * 1024))
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Process info
        current_process = psutil.Process()
        thread_count = current_process.num_threads()
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_cores': cpu_cores,
            'memory_percent': memory_percent,
            'memory_mb': memory_mb,
            'disk_percent': disk_percent,
            'thread_count': thread_count
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {
            'cpu_percent': 0,
            'cpu_cores': 0,
            'memory_percent': 0,
            'memory_mb': 0,
            'disk_percent': 0,
            'thread_count': 0
        }

# Store server start time
server_start_time = time.time()
server_start_time_str = time.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def home():
    start_time = time.time()
    
    bot_status = "running" if bot_process and bot_process.poll() is None else "stopped"
    bot_pid = bot_process.pid if bot_process and bot_process.poll() is None else "N/A"
    uptime = format_uptime(int(time.time() - server_start_time))
    
    status_icon = "🤖" if bot_status == "running" else "⚠️"
    status_message = "Your Discord bot is running successfully!" if bot_status == "running" else "Bot process is currently offline"
    
    # Get system statistics
    system_stats = get_system_stats()
    
    # Calculate response time
    response_time = round((time.time() - start_time) * 1000, 1)
    
    return render_template_string(HTML_TEMPLATE, 
        status_icon=status_icon,
        status_message=status_message,
        bot_status=bot_status,
        bot_pid=bot_pid,
        uptime=uptime,
        start_time=server_start_time_str,
        port=os.environ.get('PORT', 10000),
        cpu_usage=system_stats['cpu_percent'],
        memory_usage=system_stats['memory_percent'],
        cpu_cores=system_stats['cpu_cores'],
        memory_mb=system_stats['memory_mb'],
        disk_usage=system_stats['disk_percent'],
        thread_count=system_stats['thread_count'],
        response_time=response_time
    )

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    if bot_process and bot_process.poll() is None:
        return jsonify({
            "status": "healthy", 
            "bot": "running",
            "timestamp": time.time(),
            "uptime": format_uptime(int(time.time() - server_start_time)),
            "system": get_system_stats()
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
    """Enhanced ping endpoint"""
    start_time = time.time()
    
    # Measure bot response time
    bot_response_time = round((time.time() - start_time) * 1000, 1)
    
    # Get system stats
    system_stats = get_system_stats()
    
    return jsonify({
        "status": "pong",
        "timestamp": time.time(),
        "response_time_ms": bot_response_time,
        "system": system_stats,
        "bot_status": "running" if bot_process and bot_process.poll() is None else "stopped",
        "uptime": format_uptime(int(time.time() - server_start_time))
    })

@app.route('/bot-status')
def bot_status():
    """Comprehensive bot status API"""
    system_stats = get_system_stats()
    
    if bot_process:
        return_code = bot_process.poll()
        if return_code is None:
            return jsonify({
                "status": "running", 
                "process": {
                    "pid": bot_process.pid,
                    "uptime": format_uptime(int(time.time() - server_start_time)),
                    "start_time": server_start_time_str
                },
                "system": system_stats,
                "resources": {
                    "cpu_cores": system_stats['cpu_cores'],
                    "memory_used_mb": system_stats['memory_mb'],
                    "thread_count": system_stats['thread_count']
                },
                "timestamp": time.time(),
                "message": "Bot is running normally"
            })
        else:
            return jsonify({
                "status": "stopped", 
                "exit_code": return_code,
                "system": system_stats,
                "uptime": format_uptime(int(time.time() - server_start_time)),
                "timestamp": time.time(),
                "error": "Bot process has stopped"
            })
    return jsonify({
        "status": "not_started",
        "system": system_stats,
        "timestamp": time.time(),
        "message": "Bot process has not been started"
    })

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
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        logger.info(f"✅ Discord bot process started with PID: {bot_process.pid}")
        
        # Log bot output in background threads
        def log_stdout():
            while True:
                if bot_process.poll() is not None:
                    break
                output = bot_process.stdout.readline()
                if output:
                    logger.info(f"BOT: {output.strip()}")
        
        def log_stderr():
            while True:
                if bot_process.poll() is not None:
                    break
                error = bot_process.stderr.readline()
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

def start_ping_service():
    """Ping the service periodically to keep it awake"""
    def ping_self():
        while True:
            try:
                base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000')
                response = requests.get(f"{base_url}/ping", timeout=10)
                logger.info(f"🔄 Self-ping successful: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Self-ping failed: {e}")
            time.sleep(300)  # Ping every 5 minutes
    
    threading.Thread(target=ping_self, daemon=True).start()

if __name__ == '__main__':
    # Start the bot when the web server starts
    start_bot()
    
    # Start bot monitor
    monitor_bot()
    
    # Start self-ping service to keep awake
    start_ping_service()
    
    # Start Flask server on Render's assigned port
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🌐 Starting web server on port {port}")
    
    # Use Waitress for production if available, else use Flask dev server
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=port, threads=4, _quiet=True)
    except ImportError:
        logger.warning("⚠️ Waitress not found, using Flask development server")
        app.run(host='0.0.0.0', port=port, debug=False)