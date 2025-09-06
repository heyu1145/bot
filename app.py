from flask import Flask, jsonify
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

@app.route('/')
def home():
    bot_status = "running" if bot_process and bot_process.poll() is None else "stopped"
    return jsonify({
        "status": "online",
        "service": "discord_bot_web_server",
        "bot_status": bot_status,
        "timestamp": time.time(),
        "message": "Web server is running - Bot keep-alive service"
    })

@app.route('/health')
def health():
    # Critical health check - Render uses this to verify the service is alive
    if bot_process and bot_process.poll() is None:
        return jsonify({
            "status": "healthy", 
            "bot": "running",
            "timestamp": time.time()
        })
    else:
        return jsonify({
            "status": "degraded", 
            "bot": "stopped",
            "timestamp": time.time()
        }), 503

@app.route('/ping')
def ping():
    return "pong"

@app.route('/bot-status')
def bot_status():
    if bot_process:
        return_code = bot_process.poll()
        if return_code is None:
            return jsonify({"bot": "running", "pid": bot_process.pid})
        else:
            return jsonify({"bot": "stopped", "exit_code": return_code})
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