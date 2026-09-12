"""NESYS Named Pipe Stub Server.

Faithful re-implementation of FakeNesicaService (github.com/ArcadeMachinist/
FakeNesicaService) for Starwing Paradox.

Reference files:
  - FakeNesicaService/PipeServer.cs   (byte-mode, multi-instance server loop)
  - FakeNesicaService/NESYS.cs        (captured wire-trace comments)

Wire frame: 4-byte LE cmd_id + 4-byte LE data_size + payload.  Most service
replies are a bare 8-byte frame (cmd + size=0).  Data-carrying replies embed
their real length in the size field:
  - CERT_INIT_NOTICE:    size = 1156 + len(host), payload built below
  - LOCALNW_INFO_NOTICE: size = 80          (ResultOK + iface_len + 72 iface)
  - GLOBALADDR_REPLY:    size = 0x18        (1 + 0x01A6 + 16 addr)
  - ADAPTER_INFO_REPLY:  size = 0xE8=232    (1 + 1 + 14x16)
  - ROW_EVENTDATA_LIST:  size = 0x844=2116  (0x840 + 2112 zero bytes)

Card commands (CARD_SELECT/INSERT/CARD_UPDATE/...) are deliberately NOT
answered - the reference switch() has no case for them (default writes 0
bytes).  On a real cabinet the card comes from the R.F. reader, not over the
NESYS pipe; the launcher's keepalive/card-slot injection provides NESiCA_ID.
"""
from __future__ import annotations

import struct
import sys
import threading
import time

import pywintypes
import win32file
import win32pipe

PIPE_NAME = r"\\.\pipe\nesys_games"

# Number of concurrent pipe instances, mirroring FakeNesicaService's 4 server
# threads. The game may hold a second pipe connection open (card/auth ops)
# alongside the main one; a single instance would leave that client with
# ERROR_PIPE_BUSY.
NUM_INSTANCES = 4

# LCOMMAND IDs (Game -> Service) -- g42/public StarwingParadox protocol (matches
# tools/nesys_tcp_stub.py which is the authoritative reference).
LCOMMAND_NONE = 0x00
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
LCOMMAND_GAME_FREE_CONTINUE_REQUEST = 0x2C
LCOMMAND_INCOME_FREE_CONTINUE_REQUEST = 0x2C
LCOMMAND_PING = 0x66

# SCOMMAND IDs (Service -> Game) -- reply = relevant server command id
SCOMMAND_NONE = 0x00
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
SCOMMAND_PING_RESPONSE = 0x166

HEADER_SIZE = 8  # 4 bytes cmd_id + 4 bytes data_size

# Default NESiCA card id used when no profile has been selected yet.
DEFAULT_CARD_ID = 7020392000000000

# Network parameters imitating a real cabinet (FakeNesicaService PipeServer.cs).
_SERVER_VERSION = b"2.85(x64) 2014/07/08"
_GLOBAL_ADDR = b"10.79.0.41"
_ADAPTER_GATE = b"192.168.8.1"
_ADAPTER_ADDR = b"192.168.8.117"
_ADAPTER_MASK = b"255.255.255.0"
_ADAPTER_MAC = b"001C42888475"
_NET_MAC = b"001C42888475"
_NET_IP = b"10.211.55.3"
_NET_GW = b"10.211.55.1"
_NET_DNS = b"10.211.55.1"
_NET_UNKN = b"\x7c\x15\x00\x00\x00\x00\x00\x00"


def profile_id_to_nesys_id(profile_id: int) -> int:
    """Map a local profile id to a synthetic NESiCA id so the server can
    return a specific card at the insert-card screen."""
    return 1000000000000000 + profile_id


def pack_message(cmd_id: int, payload: bytes = b"") -> bytes:
    return struct.pack("<II", cmd_id, len(payload)) + payload


