from waitress import serve
from flask import Flask, jsonify
from threading import Thread
import time
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('keep_alive')

app = Flask('')

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "message": "Discord Bot is running!",
        "timestamp": time.time(),
        "service": "waitress_wsgi"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/status')
def status():
    return jsonify({"status": "active", "service": "discord_bot"})

def run_waitress():
    try:
        logger.info("Starting Waitress WSGI server on port 8080...")
        # Waitress is production-ready and completely silent by default
        serve(app, host='0.0.0.0', port=8080, threads=4, _quiet=True)
    except Exception as e:
        logger.error(f"Waitress server error: {e}")

def keep_alive():
    try:
        wsgi_thread = Thread(target=run_waitress, daemon=True)
        wsgi_thread.start()
        logger.info("Waitress WSGI server started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start WSGI server: {e}")
        return False