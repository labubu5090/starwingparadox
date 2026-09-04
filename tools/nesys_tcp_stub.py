"""NESYS TCP Stub Server for port 1042.

Emulates NesysService.exe on TCP port 1042 using the same LCOMMAND/SCOMMAND
protocol as the named pipe stub. This makes the game think NesysService is
running, which triggers the HTTP cert validation path (bNesysServerLive).
"""
import struct
import socket
import ssl
import os
import sys
import threading
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

HEADER_SIZE = 8

LCOMMAND_ERROR = 0x00
LCOMMAND_CLIENT_START = 0x01
LCOMMAND_CONNECT_REQUEST = 0x02
LCOMMAND_DISCONNECT_REQUEST = 0x03
LCOMMAND_GAME_START_REQUEST = 0x04
LCOMMAND_GAME_END_REQUEST = 0x05
LCOMMAND_GAME_CONTINUE_REQUEST = 0x06
LCOMMAND_EVENT_DOWNLOAD_REQUEST = 0x07
LCOMMAND_EVENT_REQUEST_REQUEST = 0x08
LCOMMAND_CARD_SELECT_REQUEST = 0x09
LCOMMAND_CARD_INSERT_REQUEST = 0x0A
LCOMMAND_CARD_UPDATE_REQUEST = 0x0B
LCOMMAND_CARD_BUYS_ITEM_REQUEST = 0x0C
LCOMMAND_CARD_TAKEOVER_REQUEST = 0x0D
LCOMMAND_CARD_FORCE_TAKEOVER_REQ = 0x0E
LCOMMAND_CARD_DECREASE_REQUEST = 0x0F
LCOMMAND_CARD_REISSUE_TEST_REQUE = 0x10
LCOMMAND_CARD_REISSUE_REQUEST = 0x11
LCOMMAND_CARD_PLAYED_LIST_REQUES = 0x12
LCOMMAND_RANKING_DATA_REQUEST = 0x13
LCOMMAND_LOCALNW_INFO_REQUEST = 0x14
LCOMMAND_GLOBALADDR_REQUEST = 0x15
LCOMMAND_ECHO_REQUEST = 0x16
LCOMMAND_ADAPTER_INFO_REQUEST = 0x17
LCOMMAND_SERVICE_VERSION_REQUEST = 0x18
LCOMMAND_DHCP_RENEW_REQUEST = 0x19
LCOMMAND_HTTPACCESS_GET_REQUEST = 0x1A
LCOMMAND_HTTPACCESS_POST_REQUEST = 0x1B
LCOMMAND_UPLOAD_CONFIG_REQUEST = 0x1C
LCOMMAND_INCOME_START_REQUEST = 0x1D
LCOMMAND_INCOME_END_REQUEST = 0x1E
LCOMMAND_INCOME_CONTINUE_REQUEST = 0x1F
LCOMMAND_SET_INCOME_MODE_REQUEST = 0x20
LCOMMAND_DESTROY_MY_SERVICE = 0x21
LCOMMAND_INCOME_POINT_REQUEST = 0x22
LCOMMAND_GAMESTATUS_RESET_REQUEST = 0x23
LCOMMAND_ROW_EVENTDATA_LIST_REQUEST = 0x24
LCOMMAND_SHOPPING_REQUEST = 0x25
LCOMMAND_FREE_TICKET_REQUEST = 0x26
LCOMMAND_GAME_FREE_START_REQUEST = 0x27
LCOMMAND_GAME_FREE_END_REQUEST = 0x28
LCOMMAND_INCOME_FREE_START_REQUEST = 0x29
LCOMMAND_INCOME_FREE_END_REQUEST = 0x2A
LCOMMAND_CLIENT_END = 0x2B
LCOMMAND_INCOME_FREE_CONTINUE_REQUEST = 0x2C

