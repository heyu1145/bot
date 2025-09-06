from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HTTPService')
logger.setLevel(logging.INFO)

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is alive!')
    
    def log_message(self, format, *args):
        # Silence the server logs
        return

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    logger.info("✅ Keep-alive server started on port 8080")
    server.serve_forever()

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()