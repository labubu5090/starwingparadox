"""G30 reverse proxy using only stdlib."""
import http.server
import socketserver
import urllib.request
import logging
import uuid
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("g30_proxy")

PROXY_PORT = 80
TARGET_BASE = "http://127.0.0.1:4001"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        correlation_id = str(uuid.uuid4())[:8]
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # Strip /mock prefix: game sends /mock/matching/server -> /matching/server
        upstream_path = self.path
        if upstream_path.startswith("/mock"):
            upstream_path = upstream_path[5:]  # strip "/mock"
        
        target_url = f"{TARGET_BASE}{upstream_path}"
        logger.info("[%s] PROXY %s %s -> %s (%d bytes)", correlation_id, self.command, self.path, target_url, len(body))
        
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'transfer-encoding')}
        headers['Host'] = '127.0.0.1:4001'
        
        req = urllib.request.Request(target_url, data=body, headers=headers, method='POST')
        logger.info("[%s] Upstream request: %s %s", correlation_id, req.method, req.full_url)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read()
                logger.info("[%s] Response: %d %d bytes", correlation_id, resp.status, len(resp_body))
                
                self.send_response(resp.status)
                for key, value in resp.getheaders():
                    if key.lower() not in ('transfer-encoding', 'content-length'):
                        self.send_header(key, value)
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except Exception as e:
            logger.error("[%s] Proxy error: %s", correlation_id, e)
            error_body = f"Proxy error: {e}".encode()
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
    
    def do_GET(self):
        self.do_POST()
    
    def log_message(self, format, *args):
        logger.info(format, *args)

if __name__ == "__main__":
    logger.info("G30 proxy starting on port %d", PROXY_PORT)
    with socketserver.TCPServer(("127.0.0.1", PROXY_PORT), ProxyHandler) as httpd:
        httpd.serve_forever()