SCOMMAND_NW_ERROR = 0x101
SCOMMAND_CERT_ERROR = 0x102
SCOMMAND_NWRECOVER_NOTICE = 0x103
SCOMMAND_SOON_MAINTENANCE_NOTICE = 0x104
SCOMMAND_LINKUP_NOTICE = 0x105
SCOMMAND_LINKLOCAL_MODE_NOTICE = 0x106
SCOMMAND_CERT_INIT_NOTICE = 0x107
SCOMMAND_CERT_REGULAR_NOTICE = 0x108
SCOMMAND_EFFECTIVE_EVENT_NOTICE = 0x109
SCOMMAND_INEFFECTIVE_EVENT_NOTICE = 0x10A
SCOMMAND_DHCP_RENEW_START = 0x10B
SCOMMAND_DHCP_COMPLETE_NOTICE = 0x10C
SCOMMAND_CLIENT_START_REPLY = 0x10D
SCOMMAND_CONNECT_REPLY = 0x10E
SCOMMAND_DISCONNECT_REPLY = 0x10F
SCOMMAND_GAME_STATUS_REPLY = 0x110
SCOMMAND_CARD_SELECT_REPLY = 0x111
SCOMMAND_CARD_INSERT_REPLY = 0x112
SCOMMAND_CARD_UPDATE_REPLY = 0x113
SCOMMAND_CARD_BUYS_ITEM_REPLY = 0x114
SCOMMAND_CARD_TAKEOVER_REPLY = 0x115
SCOMMAND_CARD_DECREASE_REPLY = 0x116
SCOMMAND_CARD_REISSUE_TEST_REPLY = 0x117
SCOMMAND_CARD_REISSUE_REPLY = 0x118
SCOMMAND_CARD_PLAYED_LIST_REPLY = 0x119
SCOMMAND_RANKING_DATA_REPLY = 0x11A
SCOMMAND_LOCALNW_INFO_REPLY = 0x11B
SCOMMAND_LOCALNW_INFO_NOTICE = 0x11C
SCOMMAND_GLOBALADDR_REPLY = 0x11D
SCOMMAND_ECHO_REPLY = 0x11E
SCOMMAND_ADAPTER_INFO_REPLY = 0x11F
SCOMMAND_SERVICE_VERSION_REPLY = 0x120
SCOMMAND_HTTPACCESS_START = 0x121
SCOMMAND_HTTPACCESS_REPLY = 0x122
SCOMMAND_UPLOAD_CONFIG_REPLY = 0x123
SCOMMAND_INCOME_STATUS_REPLY = 0x124
SCOMMAND_SET_INCOME_MODE_REPLY = 0x125
SCOMMAND_DESTROY_MY_SERVICE_REPLY = 0x126
SCOMMAND_GAMESTATUS_RESET_REPLY = 0x127
SCOMMAND_ROW_EVENTDATA_LIST_REPLY = 0x128
SCOMMAND_SHOPPING_REPLY = 0x129
SCOMMAND_FREE_TICKET_REPLY = 0x12A
SCOMMAND_CLIENT_END_REPLY = 0x12B

DEFAULT_CARD_ID = 7020392000000000

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("nesys-tcp")

from tools.nesys_trace import TraceLogger as _TraceLogger
_trace = _TraceLogger("[TCP1042]")


def pack_message(cmd_id: int, payload: bytes = b"") -> bytes:
    return struct.pack("<II", cmd_id, len(payload)) + payload


def unpack_header(data: bytes) -> tuple[int, int]:
    if len(data) < HEADER_SIZE:
        return 0, 0
    cmd_id, data_size = struct.unpack("<II", data[:HEADER_SIZE])
    return cmd_id, data_size


def recv_exact(sock: socket.socket, n: int) -> bytes | None:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)


def recv_message(sock: socket.socket) -> tuple[int, bytes, bytes] | None:
    header = recv_exact(sock, HEADER_SIZE)
    if not header:
        return None
    cmd_id, data_size = unpack_header(header)
    payload = b""
    if data_size > 0:
        p = recv_exact(sock, data_size)
        if not p:
            return None
        payload = p
    return cmd_id, payload, header + payload


