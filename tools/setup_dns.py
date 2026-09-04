"""
Setup script: Start local DNS server, set system DNS, flush cache.
This makes cert3.nesys.jp resolve to 127.0.0.1 for ALL DNS clients,
including the game's HTTP client which bypasses the hosts file.
"""
import subprocess
import sys
import time
import socket

DNS_SERVER = "127.0.0.1"
UPSTREAM_DNS = "10.0.4.1"


def check_port53_free():
    """Check if port 53 is already in use."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(("127.0.0.1", 53))
        s.close()
        return True
    except OSError:
        return False


def flush_dns():
    """Flush the DNS resolver cache."""
    print("[*] Flushing DNS cache...")
    r = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
    print(f"    {r.stdout.strip()}")


def get_ethernet_interface():
    """Get the name of the main ethernet interface."""
    r = subprocess.run(
        ["netsh", "interface", "show", "interface"],
        capture_output=True, text=True
    )
    for line in r.stdout.splitlines():
        if "Connected" in line and "Dedicated" in line:
            parts = line.split()
            # Interface name is everything between the status columns
            name = " ".join(parts[2:])
            return name
    # Fallback
    return "Ethernet 7"


def set_dns_server(interface_name: str, dns_ip: str):
    """Set the DNS server for a network interface."""
    print(f"[*] Setting DNS server to {dns_ip} on interface: {interface_name}")
    r = subprocess.run(
        ["netsh", "interface", "ip", "set", "dns",
         f"name={interface_name}", "static", dns_ip, "primary"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print(f"    DNS set to {dns_ip}")
    else:
        print(f"    Error: {r.stderr.strip()}")
        # Try with quotes
        r2 = subprocess.run(
            ["netsh", "interface", "ip", "set", "dns",
             f'name="{interface_name}"', "static", dns_ip, "primary"],
            capture_output=True, text=True
        )
        if r2.returncode == 0:
            print(f"    DNS set to {dns_ip} (retry)")
        else:
            print(f"    Retry also failed: {r2.stderr.strip()}")


def restore_dns(interface_name: str):
    """Restore DHCP DNS (original upstream)."""
    print(f"[*] Restoring DHCP DNS on: {interface_name}")
    r = subprocess.run(
        ["netsh", "interface", "ip", "set", "dns",
         f"name={interface_name}", "dhcp"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print("    DNS restored to DHCP")
    else:
        print(f"    Error: {r.stderr.strip()}")


def test_dns_intercept():
    """Quick test to verify our DNS server intercepts correctly."""
    import dns.resolver
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["127.0.0.1"]
        resolver.lifetime = 3
        answers = resolver.resolve("cert3.nesys.jp", "A")
        ip = str(answers[0])
        if ip == "127.0.0.1":
            print(f"    [OK] cert3.nesys.jp -> {ip}")
            return True
        else:
            print(f"    [FAIL] cert3.nesys.jp -> {ip} (expected 127.0.0.1)")
            return False
    except Exception as e:
        print(f"    [FAIL] DNS test failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        iface = get_ethernet_interface()
        restore_dns(iface)
        flush_dns()
        print("[*] DNS restored. Restart DNS Client service for changes to take effect.")
        sys.exit(0)

    if not check_port53_free():
        print("[!] Port 53 already in use. Kill the existing DNS server first.")
        sys.exit(1)

    print("=" * 60)
    print("NESYS Local DNS + System DNS Setup")
    print("=" * 60)

    # Step 1: Flush existing DNS cache
    flush_dns()

    # Step 2: Get interface name
    iface = get_ethernet_interface()
    print(f"[*] Detected interface: {iface}")

    # Step 3: Set system DNS to 127.0.0.1
    set_dns_server(iface, DNS_SERVER)

    # Step 4: Flush again
    flush_dns()

    print()
    print("[*] DNS configuration complete!")
    print(f"    System DNS -> {DNS_SERVER}")
    print(f"    Upstream fallback -> {UPSTREAM_DNS}")
    print()
    print("[*] To restore original DNS later, run:")
    print("    python tools/local_dns.py restore")
