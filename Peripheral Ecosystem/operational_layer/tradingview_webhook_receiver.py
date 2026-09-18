import json
import logging
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Configure logging
LOG_DIR = Path(r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\operational_layer\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "tradingview_signals.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

PORT = 8080

class TradingViewWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"status": "error", "message": "Invalid JSON payload"}')
            return

        normalized_signal = {
            "governance": {
                "read_only": True,
                "live_auto_execution": False,
                "order_capability": "NONE",
                "execution_authority": "NONE"
            },
            "received_at": datetime.now(timezone.utc).isoformat(),
            "raw_payload": payload
        }

        logging.info(f"Received Webhook Signal: {json.dumps(normalized_signal)}")
        print(f"\n[WEBHOOK RECEIVED] Normalized & Logged Safely:\n{json.dumps(normalized_signal, indent=2)}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success", "governance": "READ_ONLY"}).encode('utf-8'))

    def log_message(self, format, *args):
        return

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, TradingViewWebhookHandler)
    print("=" * 70)
    print(f"HALAL TRADING OS - TRADINGVIEW WEBHOOK RECEIVER V1")
    print(f"Listening on http://127.0.0.1:{PORT}")
    print("Governance: READ_ONLY = True | ORDER_CAPABILITY = NONE")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Webhook Receiver...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()