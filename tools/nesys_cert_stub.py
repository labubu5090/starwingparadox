"""HTTPS stub server for NESYS certificate endpoints.
Listens on port 443 and serves fake cert validation responses.
"""
import json
import pathlib
import ssl
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

CERTS_DIR = pathlib.Path(r"C:\Users\KAHO\Pictures\Starwing\server\certs")


class NesysCertHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        msg = f"[NESYS-CERT] {self.client_address[0]} {format % args}"
        print(msg, flush=True)

    def do_GET(self):
        self._respond(200)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            self.rfile.read(content_length)
        self._respond(200)

    def _respond(self, code):
        path = self.path
        print(f"  {self.command} {path}", flush=True)

        body = json.dumps({
            "status": 0,
            "result": 1,
            "message": "OK",
        }).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(
        str(CERTS_DIR / "nesys_all.pem"),
        str(CERTS_DIR / "nesys_all.key"),
    )

    server = HTTPServer(("0.0.0.0", 443), NesysCertHandler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print("[NESYS-CERT] HTTPS stub on https://0.0.0.0:443 (cert3/cert2.nesys.jp)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