def build_cert_init_notice(card_id: int) -> bytes:
    tenpo_id = 119
    tenpo_name = "Arcademachine".encode("utf-8").ljust(31, b"\x00")[:31]
    address = "Tokyo".encode("utf-8").ljust(33, b"\x00")[:33]
    ticket = "none".encode("utf-8").ljust(33, b"\x00")[:33]
    prefecture = "US".encode("utf-8").ljust(23, b"\x00")[:23]
    img_path = b"\x00" * 1024
    host = f"card_id={card_id},relay_addr=127.0.0.1,relay_port=80".encode("utf-8")

    payload = bytearray()
    payload.extend(struct.pack("<I", tenpo_id))
    payload.extend(tenpo_name)
    payload.extend(address)
    payload.extend(ticket)
    payload.extend(prefecture)
    payload.extend(struct.pack("<I", tenpo_id))
    payload.extend(img_path)
    payload.extend(struct.pack("<I", len(host)))
    payload.extend(host)
    return pack_message(SCOMMAND_CERT_INIT_NOTICE, bytes(payload))


def build_localnw_info_notice() -> bytes:
    net_mac = b"001C42888475\x00\x00\x00\x00"
    ip_addr = b"192.168.1.100\x00\x00\x00"
    ip_gate = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_dns = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_unkn = b"\x7c\x15\x00\x00\x00\x00\x00\x00"
    iface_data = net_mac + ip_addr + ip_gate + ip_dns + ip_unkn
    payload = struct.pack("<I", 1) + struct.pack("<I", len(iface_data)) + iface_data
    return pack_message(SCOMMAND_LOCALNW_INFO_NOTICE, payload)


def build_adapter_info_reply() -> bytes:
    ip_gate = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_addr = b"192.168.1.100\x00\x00\x00"
    ip_mask = b"255.255.255.0\x00\x00\x00"
    ip_dns1 = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_dns2 = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_mac = b"001C42888475\x00\x00\x00\x00"
    zero16 = b"\x00" * 16
    payload = bytearray()
    payload.extend(struct.pack("<I", 1))
    payload.extend(struct.pack("<I", 1))
    for addr in [ip_gate, zero16, ip_addr, zero16, ip_mask, zero16, ip_dns1, zero16, ip_dns2, zero16, ip_mac, zero16]:
        payload.extend(addr)
    payload.extend(zero16)
    payload.extend(zero16)
    return pack_message(SCOMMAND_ADAPTER_INFO_REPLY, bytes(payload))


def build_globaladdr_reply() -> bytes:
    global_addr = b"10.79.0.41"
    payload = struct.pack("<I", 0x0018)
    payload += struct.pack("<I", 0x0001)
    payload += struct.pack("<I", 0x01A6)
    payload += global_addr.ljust(16, b"\x00")
    return pack_message(SCOMMAND_GLOBALADDR_REPLY, payload)


CARD_ID = DEFAULT_CARD_ID


