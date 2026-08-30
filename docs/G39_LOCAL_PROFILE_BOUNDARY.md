# G39 Local Profile Boundary

## What This Is
- Operator-owned local profiles for the private server
- Entirely server-side persistence via SQLite
- No relationship to NESYS authentication, NESiCA identity, or production systems

## What This Is NOT
- This is NOT a NESiCA card emulation
- This is NOT an online identity
- This is NOT a production entitlement
- This is NOT a payment system
- This is NOT a certificate authentication system

## Security Boundaries

### In Scope
- Local profile creation, selection, deletion
- Tutorial attempt tracking (local only)
- Session management (local only)
- Server status monitoring (loopback only)

### Out of Scope (NEVER implemented)
- NESYS authentication
- NESiCA identity
- Certificate verification
- Production matching
- Production entitlement
- Payment systems
- External network interfaces
- Game binary modification
- Game save file modification
- IsOnline or bNesysServerLive mutation
- Pipe emulation (port 1042)

## API Design Principles
- All endpoints return `{"error": bool, "status": int}` pattern
- Profile data is private-server-only
- No cross-server synchronization
- No external authentication
- Tutorial tracking is local only, not authoritative for game state

## GUI Design Principles
- Card-style profile display
- Server status dashboard shows "NESYS authenticated: No"
- Server status dashboard shows "Production services: Disabled"
- All network checks are loopback-only (127.0.0.1)
- No NESYS/NESiCA branding in UI