def unpack_header(data: bytes) -> tuple[int, int]:
    if len(data) < HEADER_SIZE:
        return 0, 0
    cmd_id, data_size = struct.unpack("<II", data[:HEADER_SIZE])
    return cmd_id, data_size


def _pad16(value: bytes) -> bytes:
    return value[:16].ljust(16, b"\x00")


def build_service_version_reply() -> bytes:
    """SCOMMAND_SERVICE_VERSION_REPLY (0x120): cmd + len(32) + 32-byte string."""
    ver = _SERVER_VERSION.ljust(32, b"\x00")[:32]
    return pack_message(SCOMMAND_SERVICE_VERSION_REPLY, ver)


def build_cert_init_notice(card_id: int) -> bytes:
    """SCOMMAND_CERT_INIT_NOTICE (0x107).

    Wire layout (matches PipeServer.cs + NESYS.cs captured trace):
      cmd(0x107) + size(1156+hostlen) + payload:
        tenpo_id(4) tenpo_name(31) address(33) ticket(33) prefecture(23)
        tenpo_id(4) img_path(1024) host_len(4) host
    This notice completes the game's certificate initialization and sets
    NESYS_state->byte_1600 == 1 -> bNesysServerLive[1].
    """
    tenpo_id = 119
    tenpo_name = b"Arcademachine".ljust(31, b"\x00")[:31]
    address = b"Tokyo".ljust(33, b"\x00")[:33]
    ticket = b"none".ljust(33, b"\x00")[:33]
    prefecture = b"US".ljust(23, b"\x00")[:23]
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
    """SCOMMAND_LOCALNW_INFO_NOTICE (0x11C).

    Frame: cmd(0x11C) + size(80) + ResultOK(1) + iface_len(72) + iface(72).
    """
    iface = _NET_MAC.ljust(16, b"\x00")[:16]
    iface += _NET_IP.ljust(16, b"\x00")[:16]
    iface += _NET_GW.ljust(16, b"\x00")[:16]
    iface += _NET_DNS.ljust(16, b"\x00")[:16]
    iface += _NET_UNKN
    payload = struct.pack("<I", 1) + struct.pack("<I", len(iface)) + iface
    return pack_message(SCOMMAND_LOCALNW_INFO_NOTICE, payload)


def build_globaladdr_reply() -> bytes:
    """SCOMMAND_GLOBALADDR_REPLY (0x11D): cmd + len(0x18) + 1 + 0x01A6 + addr."""
    payload = struct.pack("<I I", 0x0001, 0x01A6) + _GLOBAL_ADDR.ljust(16, b"\x00")[:16]
    return pack_message(SCOMMAND_GLOBALADDR_REPLY, payload)


def build_adapter_info_reply() -> bytes:
    """SCOMMAND_ADAPTER_INFO_REPLY (0x11F).

    Frame: cmd + size(0xE8=232) + 1 + 1 + [gate16 0x00x16 addr16 0 x16
           mask16 0x.. dns1_16 0x.. dns2_16 0x.. mac16 0x.. 0x.. 0x..]
    """
    z = b"\x00" * 16
    payload = struct.pack("<I I", 1, 1)
    payload += _pad16(_ADAPTER_GATE) + z
    payload += _pad16(_ADAPTER_ADDR) + z
    payload += _pad16(_ADAPTER_MASK) + z
    payload += _pad16(_ADAPTER_GATE) + z
    payload += _pad16(_ADAPTER_GATE) + z
    payload += _pad16(_ADAPTER_MAC) + z + z + z
    return pack_message(SCOMMAND_ADAPTER_INFO_REPLY, payload)


def build_row_eventdata_list_reply() -> bytes:
    """SCOMMAND_ROW_EVENTDATA_LIST_REPLY (0x128).

    Single frame: cmd + len(0x844=2116) + len2(0x840) + 2112 zero bytes.
    """
    return pack_message(
        SCOMMAND_ROW_EVENTDATA_LIST_REPLY,
        struct.pack("<I", 0x0840) + b"\x00" * 0x0840,
    )


