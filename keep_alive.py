from flask import Flask, jsonify
from threading import Thread
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('keep_alive')

app = Flask('')

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "message": "Discord Bot is running!",
        "timestamp": time.time()
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

def run_flask():
    try:
        logger.info("Starting Flask server on port 8080...")
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def keep_alive():
    try:
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask keep-alive server started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start keep-alive server: {e}")
        return False