def handle_client(conn: socket.socket, addr: tuple) -> None:
    global CARD_ID
    log.info("Client connected: %s:%d", addr[0], addr[1])
    conn_id = _trace.conn_open()

    _orig_sendall = conn.sendall
    def _traced_sendall(data: bytes, *a, **kw):
        try:
            _trace.tx(conn_id, data)
        except Exception:
            pass
        return _orig_sendall(data, *a, **kw)
    conn.sendall = _traced_sendall  # type: ignore[assignment]

    try:
        while True:
            msg = recv_message(conn)
            if msg is None:
                break
            cmd_id, payload, client_data = msg
            log.info("RECV: cmd=0x%03X size=%d", cmd_id, len(payload))
            try:
                _trace.rx(conn_id, client_data)
            except Exception:
                pass

            if cmd_id == LCOMMAND_CLIENT_START:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CLIENT_START_REPLY, b"\x00" * 4))

            elif cmd_id == LCOMMAND_CONNECT_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CONNECT_REPLY, b"\x00" * 4))
                time.sleep(0.03)
                conn.sendall(pack_message(SCOMMAND_NWRECOVER_NOTICE, b""))
                time.sleep(0.03)
                conn.sendall(build_cert_init_notice(CARD_ID))
                time.sleep(0.03)
                conn.sendall(pack_message(SCOMMAND_LINKUP_NOTICE, b""))
                time.sleep(0.03)
                conn.sendall(pack_message(SCOMMAND_CERT_REGULAR_NOTICE, struct.pack("<I", 1)))
                time.sleep(0.03)
                conn.sendall(pack_message(SCOMMAND_EFFECTIVE_EVENT_NOTICE, b""))

            elif cmd_id == LCOMMAND_DISCONNECT_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_DISCONNECT_REPLY, b""))
                break

            elif cmd_id == LCOMMAND_LOCALNW_INFO_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_LOCALNW_INFO_REPLY, b""))
                conn.sendall(build_localnw_info_notice())

            elif cmd_id == LCOMMAND_GLOBALADDR_REQUEST:
                conn.sendall(client_data)
                conn.sendall(build_globaladdr_reply())

            elif cmd_id == LCOMMAND_ECHO_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_ECHO_REPLY, payload))

            elif cmd_id == LCOMMAND_ADAPTER_INFO_REQUEST:
                conn.sendall(client_data)
                conn.sendall(build_adapter_info_reply())

            elif cmd_id == LCOMMAND_SERVICE_VERSION_REQUEST:
                conn.sendall(client_data)
                ver = "2.85(x64) 2014/07/08".encode("utf-8")
                conn.sendall(pack_message(SCOMMAND_SERVICE_VERSION_REPLY, ver.ljust(32, b"\x00")))

            elif cmd_id == LCOMMAND_GAME_START_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_GAME_STATUS_REPLY, b""))

            elif cmd_id == LCOMMAND_GAME_END_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_GAME_STATUS_REPLY, b""))

            elif cmd_id == LCOMMAND_GAME_CONTINUE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_GAME_STATUS_REPLY, b""))

            elif cmd_id == LCOMMAND_INCOME_START_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10)))

            elif cmd_id == LCOMMAND_INCOME_END_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10)))

            elif cmd_id == LCOMMAND_INCOME_CONTINUE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10)))

            elif cmd_id == LCOMMAND_SET_INCOME_MODE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_SET_INCOME_MODE_REPLY, struct.pack("<I", 0)))

            elif cmd_id == LCOMMAND_GAMESTATUS_RESET_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_GAMESTATUS_RESET_REPLY, b""))

            elif cmd_id == LCOMMAND_ROW_EVENTDATA_LIST_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_ROW_EVENTDATA_LIST_REPLY, b""))
                event_data = b"\x00" * 2112
                conn.sendall(struct.pack("<I", len(event_data)))
                conn.sendall(event_data)

            elif cmd_id == LCOMMAND_CARD_SELECT_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_SELECT_REPLY, struct.pack("<I", 1) + struct.pack("<Q", CARD_ID)))

            elif cmd_id == LCOMMAND_CARD_INSERT_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_INSERT_REPLY, struct.pack("<I", 1) + struct.pack("<Q", CARD_ID)))

            elif cmd_id == LCOMMAND_CARD_UPDATE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_UPDATE_REPLY, struct.pack("<I", 1)))

            elif cmd_id == LCOMMAND_CARD_BUYS_ITEM_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_BUYS_ITEM_REPLY, struct.pack("<I", 1)))

            elif cmd_id == LCOMMAND_CARD_TAKEOVER_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_TAKEOVER_REPLY, struct.pack("<I", 1)))

            elif cmd_id == LCOMMAND_CARD_DECREASE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_DECREASE_REPLY, struct.pack("<I", 1)))

            elif cmd_id == LCOMMAND_CARD_REISSUE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_REISSUE_REPLY, b""))

            elif cmd_id == LCOMMAND_CARD_PLAYED_LIST_REQUES:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CARD_PLAYED_LIST_REPLY, b""))

            elif cmd_id == LCOMMAND_RANKING_DATA_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_RANKING_DATA_REPLY, b""))

            elif cmd_id == LCOMMAND_GAME_FREE_START_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_GAME_STATUS_REPLY, b""))

            elif cmd_id == LCOMMAND_GAME_FREE_END_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_FREE_TICKET_REPLY, b"\x00" * 8))

            elif cmd_id == LCOMMAND_INCOME_FREE_START_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10)))

            elif cmd_id == LCOMMAND_INCOME_FREE_END_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10)))

            elif cmd_id == LCOMMAND_INCOME_FREE_CONTINUE_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10)))

            elif cmd_id == LCOMMAND_CLIENT_END:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_CLIENT_END_REPLY, b""))

            elif cmd_id == LCOMMAND_HTTPACCESS_GET_REQUEST:
                log.info("HTTPACCESS_GET: %s", payload.decode("utf-8", errors="replace"))
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_HTTPACCESS_START, b""))
                conn.sendall(pack_message(SCOMMAND_HTTPACCESS_REPLY, b""))

            elif cmd_id == LCOMMAND_HTTPACCESS_POST_REQUEST:
                log.info("HTTPACCESS_POST: %s", payload.decode("utf-8", errors="replace"))
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_HTTPACCESS_START, b""))
                conn.sendall(pack_message(SCOMMAND_HTTPACCESS_REPLY, b""))

            elif cmd_id == LCOMMAND_UPLOAD_CONFIG_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_UPLOAD_CONFIG_REPLY, b""))

            elif cmd_id == LCOMMAND_EVENT_DOWNLOAD_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_ROW_EVENTDATA_LIST_REPLY, b""))

            elif cmd_id == LCOMMAND_SHOPPING_REQUEST:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_SHOPPING_REPLY, b""))

            elif cmd_id == LCOMMAND_DESTROY_MY_SERVICE:
                conn.sendall(client_data)
                conn.sendall(pack_message(SCOMMAND_DESTROY_MY_SERVICE_REPLY, b""))

            else:
                log.warning("Unknown cmd: 0x%03X", cmd_id)
                conn.sendall(client_data)

    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        conn.close()
        try:
            _trace.conn_close(conn_id)
        except Exception:
            pass
        log.info("Client disconnected: %s:%d", addr[0], addr[1])


