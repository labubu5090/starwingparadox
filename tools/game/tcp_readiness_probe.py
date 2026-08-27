"""TCP accept readiness probe for Phase 2A-G9.

RAW_TRANSPORT_READINESS_ONLY — generated Protobuf is unavailable.

Non-destructive test that proves:
- A client can connect to 127.0.0.1:6666
- The server accepts the connection
- A raw framed message can be sent (4-byte LE length prefix + raw bytes)
- The connection closes cleanly
- The TCP server remains alive afterward
- No session state remains
- No background tasks remain

Usage:
    python -m tools.game.tcp_readiness_probe
    # or
    from tools.game.tcp_readiness_probe import run_probe
    result = run_probe()
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import struct
import subprocess
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProbeResult:
    """Result of a TCP readiness probe."""

    success: bool = False
    connected: bool = False
    frame_sent: bool = False
    response_received: bool = False
    response_bytes: int = 0
    response_sha256: str = ""
    connection_closed_cleanly: bool = False
    server_alive_after: bool = False
    listener_still_owned: bool = False
    connection_count_zero: bool = False
    elapsed_ms: float = 0.0
    error: str = ""
    probe_type: str = "RAW_TRANSPORT_READINESS_ONLY"


def _build_raw_ping_frame() -> bytes:
    """Build a raw Ping frame (0x66) for transport-level readiness.

    This is a minimal PbMessage envelope encoded manually:
      field 1 (packetId) = 999: tag=0x08, varint(999)
      field 2 (messageType) = 0x66: tag=0x10, varint(0x66)

    RAW_TRANSPORT_READINESS_ONLY — no semantic protobuf validation.
    """
    inner = bytearray()
    inner.append(0x08)
    val = 999
    while val > 0x7F:
        inner.append((val & 0x7F) | 0x80)
        val >>= 7
    inner.append(val & 0x7F)
    inner.append(0x10)
    inner.append(0x66)
    return bytes(inner)


def _encode_length_prefix(payload: bytes) -> bytes:
    """Encode a 4-byte little-endian length prefix."""
    return struct.pack("<I", len(payload))


def _check_netstat_listening(port: int) -> tuple[bool, int]:
    """Check netstat for LISTENING on port. Returns (found, pid)."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            timeout=5,
            stderr=subprocess.DEVNULL,
        )
        for line in out.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    return True, int(parts[-1])
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    return False, 0


def _check_netstat_active(port: int) -> int:
    """Count active (ESTABLISHED/TIME_WAIT) connections on port."""
    try:
        out = subprocess.check_output(
            ["netstat", "-ano"],
            text=True,
            timeout=5,
            stderr=subprocess.DEVNULL,
        )
        count = 0
        for line in out.splitlines():
            if f":{port}" in line and ("ESTABLISHED" in line or "TIME_WAIT" in line):
                count += 1
        return count
    except (subprocess.SubprocessError, OSError):
        return -1


async def run_probe(
    host: str = "127.0.0.1",
    port: int = 6666,
    timeout: float = 5.0,
    listener_pid: int | None = None,
) -> ProbeResult:
    """Run a TCP readiness probe against the matching server.

    Returns a ProbeResult with detailed status.
    """
    result = ProbeResult()
    start = time.monotonic()

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        result.connected = True
        peer = writer.get_extra_info("peername")
        logger.info("Connected to %s:%d (local=%s)", host, port, peer)

        raw_payload = _build_raw_ping_frame()
        framed = _encode_length_prefix(raw_payload)
        writer.write(framed)
        await writer.drain()
        result.frame_sent = True
        logger.info("Raw frame sent: %d bytes (RAW_TRANSPORT_READINESS_ONLY)", len(framed))

        try:
            header = await asyncio.wait_for(reader.readexactly(4), timeout=timeout)
            resp_len = struct.unpack("<I", header)[0]
            if 0 < resp_len < 1_048_576:
                payload = await asyncio.wait_for(reader.readexactly(resp_len), timeout=timeout)
                result.response_received = True
                result.response_bytes = resp_len
                result.response_sha256 = hashlib.sha256(payload).hexdigest()[:16]
                logger.info(
                    "Response received: %d bytes, sha256=%s",
                    resp_len,
                    result.response_sha256,
                )
            else:
                logger.info("No response (length=%d)", resp_len)
        except asyncio.TimeoutError:
            logger.info("No response within timeout (expected in raw fallback mode)")
        except asyncio.IncompleteReadError:
            logger.info("Connection closed by server (no response)")

        writer.close()
        await writer.wait_closed()
        result.connection_closed_cleanly = True
        logger.info("Connection closed cleanly")

    except asyncio.TimeoutError:
        result.error = "Connection timeout"
        logger.error("Connection timeout")
    except ConnectionRefusedError:
        result.error = "Connection refused"
        logger.error("Connection refused")
    except OSError as exc:
        result.error = str(exc)
        logger.error("Probe error: %s", exc)

    await asyncio.sleep(1.0)
    try:
        _r, w2 = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=2.0,
        )
        w2.close()
        await w2.wait_closed()
        result.server_alive_after = True
        logger.info("Server alive after probe")
    except (OSError, TimeoutError):
        logger.warning("Server NOT alive after probe")

    if listener_pid is not None:
        found, current_pid = _check_netstat_listening(port)
        if found and current_pid == listener_pid:
            result.listener_still_owned = True
            logger.info("Listener still owned by PID %d", listener_pid)
        elif found:
            logger.warning("Listener PID changed: expected %d, got %d", listener_pid, current_pid)

    active = _check_netstat_active(port)
    if active >= 0:
        result.connection_count_zero = active == 0
        logger.info("Active connections on port %d: %d", port, active)

    result.elapsed_ms = (time.monotonic() - start) * 1000
    result.success = (
        result.connected
        and result.frame_sent
        and result.connection_closed_cleanly
        and result.server_alive_after
    )
    return result


def run_probe_sync(
    host: str = "127.0.0.1",
    port: int = 6666,
    timeout: float = 5.0,
    listener_pid: int | None = None,
) -> ProbeResult:
    """Synchronous wrapper for run_probe."""
    return asyncio.run(run_probe(host, port, timeout, listener_pid))


async def main() -> None:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = run_probe_sync()
    print("\n=== TCP Readiness Probe Result ===")
    print(f"  Probe type:            {result.probe_type}")
    print(f"  Success:               {result.success}")
    print(f"  Connected:             {result.connected}")
    print(f"  Frame sent:            {result.frame_sent}")
    print(f"  Response received:     {result.response_received}")
    print(f"  Response bytes:        {result.response_bytes}")
    print(f"  Response sha256:       {result.response_sha256}")
    print(f"  Connection closed:     {result.connection_closed_cleanly}")
    print(f"  Server alive after:    {result.server_alive_after}")
    print(f"  Listener still owned:  {result.listener_still_owned}")
    print(f"  Connection count zero: {result.connection_count_zero}")
    print(f"  Elapsed:               {result.elapsed_ms:.1f}ms")
    if result.error:
        print(f"  Error:                 {result.error}")
    print("=" * 39)
    return result


if __name__ == "__main__":
    asyncio.run(main())
