"""Path 1 pre-flight verifier.

Run AFTER install_cert_admin.bat + setup_dns_admin.bat.
Checks every automatable part of the Path 1 setup.
READ-ONLY — does not modify anything.
"""
import ipaddress
import os
import socket
import ssl
import struct
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CERTS_DIR = os.path.join(SCRIPT_DIR, "certs")

REQUIRED_DNS = [
    "cert3.nesys.jp",
    "cert2.nesys.jp",
    "proxy.nesys.jp",
    "data.nesys.jp",
    "nesys.taito.co.jp",
]
REQUIRED_IP = ipaddress.ip_address("127.0.0.1")

pass_count = 0
fail_count = 0
warn_count = 0
total_critical = 7


def result(status: str, detail: str) -> None:
    global pass_count, fail_count, warn_count
    tag = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]"}[status]
    print(f"  {tag} {detail}")
    if status == "PASS":
        pass_count += 1
    elif status == "FAIL":
        fail_count += 1
    else:
        warn_count += 1


def run(cmd: list[str], timeout: int = 5) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr
    except Exception:
        return -1, ""


def build_dns_query(name: str, qtype: int = 1) -> bytes:
    """Build a raw DNS A-record query."""
    tx_id = os.urandom(2)
    flags = b"\x01\x00"  # standard query, RD=1
    header = tx_id + flags + struct.pack("!HHHH", 1, 0, 0, 0)
    question = b""
    for label in name.rstrip(".").split("."):
        question += bytes([len(label)]) + label.encode("ascii")
    question += b"\x00" + struct.pack("!HH", qtype, 1)
    return header + question


def parse_dns_answer(data: bytes) -> str | None:
    """Parse the first A-record answer from a DNS response. Returns IP string or None."""
    if len(data) < 12:
        return None
    ancount = struct.unpack("!H", data[6:8])[0]
    if ancount < 1:
        return None
    # skip header + question
    offset = 12
    # skip QNAME
    while offset < len(data):
        length = data[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            offset += 2
            break
        offset += 1 + length
    offset += 4  # QTYPE + QCLASS
    # parse first answer
    if offset + 10 > len(data):
        return None
    # NAME (may be pointer)
    if (data[offset] & 0xC0) == 0xC0:
        offset += 2
    else:
        while offset < len(data) and data[offset] != 0:
            offset += 1 + data[offset]
        offset += 1
    atype = struct.unpack("!H", data[offset:offset + 2])[0]
    offset += 8  # TYPE(2) CLASS(2) TTL(4)
    rdlength = struct.unpack("!H", data[offset:offset + 2])[0]
    offset += 2
    if atype == 1 and rdlength == 4 and offset + 4 <= len(data):
        return socket.inet_ntoa(data[offset:offset + 4])
    return None


def check_cert_files() -> None:
    print("1. CERT FILES EXIST")
    files = ["nesys_bundle.pem", "nesys_cert.pem", "nesys_key.pem", "nesys_cert.der"]
    all_ok = True
    for f in files:
        p = os.path.join(CERTS_DIR, f)
        if os.path.isfile(p):
            pass
        else:
            result("FAIL", f"Missing: tools/certs/{f}")
            all_ok = False
    if all_ok:
        result("PASS", "All cert files present in tools/certs/")


def check_cert_in_store() -> None:
    print("2. CERT IN ROOT STORE")
    rc, out = run(["certutil", "-store", "Root", "cert3.nesys.jp"])
    if rc == 0 and "cert3.nesys.jp" in out.lower():
        result("PASS", "cert3.nesys.jp found in Root store")
    else:
        result("FAIL", "cert3.nesys.jp NOT in Root store — run install_cert_admin.bat")


def check_cert_san() -> None:
    print("3. CERT SAN COVERAGE")
    cert_path = os.path.join(CERTS_DIR, "nesys_cert.pem")
    if not os.path.isfile(cert_path):
        result("FAIL", "nesys_cert.pem not found — run gen_cert.py first")
        return
    try:
        info = ssl._ssl._test_decode_cert(cert_path)
    except Exception as e:
        result("FAIL", f"Cannot parse cert: {e}")
        return

    san_entries = info.get("subjectAltName", ())
    dns_names = {v for t, v in san_entries if t == "DNS"}
    ip_addrs = set()
    for t, v in san_entries:
        if t == "IP Address":
            ip_addrs.add(ipaddress.ip_address(v))

    missing = [h for h in REQUIRED_DNS if h not in dns_names]
    ip_ok = REQUIRED_IP in ip_addrs

    if not missing and ip_ok:
        result("PASS", f"SAN coverage OK: {len(dns_names)} DNS + {len(ip_addrs)} IP")
    else:
        if missing:
            result("FAIL", f"Missing DNS SANs: {', '.join(missing)}")
        if not ip_ok:
            result("FAIL", "Missing IP SAN: 127.0.0.1")


def check_port53() -> None:
    print("4. PORT 53 OWNERSHIP")
    rc, out = run(["netstat", "-ano", "-p", "UDP"])
    if rc != 0:
        result("WARN", "Could not run netstat")
        return

    pid = None
    for line in out.splitlines():
        if ":53 " in line and "UDP" in line:
            parts = line.split()
            if parts:
                pid = parts[-1]
            break

    if pid is None:
        result("WARN", "Nothing on UDP :53 — interceptor may not be running")
        return

    rc2, out2 = run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "LIST"])
    if "python" in out2.lower():
        result("PASS", f"Port 53 held by python.exe (PID {pid}) — interceptor running")
    elif "svchost" in out2.lower():
        result("FAIL", f"Port 53 held by svchost (PID {pid}) — SharedAccess still active")
    else:
        name = "unknown"
        for line in out2.splitlines():
            if "Image Name" in line:
                name = line.split(":", 1)[1].strip()
                break
        result("FAIL", f"Port 53 held by {name} (PID {pid})")


