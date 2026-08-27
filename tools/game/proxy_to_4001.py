"""Lightweight reverse proxy: 127.0.0.1:80 -> 127.0.0.1:4001

Preserves the original Host header (dev.starwing.jp).
Binds only to 127.0.0.1.
Logs all requests and responses for observation.
"""

import http.server
import json
import logging
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BACKEND = "http://127.0.0.1:4001"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 80
LOG_DIR = Path(r"C:\Users\KAHO\Pictures\Starwing\docs\generated")
LOG_FILE = LOG_DIR / "g5_proxy_requests.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("proxy")

requests_log = []


def log_request(method, path, headers, body_len, status, resp_headers, resp_body_len):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "headers": dict(headers),
        "body_length": body_len,
        "response_status": status,
        "response_length": resp_body_len,
    }
    requests_log.append(entry)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


class ProxyHandler(BaseHTTPRequestHandler):
    """Forward all requests to the backend, preserving Host header."""

    def log_message(self, format, *args):
        logger.info(format % args)

    def _proxy(self):
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Build backend URL - strip /mock prefix if present
        backend_path = self.path
        if backend_path.startswith("/mock/"):
            backend_path = backend_path[len("/mock/"):]
        elif backend_path == "/mock":
            backend_path = "/"
        url = f"{BACKEND}/{backend_path.lstrip('/')}"

        # Forward headers, preserving Host as dev.starwing.jp
        fwd_headers = {}
        for key, val in self.headers.items():
            if key.lower() == "host":
                fwd_headers["Host"] = "dev.starwing.jp"
            elif key.lower() not in ("transfer-encoding",):
                fwd_headers[key] = val

        # Make backend request
        try:
            req = urllib.request.Request(
                url, data=body, headers=fwd_headers, method=self.command
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_status = resp.status
                resp_headers = dict(resp.headers)
                resp_body = resp.read()
        except urllib.error.HTTPError as e:
            resp_status = e.code
            resp_headers = dict(e.headers)
            resp_body = e.read()
        except Exception as e:
            resp_status = 502
            resp_headers = {}
            resp_body = json.dumps({"error": str(e)}).encode()

        # Log
        log_request(
            self.command,
            self.path,
            self.headers,
            content_length,
            resp_status,
            resp_headers,
            len(resp_body),
        )

        # Send response to client
        self.send_response(resp_status)
        for key, val in resp_headers.items():
            if key.lower() not in ("transfer-encoding", "connection"):
                self.send_header(key, val)
        self.end_headers()
        self.wfile.write(resp_body)

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_OPTIONS(self):
        self._proxy()

    def do_HEAD(self):
        self._proxy()


class ThreadedHTTPServer(HTTPServer):
    """Handle each request in a new thread."""

    allow_reuse_address = True

    def process_request(self, request, client_address):
        t = threading.Thread(target=self._handle_request_thread, args=(request, client_address))
        t.daemon = True
        t.start()

    def _handle_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)


def run_proxy():
    server = ThreadedHTTPServer((LISTEN_HOST, LISTEN_PORT), ProxyHandler)
    logger.info(f"Proxy listening on {LISTEN_HOST}:{LISTEN_PORT} -> {BACKEND}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logger.info("Proxy stopped")


if __name__ == "__main__":
    run_proxy()