def _reply_8(cmd_id: int) -> bytes:
    """Bare 8-byte reply: cmd + size=0 (FakeNesicaService writes cmd + 4 nulls)."""
    return pack_message(cmd_id, b"")


class NesysPipeServer:
    """Byte-mode named-pipe responder with NUM_INSTANCES concurrent clients."""

    def __init__(self) -> None:
        self._handles: list[int] = []
        self._lock = threading.Lock()
        self._running = False
        self._threads: list[threading.Thread] = []
        self._client_count = 0
        self._command_count = 0
        self._log_callback = None
        # The card id carried in the CERT_INIT_NOTICE host string. Updated by
        # the launcher when an active profile is selected.
        self.card_id = DEFAULT_CARD_ID

    @property
    def running(self) -> bool:
        return self._running

    @property
    def client_connected(self) -> bool:
        return self._client_count > 0

    @property
    def command_count(self) -> int:
        return self._command_count

    def set_log_callback(self, cb) -> None:
        self._log_callback = cb

    def _log(self, msg: str) -> None:
        if self._log_callback is not None:
            try:
                self._log_callback(msg)
            except Exception:
                pass

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._threads = []
        for i in range(NUM_INSTANCES):
            t = threading.Thread(target=self._serve_instance, args=(i,), daemon=True,
                                 name=f"nesys-pipe-{i}")
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        self._running = False
        with self._lock:
            for h in self._handles:
                try:
                    win32file.CloseHandle(h)
                except (OSError, pywintypes.error):
                    pass
            self._handles = []
        for t in self._threads:
            t.join(timeout=1.0)
        self._threads = []

    def _register_handle(self, h: int) -> None:
        with self._lock:
            self._handles.append(h)

    def _unregister_handle(self, h: int) -> None:
        with self._lock:
            try:
                self._handles.remove(h)
            except ValueError:
                pass

    def _serve_instance(self, idx: int) -> None:
        while self._running:
            try:
                self._serve_client(idx)
            except (OSError, pywintypes.error):
                time.sleep(0.05)
            except Exception:
                time.sleep(0.05)

    def _serve_client(self, idx: int) -> None:
        handle = win32pipe.CreateNamedPipe(
            PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            4096,
            4096,
            0,
            None,
        )
        self._register_handle(handle)
        connected = False
        try:
            win32pipe.ConnectNamedPipe(handle, None)
            connected = True
            self._client_count += 1
            self._log(f"[{idx}] Client connected")
            self._read_loop(idx, handle)
        except (OSError, pywintypes.error):
            pass
        finally:
            if connected:
                self._client_count -= 1
            try:
                win32pipe.DisconnectNamedPipe(handle)
            except (OSError, pywintypes.error):
                pass
            self._unregister_handle(handle)
            try:
                win32file.CloseHandle(handle)
            except (OSError, pywintypes.error):
                pass

    def _read_loop(self, idx: int, handle: int) -> None:
        buffer = b""
        while self._running:
            try:
                hr, data = win32file.ReadFile(handle, 8192)
            except (OSError, pywintypes.error):
                break
            if hr != 0 or not data:
                break
            buffer += data
            while len(buffer) >= HEADER_SIZE:
                cmd_id, data_size = unpack_header(buffer)
                # Tolerate a non-size trailing field (request layouts differ);
                # the reference only ever reads the command id.
                if data_size > 8192:
                    data_size = 0
                total = HEADER_SIZE + data_size
                if len(buffer) < total:
                    break
                frame = buffer[:total]
                buffer = buffer[total:]
                self._command_count += 1
                self._log(f"[{idx}] RX[{len(frame)}] cmd=0x{cmd_id:02X} size={data_size}")
                responses = self._dispatch(cmd_id, frame[HEADER_SIZE:])
                for response in responses:
                    if response is not None:
                        win32file.WriteFile(handle, response, None)
                        self._log(f"[{idx}] TX[{len(response)}] cmd=0x{response[0]:02X}{response[1]:02X}")
                        # FakeNesicaService paces the 3 CONNECT frames ~30ms.
                        if cmd_id == LCOMMAND_CONNECT_REQUEST:
                            time.sleep(0.03)

    def _dispatch(self, cmd_id: int, payload: bytes) -> list[bytes]:
        # Faithful to FakeNesicaService PipeServer.cs switch():
        #  - every handler returns either 8 empty bytes or an exact frame
        #  - CONNECT emits reply + NWRECOVER + CERT_INIT (30ms gaps on real hw)
        #  - card commands and anything else get NO reply (default case)
        if cmd_id == LCOMMAND_CLIENT_START:
            return [_reply_8(SCOMMAND_CLIENT_START_REPLY)]

        if cmd_id == LCOMMAND_CONNECT_REQUEST:
            return [
                _reply_8(SCOMMAND_CONNECT_REPLY),
                _reply_8(SCOMMAND_NWRECOVER_NOTICE),
                build_cert_init_notice(self.card_id),
            ]

        if cmd_id == LCOMMAND_DISCONNECT_REQUEST:
            return [_reply_8(SCOMMAND_DISCONNECT_REPLY)]

        if cmd_id in (LCOMMAND_GAME_START_REQUEST,
                      LCOMMAND_GAME_END_REQUEST,
                      LCOMMAND_GAME_CONTINUE_REQUEST):
            return [_reply_8(SCOMMAND_GAME_STATUS_REPLY)]

        if cmd_id in (LCOMMAND_GAME_FREE_START_REQUEST,
                      LCOMMAND_GAME_FREE_CONTINUE_REQUEST):
            return [_reply_8(SCOMMAND_GAME_STATUS_REPLY)]

        if cmd_id == LCOMMAND_LOCALNW_INFO_REQUEST:
            return [
                _reply_8(SCOMMAND_LOCALNW_INFO_REPLY),
                build_localnw_info_notice(),
            ]

        if cmd_id == LCOMMAND_GLOBALADDR_REQUEST:
            return [build_globaladdr_reply()]

        if cmd_id == LCOMMAND_ADAPTER_INFO_REQUEST:
            return [build_adapter_info_reply()]

        if cmd_id == LCOMMAND_SERVICE_VERSION_REQUEST:
            return [build_service_version_reply()]

        if cmd_id == LCOMMAND_GAMESTATUS_RESET_REQUEST:
            return [_reply_8(SCOMMAND_GAMESTATUS_RESET_REPLY)]

        if cmd_id in (LCOMMAND_INCOME_START_REQUEST,
                      LCOMMAND_INCOME_END_REQUEST,
                      LCOMMAND_INCOME_CONTINUE_REQUEST):
            return [_reply_8(SCOMMAND_INCOME_STATUS_REPLY)]

        if cmd_id in (LCOMMAND_INCOME_FREE_START_REQUEST,
                      LCOMMAND_INCOME_FREE_END_REQUEST,
                      LCOMMAND_INCOME_FREE_CONTINUE_REQUEST):
            return [_reply_8(SCOMMAND_INCOME_STATUS_REPLY)]

        if cmd_id == LCOMMAND_SET_INCOME_MODE_REQUEST:
            return [_reply_8(SCOMMAND_SET_INCOME_MODE_REPLY)]

        if cmd_id == LCOMMAND_ROW_EVENTDATA_LIST_REQUEST:
            return [build_row_eventdata_list_reply()]

        if cmd_id == LCOMMAND_GAME_FREE_END_REQUEST:
            return [pack_message(SCOMMAND_FREE_TICKET_REPLY, b"\x00" * 8)]

        if cmd_id == LCOMMAND_ECHO_REQUEST:
            return [pack_message(SCOMMAND_ECHO_REPLY, payload)]

        # Unhandled (card ops, PING, HTTPACCESS, upload, ...) -> no reply.
        return []