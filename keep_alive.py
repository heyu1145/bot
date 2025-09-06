import threading
from flask import Flask, jsonify
import requests
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "message": "Discord Bot is running!"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

def run_flask():
    try:
        # Use a more standard port for Render
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def keep_alive():
    # Start Flask server in a thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Flask keep-alive server started")
    
    # If you want to ping yourself periodically (optional)
    def ping_self():
        while True:
            try:
                # This is the URL Render provides for your app
                response = requests.get('https://bot-cjlc.onrender.com/health')
                logger.info(f"Self-ping response: {response.status_code}")
            except Exception as e:
                logger.error(f"Self-ping failed: {e}")
            time.sleep(300)  # Ping every 5 minutes
    
    ping_thread = threading.Thread(target=ping_self)
    ping_thread.daemon = True
    ping_thread.start()

if __name__ == "__main__":
    keep_alive()
    # Keep the main thread alive
    while True:
        time.sleep(1)