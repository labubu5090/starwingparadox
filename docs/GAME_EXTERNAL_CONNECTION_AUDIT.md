# Game External Connection Audit

## G2 Run

| Property | Value |
|----------|-------|
| Destination IP | 44.213.205.183 |
| Destination Port | 443 (HTTPS) |
| Local Address | 10.0.4.99:38391 |
| Protocol | HTTPS/TLS |
| Initiating Process | AcrGame-Win64-Shipping.exe (PID 10480) |
| First Observed | t=45s after launch |
| Purpose | NESYS server (cert3.nesys.jp) |

## G3 Run

| Property | Value |
|----------|-------|
| Destination IP | 100.25.160.95 |
| Destination Port | 443 (HTTPS) |
| Local Address | 10.0.4.99:61900 |
| Protocol | HTTPS/TLS |
| Initiating Process | AcrGame-Win64-Shipping.exe (PID 38472) |
| First Observed | t=60s after launch |
| Purpose | NESYS server (cert3.nesys.jp) |

## Analysis

Both IPs are likely CDN endpoints for `cert3.nesys.jp`:
- 44.213.205.183 — AWS/GCP IP range
- 100.25.160.95 — Tailscale/CGNAT range (possibly local network path)

The game contacts the external NESYS server via:
1. NesysService (WINHTTP client) → cert3.nesys.jp
2. Without NesysService, the game's built-in HTTP client attempts direct connection

## Safety

- No TLS interception performed
- No credentials captured
- No requests replayed
- No destination redirected
- Metadata observed only