def check_dns_intercept() -> None:
    print("5. DNS INTERCEPT WORKS")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(build_dns_query("cert3.nesys.jp"), ("127.0.0.1", 53))
        data, _ = sock.recvfrom(4096)
        sock.close()
        ip = parse_dns_answer(data)
        if ip == "127.0.0.1":
            result("PASS", "cert3.nesys.jp -> 127.0.0.1 (intercept working)")
        elif ip is not None:
            result("FAIL", f"cert3.nesys.jp -> {ip} (intercept not catching it)")
        else:
            result("FAIL", "No A record in DNS response")
    except socket.timeout:
        result("FAIL", "DNS query timed out — interceptor not responding on :53")
    except OSError as e:
        result("FAIL", f"DNS query failed: {e}")


def check_dns_passthrough() -> None:
    print("6. DNS PASSTHROUGH WORKS")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        sock.sendto(build_dns_query("www.google.com"), ("127.0.0.1", 53))
        data, _ = sock.recvfrom(4096)
        sock.close()
        ip = parse_dns_answer(data)
        if ip and ip != "127.0.0.1":
            result("PASS", f"www.google.com -> {ip} (passthrough OK)")
        elif ip == "127.0.0.1":
            result("WARN", "www.google.com -> 127.0.0.1 (passthrough broken)")
        else:
            result("WARN", "No A record for www.google.com (may be CNAME chain)")
    except socket.timeout:
        result("WARN", "DNS passthrough timed out — upstream may be unreachable")
    except OSError as e:
        result("WARN", f"DNS passthrough error: {e}")


def check_443_stub() -> None:
    print("7. :443 STUB + CERT")
    cert_path = os.path.join(CERTS_DIR, "nesys_cert.pem")
    if not os.path.isfile(cert_path):
        result("FAIL", "nesys_cert.pem missing — cannot verify :443")
        return
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cert_path)
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED

        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw.settimeout(3)
        raw.connect(("127.0.0.1", 443))
        tls = ctx.wrap_socket(raw, server_hostname="cert3.nesys.jp")
        peer = tls.getpeercert()
        tls.close()

        cn = ""
        for rdn in peer.get("subject", ()):
            for attr, val in rdn:
                if attr == "commonName":
                    cn = val
        if cn == "cert3.nesys.jp":
            result("PASS", f":443 serving cert with CN={cn}")
        else:
            result("FAIL", f":443 cert CN is '{cn}', expected 'cert3.nesys.jp'")
    except ssl.SSLCertVerificationError as e:
        result("FAIL", f":443 cert verification failed: {e}")
    except (ConnectionRefusedError, OSError) as e:
        result("FAIL", f":443 not reachable: {e}")
    except socket.timeout:
        result("FAIL", ":443 connection timed out")


def check_nesys_service() -> None:
    print("8. NESYSSERVICE + PIPE (best-effort)")
    # TCP 1042
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("127.0.0.1", 1042))
        s.close()
        result("PASS", "TCP 1042 reachable (NesysService stub)")
    except (ConnectionRefusedError, OSError, socket.timeout):
        result("WARN", "TCP 1042 not reachable")

    # Named pipe
    pipe_path = r"\\.\pipe\nesys_games"
    if os.path.exists(pipe_path):
        result("PASS", f"Named pipe exists: {pipe_path}")
    else:
        result("WARN", f"Named pipe not found: {pipe_path}")


def main() -> None:
    print("=" * 55)
    print("  Path 1 Pre-Flight Verifier")
    print("=" * 55)
    print()

    check_cert_files()
    print()
    check_cert_in_store()
    print()
    check_cert_san()
    print()
    check_port53()
    print()
    check_dns_intercept()
    print()
    check_dns_passthrough()
    print()
    check_443_stub()
    print()
    check_nesys_service()

    print()
    print("=" * 55)
    print(f"  Results: {pass_count} passed, {fail_count} failed, {warn_count} warnings")
    print(f"  Critical checks: {pass_count}/{total_critical} passed")
    print("=" * 55)

    if fail_count == 0:
        print()
        print("  PATH 1 READY — launch the game and watch bNesysServerLive")
    else:
        print()
        print("  Fix the first FAIL above, then re-run this script.")

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