def tcp_server_thread() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 1042))
    srv.listen(5)
    log.info("TCP server listening on 127.0.0.1:1042")
    while True:
        conn, addr = srv.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


def handle_http_on_tls(tls_sock: socket.socket, addr: tuple) -> None:
    import json
    try:
        f = tls_sock.makefile("rb")
        while True:
            req_line = f.readline()
            if not req_line:
                break

            headers_raw = b""
            while True:
                line = f.readline()
                headers_raw += line
                if line == b"\r\n" or line == b"\n" or not line:
                    break

            parts = req_line.split(b" ")
            method = parts[0].decode("utf-8", errors="replace") if parts else ""
            path = parts[1].decode("utf-8", errors="replace") if len(parts) > 1 else "/"
            log.info("HTTPS: %s %s from %s:%d", method, path, addr[0], addr[1])

            content_length = 0
            for h in headers_raw.split(b"\r\n"):
                if h.lower().startswith(b"content-length:"):
                    content_length = int(h.split(b":")[1].strip())

            body = b""
            if content_length > 0:
                body = f.read(content_length)

            resp_body = json.dumps({"status": 0, "result": 1, "message": "OK"}).encode("utf-8")
            resp = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(resp_body)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            ).encode("utf-8")
            tls_sock.sendall(resp + resp_body)
            log.info("  -> 200 OK (%d bytes)", len(resp_body))
            break
    except Exception as e:
        log.info("HTTPS handler error: %s", e)
    finally:
        try:
            tls_sock.close()
        except Exception:
            pass


