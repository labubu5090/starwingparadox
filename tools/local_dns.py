"""
Local DNS server that intercepts NESYS/arcade domains → 127.0.0.1
and forwards all other queries to the real DNS server.

This bypasses Windows DNS Client DoH which ignores the hosts file.
"""
import socket
import struct
import sys
import threading

# NESYS domains that must resolve to 127.0.0.1
INTERCEPT_DOMAINS = {
    "cert3.nesys.jp",
    "cert2.nesys.jp",
    "proxy.nesys.jp",
    "data.nesys.jp",
    "nesys.taito.co.jp",
    "dev.starwing.jp",
}

UPSTREAM_DNS = "10.0.4.1"
LISTEN_PORT = 53
BUFFER_SIZE = 4096


def decode_name(data: bytes, offset: int) -> tuple[str, int]:
    """Decode a DNS name from a packet starting at offset."""
    parts = []
    jumped = False
    original_offset = offset
    max_offset = offset

    while True:
        if offset >= len(data):
            break
        length = data[offset]
        if length == 0:
            offset += 1
            if not jumped:
                max_offset = offset
            break
        if (length & 0xC0) == 0xC0:
            if not jumped:
                max_offset = offset + 2
            pointer = struct.unpack("!H", data[offset:offset + 2])[0] & 0x3FFF
            offset = pointer
            jumped = True
            continue
        offset += 1
        parts.append(data[offset:offset + length].decode("ascii", errors="replace"))
        offset += length

    return ".".join(parts), max_offset if not jumped else max_offset


def encode_name(name: str) -> bytes:
    """Encode a DNS name into wire format."""
    parts = name.split(".")
    result = b""
    for part in parts:
        result += bytes([len(part)]) + part.encode("ascii")
    result += b"\x00"
    return result


def handle_query(data: bytes, upstream_sock: socket.socket) -> bytes | None:
    """Process a DNS query. Intercept NESYS domains, forward others."""
    if len(data) < 12:
        return None

    # Parse header
    tx_id = data[0:2]
    flags = data[2:4]
    qdcount = struct.unpack("!H", data[4:6])[0]

    # Parse question
    qname, offset = decode_name(data, 12)
    if offset + 4 > len(data):
        return None
    qtype = struct.unpack("!H", data[offset:offset + 2])[0]
    qclass = struct.unpack("!H", data[offset + 2:offset + 4])[0]

    qname_lower = qname.lower()

    if qname_lower in {d.lower() for d in INTERCEPT_DOMAINS}:
        print(f"[INTERCEPT] {qname} -> 127.0.0.1 (type={qtype})")
        sys.stdout.flush()
        return build_reply(tx_id, flags, qdcount, qname, qtype, qclass, "127.0.0.1")

    # Forward to upstream DNS
    try:
        upstream_sock.sendto(data, (UPSTREAM_DNS, 53))
        upstream_sock.settimeout(3.0)
        reply, _ = upstream_sock.recvfrom(BUFFER_SIZE)
        return reply
    except socket.timeout:
        print(f"[TIMEOUT] Forwarding {qname} to {UPSTREAM_DNS} timed out")
        sys.stdout.flush()
        return None
    except Exception as e:
        print(f"[ERROR] Forwarding failed: {e}")
        sys.stdout.flush()
        return None


def build_reply(tx_id: bytes, flags: bytes, qdcount: int,
                qname: str, qtype: int, qclass: int, ip: str) -> bytes:
    """Build a DNS reply packet."""
    # Response header
    reply_flags = b"\x81\x80"  # Standard response, no error
    ancount = 1
    nscount = 0
    arcount = 0

    header = tx_id + reply_flags + struct.pack("!H", qdcount) + \
             struct.pack("!HHH", ancount, nscount, arcount)

    # Question (echo back)
    question = encode_name(qname) + struct.pack("!HH", qtype, qclass)

    # Answer
    answer_name = encode_name(qname)
    answer_type = qtype
    answer_class = 1  # IN
    ttl = 300  # 5 minutes
    rdlength = 4
    rdata = socket.inet_aton(ip)

    answer = answer_name + struct.pack("!HHIH", answer_type, answer_class, ttl, rdlength) + rdata

    return header + question + answer


def main():
    print(f"Local DNS server starting on port {LISTEN_PORT}")
    print(f"Intercepting: {', '.join(INTERCEPT_DOMAINS)}")
    print(f"Upstream DNS: {UPSTREAM_DNS}")
    sys.stdout.flush()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", LISTEN_PORT))

    # Separate upstream socket per thread
    upstream_local = ("127.0.0.1", 0)

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            upstream_sock.bind(upstream_local)

            def handle_and_send(d=data, a=addr, us=upstream_sock):
                try:
                    reply = handle_query(d, us)
                    if reply:
                        sock.sendto(reply, a)
                finally:
                    us.close()

            t = threading.Thread(target=handle_and_send, daemon=True)
            t.start()
        except KeyboardInterrupt:
            print("\nShutting down DNS server")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            sys.stdout.flush()

    sock.close()


if __name__ == "__main__":
    main()
