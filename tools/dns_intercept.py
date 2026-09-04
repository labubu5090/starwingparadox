"""DNS interceptor for NESYS cert validation.

Resolves cert3.nesys.jp (and friends) to 127.0.0.1 so the game's
libcurl/c-ares HTTP client hits our local :443 stub instead of
the real servers.  Everything else passes through to UPSTREAM.
"""
import socket
import struct
import sys
import threading
import signal

UPSTREAM = ("1.1.1.1", 53)
BIND_ADDR = "127.0.0.1"
BIND_PORT = 53
UPSTREAM_TIMEOUT = 2.0

INTERCEPT_MAP = {
    "cert3.nesys.jp": "127.0.0.1",
    "cert2.nesys.jp": "127.0.0.1",
    "proxy.nesys.jp": "127.0.0.1",
    "data.nesys.jp": "127.0.0.1",
    "nesys.taito.co.jp": "127.0.0.1",
}

_running = True


def parse_qname(data: bytes, offset: int) -> tuple[str, int]:
    """Parse a DNS QNAME starting at *offset*.  Returns (name, end_offset)."""
    parts: list[str] = []
    while offset < len(data):
        length = data[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            offset += 2
            break
        offset += 1
        parts.append(data[offset:offset + length].decode("ascii", errors="replace"))
        offset += length
    return ".".join(parts), offset


def build_a_response(query_id: int, qname_raw: bytes, qtype: int, ip: str) -> bytes:
    """Build a minimal DNS A-record response."""
    header = struct.pack(
        "!HHHHHH",
        query_id,
        0x8180,   # QR=1, RD=1, RA=1, RCODE=0
        1,        # QDCOUNT
        1,        # ANCOUNT
        0,        # NSCOUNT
        0,        # ARCOUNT
    )
    question = qname_raw + struct.pack("!HH", qtype, 1)
    answer = (
        b"\xc0\x0c"                     # pointer to QNAME
        + struct.pack("!HHIH", 1, 1, 5, 4)  # TYPE=A, CLASS=IN, TTL=5, RDLENGTH=4
        + socket.inet_aton(ip)
    )
    return header + question + answer


def build_servfail(query_id: int, qname_raw: bytes, qtype: int) -> bytes:
    """Build a SERVFAIL response so the client fails fast."""
    header = struct.pack(
        "!HHHHHH",
        query_id,
        0x8182,   # QR=1, RD=1, RA=1, RCODE=2 (SERVFAIL)
        1, 0, 0, 0,
    )
    question = qname_raw + struct.pack("!HH", qtype, 1)
    return header + question


def handle_query(sock: socket.socket, data: bytes, addr: tuple[str, int]) -> None:
    if len(data) < 12:
        return

    query_id = struct.unpack("!H", data[0:2])[0]
    qdcount = struct.unpack("!H", data[4:6])[0]
    if qdcount < 1:
        return

    qname_str, offset = parse_qname(data, 12)
    if offset + 4 > len(data):
        return
    qtype = struct.unpack("!H", data[offset:offset + 2])[0]

    qname_lower = qname_str.lower().rstrip(".")
    intercept_ip = INTERCEPT_MAP.get(qname_lower)

    if qtype == 1 and intercept_ip:
        print(f"[INTERCEPT] {qname_lower} -> {intercept_ip}", flush=True)
        qname_raw = data[12:offset]
        reply = build_a_response(query_id, qname_raw, qtype, intercept_ip)
        try:
            sock.sendto(reply, addr)
        except OSError:
            pass
    else:
        qtype_name = {1: "A", 28: "AAAA", 5: "CNAME", 15: "MX", 16: "TXT"}.get(qtype, str(qtype))
        print(f"[PASSTHRU] {qname_lower} ({qtype_name})", flush=True)
        forward_query(sock, data, addr, query_id, qname_raw=data[12:offset], qtype=qtype)


def forward_query(sock: socket.socket, original: bytes, client_addr: tuple[str, int],
                  query_id: int, qname_raw: bytes, qtype: int) -> None:
    fwd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        fwd_sock.settimeout(UPSTREAM_TIMEOUT)
        fwd_sock.sendto(original, UPSTREAM)
        reply, _ = fwd_sock.recvfrom(4096)
        try:
            sock.sendto(reply, client_addr)
        except OSError:
            pass
    except socket.timeout:
        print(f"[TIMEOUT] upstream {UPSTREAM[0]} for query {query_id}", flush=True)
        try:
            sock.sendto(build_servfail(query_id, qname_raw, qtype), client_addr)
        except OSError:
            pass
    except OSError as e:
        print(f"[ERROR] upstream: {e}", flush=True)
        try:
            sock.sendto(build_servfail(query_id, qname_raw, qtype), client_addr)
        except OSError:
            pass
    finally:
        fwd_sock.close()


def main() -> None:
    print("=" * 50)
    print("  NESYS DNS Interceptor")
    print(f"  Listening: {BIND_ADDR}:{BIND_PORT}")
    print(f"  Upstream:  {UPSTREAM[0]}:{UPSTREAM[1]}")
    print(f"  Intercepting: {', '.join(INTERCEPT_MAP.keys())}")
    print("=" * 50, flush=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((BIND_ADDR, BIND_PORT))
    except OSError as e:
        err = e.args[0] if e.args else 0
        if err in (10013, 10048):
            print(f"\n[ERROR] Cannot bind UDP {BIND_ADDR}:{BIND_PORT}")
            print(f"  WinError {err}: SharedAccess (ICS) or another service still holds port 53.")
            print("  Run setup_dns_admin.bat as Administrator first to stop SharedAccess.")
        else:
            print(f"\n[ERROR] Cannot bind: {e}")
        sys.exit(1)

    print(f"[OK] Bound to {BIND_ADDR}:{BIND_PORT}", flush=True)

    def _shutdown(sig, frame):
        global _running
        _running = False
        print("\nShutting down...")
        try:
            sock.close()
        except OSError:
            pass
        print("DNS interceptor stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    sock.settimeout(1.0)
    while _running:
        try:
            data, addr = sock.recvfrom(4096)
            t = threading.Thread(target=handle_query, args=(sock, data, addr), daemon=True)
            t.start()
        except socket.timeout:
            continue
        except OSError:
            if _running:
                print("[ERROR] recv error", flush=True)
            break

    print("DNS interceptor stopped.")


if __name__ == "__main__":
    main()