def https_server_thread() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    certs_dir = os.path.join(project_root, "tools", "certs")
    bundle_pem = os.path.join(certs_dir, "nesys_bundle.pem")
    cert_pem = os.path.join(certs_dir, "nesys_cert.pem")
    key_pem = os.path.join(certs_dir, "nesys_key.pem")

    if os.path.isfile(bundle_pem):
        certfile = bundle_pem
        keyfile = bundle_pem
        log.info("[:443] loaded cert: %s", os.path.abspath(bundle_pem))
    elif os.path.isfile(cert_pem) and os.path.isfile(key_pem):
        certfile = cert_pem
        keyfile = key_pem
        log.info("[:443] loaded cert: %s", os.path.abspath(cert_pem))
    else:
        log.error("[:443] CERT FILES NOT FOUND in %s", certs_dir)
        log.error("  Expected: tools/certs/nesys_bundle.pem")
        log.error("       or: tools/certs/nesys_cert.pem + nesys_key.pem")
        log.error("  Run tools/install_cert_admin.bat first.")
        sys.exit(1)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)

    raw_srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    raw_srv.bind(("0.0.0.0", 443))
    raw_srv.listen(5)
    log.info("HTTPS stub on 0.0.0.0:443 (TLS + CONNECT proxy)")

    while True:
        try:
            client_sock, client_addr = raw_srv.accept()
            client_sock.settimeout(5.0)
            first_bytes = client_sock.recv(6, socket.MSG_PEEK)
            client_sock.settimeout(None)

            if first_bytes.startswith(b"CONNECT"):
                t = threading.Thread(target=handle_connect_proxy, args=(client_sock, client_addr, ctx), daemon=True)
                t.start()
            else:
                t = threading.Thread(target=handle_direct_tls, args=(client_sock, client_addr, ctx), daemon=True)
                t.start()
        except Exception as e:
            log.error("Accept error: %s", e)


def handle_connect_proxy(client_sock: socket.socket, addr: tuple, ctx: ssl.SSLContext) -> None:
    log.info("CONNECT proxy from %s:%d", addr[0], addr[1])
    try:
        request = b""
        while b"\r\n\r\n" not in request:
            chunk = client_sock.recv(4096)
            if not chunk:
                return
            request += chunk

        first_line = request.split(b"\r\n")[0].decode("utf-8", errors="replace")
        log.info("CONNECT: %s", first_line)

        client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        tls_sock = ctx.wrap_socket(client_sock, server_side=True)
        log.info("CONNECT TLS handshake OK for %s", addr)

        handle_http_on_tls(tls_sock, addr)

    except (ConnectionResetError, BrokenPipeError, OSError, ssl.SSLError) as e:
        log.info("CONNECT proxy error: %s", e)
    finally:
        try:
            client_sock.close()
        except Exception:
            pass
        log.info("CONNECT proxy done: %s:%d", addr[0], addr[1])


def handle_direct_tls(client_sock: socket.socket, addr: tuple, ctx: ssl.SSLContext) -> None:
    log.info("Direct TLS from %s:%d", addr[0], addr[1])
    try:
        tls_sock = ctx.wrap_socket(client_sock, server_side=True)
        log.info("Direct TLS handshake OK for %s", addr)
        handle_http_on_tls(tls_sock, addr)
    except (ssl.SSLError, OSError) as e:
        log.info("Direct TLS error: %s", e)
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


def main():
    log.info("=== NESYS TCP + HTTPS Stub Starting ===")
    log.info("TCP: 127.0.0.1:1042 (NesysService emulator)")
    log.info("HTTPS: 0.0.0.0:443 (cert validation stub)")

    t1 = threading.Thread(target=tcp_server_thread, daemon=True)
    t1.start()

    t2 = threading.Thread(target=https_server_thread, daemon=True)
    t2.start()

    log.info("All servers started. Waiting for connections...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Shutting down.")


if __name__ == "__main__":
    main()
