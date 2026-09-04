"""Generate a self-signed multi-SAN certificate for the NESYS :443 stub.

Covers all hosts that the DNS interceptor (tools/dns_intercept.py) redirects
to 127.0.0.1, plus a wildcard and loopback entries.
"""
import datetime
import ipaddress
import os
import sys

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
except ImportError:
    print("[ERROR] 'cryptography' package is not installed.")
    print("  Install it with:  pip install cryptography")
    sys.exit(1)

# ---------------------------------------------------------------
# Keep this list in sync with tools/dns_intercept.py INTERCEPT_MAP
# ---------------------------------------------------------------
SAN_HOSTS = [
    "cert3.nesys.jp",
    "cert2.nesys.jp",
    "proxy.nesys.jp",
    "data.nesys.jp",
    "nesys.taito.co.jp",
    "*.nesys.jp",
    "localhost",
]

SAN_IPS = [
    ipaddress.ip_address("127.0.0.1"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
KEY_PATH = os.path.join(OUTPUT_DIR, "nesys_key.pem")
CERT_PATH = os.path.join(OUTPUT_DIR, "nesys_cert.pem")
BUNDLE_PATH = os.path.join(OUTPUT_DIR, "nesys_bundle.pem")
DER_PATH = os.path.join(OUTPUT_DIR, "nesys_cert.der")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # RSA 2048-bit key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    now = datetime.datetime.utcnow()
    not_before = now - datetime.timedelta(days=1)
    not_after = now + datetime.timedelta(days=3650)

    # Subject / Issuer
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "StarwingParadox Local"),
        x509.NameAttribute(NameOID.COMMON_NAME, "cert3.nesys.jp"),
    ])

    # Subject Alternative Names
    san_names = [x509.DNSName(h) for h in SAN_HOSTS]
    san_ips = [x509.IPAddress(ip) for ip in SAN_IPS]

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(
            x509.SubjectAlternativeName(san_names + san_ips),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # --- Write private key (PEM, no passphrase) ---
    with open(KEY_PATH, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # --- Write certificate (PEM) ---
    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    # --- Write bundle (cert + key) ---
    with open(BUNDLE_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # --- Write DER form (for certutil import) ---
    with open(DER_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))

    # --- Summary ---
    print("=" * 55)
    print("  NESYS self-signed certificate generated")
    print("=" * 55)
    print()
    print("  SAN list:")
    for h in SAN_HOSTS:
        print(f"    DNS:{h}")
    for ip in SAN_IPS:
        print(f"    IP:{ip}")
    print()
    print(f"  Key:       {KEY_PATH}")
    print(f"  Cert:      {CERT_PATH}")
    print(f"  Bundle:    {BUNDLE_PATH}")
    print(f"  DER:       {DER_PATH}")
    print()
    print("  Next: run install_cert_admin.bat as Administrator")


if __name__ == "__main__":
    main()
