"""NESYS Named Pipe Stub Server.

Creates a named pipe at \\\\.\\pipe\\nesys_games that responds to the
LCOMMAND/SCOMMAND protocol. This flips bNesysServerLive=1 in the game's
observer object, allowing the online gate to pass.

Protocol reference: docs/NESYSERVICE_PIPE_PROTOCOL.md

Frame format: 4-byte little-endian cmd_id + 4-byte little-endian data_size + payload.
The CARD_INSERT_REPLY and CARD_SELECT_REPLY carry the 8-byte card ID so the game
populates NESiCA_ID at the insert-card screen instead of seeing an empty card.
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

# LCOMMAND IDs (Game -> Service) -- g42/public StarwingParadox protocol (matches
# tools/nesys_tcp_stub.py which is the authoritative reference). The wire trace
# (game CMD 0x01 CLIENT_START, then 0x02 CONNECT, then 0x14 LOCALNW) confirms this.
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
LCOMMAND_GAME_FREE_CONTINUE_REQUEST = 0x2C
LCOMMAND_INCOME_FREE_CONTINUE_REQUEST = 0x2C
LCOMMAND_CLIENT_END = 0x2B
LCOMMAND_PING = 0x66

# SCOMMAND IDs (Service -> Game) -- reply = client command + 0x100
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
SCOMMAND_DISCONNECT_REPLY = 0x10F
SCOMMAND_PING_RESPONSE = 0x166
SCOMMAND_CLIENT_END = 0x12B

HEADER_SIZE = 8  # 4 bytes cmd_id + 4 bytes data_size

# Default NESiCA card id used when no profile has been selected yet.
DEFAULT_CARD_ID = 7020392000000000


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


def build_service_version_reply() -> bytes:
    version_str = "2.0.0-stub"
    return version_str.encode("utf-8") + b"\x00"


def build_adapter_info_reply() -> bytes:
    info = {
        "adapter_name": "StarwingStub",
        "mac": "00:00:00:00:00:00",
        "ip": "127.0.0.1",
        "subnet": "255.255.255.0",
        "gateway": "127.0.0.1",
        "dns": "127.0.0.1",
    }
    return "|".join(f"{k}={v}" for k, v in info.items()).encode("utf-8") + b"\x00"


def build_localnw_info_reply() -> bytes:
    fields = [
        0,  # param_error
        0,  # interface_error
        1,  # access (wired)
        1,  # first
        0,  # errcnt
        0,  # errcode
        b"",  # errstr
        1000,  # speed (Mbps)
        0,  # total_down
        0,  # game_down
        1,  # process_num
        2048,  # OS_Phys (MB)
        1024,  # OS_Virtual (MB)
        512,  # AP_Phys (MB)
        256,  # AP_Virtual (MB)
        0,  # SV_Phys
        0,  # SV_Virtual
        50000,  # free_space (MB)
        86400,  # uptime (seconds)
        100,  # libver
        b"00000000",  # game_hash
    ]
    parts = []
    for f in fields:
        if isinstance(f, bytes):
            parts.append(f)
        else:
            parts.append(struct.pack("<I", f))
    return b"|".join(parts) + b"\x00"


def build_cert_init_notice(card_id: int) -> bytes:
    """SCOMMAND_CERT_INIT_NOTICE (0x107) carrying shop/cert identity.

    Layout matches tools/nesys_tcp_stub.py (the authoritative reference): a
    u32 tenpo_id, fixed-width ASCII fields (tenpo_name 31, address 33, ticket 33,
    prefecture 23), a repeated tenpo_id, a 1024-byte img_path, and a host string.
    This notice is what makes the game's RequestNesysControlInitiazlize [Cert]
    exchange succeed and set NESYS_state->byte_1600 == 1 -> bNesysServerLive[1].
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
    net_mac = b"001C42888475\x00\x00\x00\x00"
    ip_addr = b"192.168.1.100\x00\x00\x00"
    ip_gate = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_dns = b"192.168.1.1\x00\x00\x00\x00\x00"
    ip_unkn = b"\x7c\x15\x00\x00\x00\x00\x00\x00"
    iface_data = net_mac + ip_addr + ip_gate + ip_dns + ip_unkn
    payload = struct.pack("<I", 1) + struct.pack("<I", len(iface_data)) + iface_data
    return pack_message(SCOMMAND_LOCALNW_INFO_NOTICE, payload)


def build_globaladdr_reply() -> bytes:
    global_addr = b"10.79.0.41"
    payload = struct.pack("<I", 0x0018)
    payload += struct.pack("<I", 0x0001)
    payload += struct.pack("<I", 0x01A6)
    payload += global_addr.ljust(16, b"\x00")
    return pack_message(SCOMMAND_GLOBALADDR_REPLY, payload)


class NesysPipeServer:
    def __init__(self) -> None:
        self._pipe_handle: int | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._client_connected = False
        self._command_count = 0
        self._log_callback = None
        # The card id served at the insert-card screen. Updated by the launcher
        # when an active profile is selected (see app.py: self._nesys_pipe.card_id).
        self.card_id = DEFAULT_CARD_ID

    @property
    def running(self) -> bool:
        return self._running

    @property
    def client_connected(self) -> bool:
        return self._client_connected

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
        self._thread = threading.Thread(target=self._run, daemon=True, name="nesys-pipe")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._pipe_handle is not None:
            try:
                win32file.CloseHandle(self._pipe_handle)
            except OSError:
                pass
            self._pipe_handle = None

    def _run(self) -> None:
        while self._running:
            try:
                self._serve_client()
            except OSError:
                time.sleep(0.1)

    def _serve_client(self) -> None:
        self._pipe_handle = win32pipe.CreateNamedPipe(
            PIPE_NAME,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            65536,
            65536,
            0,
            None,
        )
        try:
            win32pipe.ConnectNamedPipe(self._pipe_handle, None)
            self._client_connected = True
            self._log("Client connected to pipe")
            self._handle_client()
        except OSError:
            pass
        finally:
            self._client_connected = False
            try:
                win32pipe.DisconnectNamedPipe(self._pipe_handle)
            except OSError:
                pass
            try:
                win32file.CloseHandle(self._pipe_handle)
            except OSError:
                pass
            self._pipe_handle = None

    def _handle_client(self) -> None:
        while self._running and self._client_connected:
            try:
                hr, data = win32file.ReadFile(self._pipe_handle, 65536)
                if hr != 0 or not data:
                    break
                cmd_id, data_size = unpack_header(data)
                payload = data[HEADER_SIZE:HEADER_SIZE + data_size] if len(data) > HEADER_SIZE else b""
                self._command_count += 1
                self._log(f"RX[{len(data)}] cmd=0x{cmd_id:02X} size={data_size} full={data.hex()}")
                responses = self._dispatch(cmd_id, payload)
                for response in responses:
                    if response is not None:
                        win32file.WriteFile(self._pipe_handle, response, None)
                        self._log(f"TX[{len(response)}] full={response.hex()}")
            except (OSError, pywintypes.error):
                # Client disconnected abruptly (ERROR_BROKEN_PIPE=109) or an I/O
                # error occurred. Do not kill the serve loop; tear this client
                # down cleanly so the server keeps accepting new connections.
                self._log(f"client I/O ended: {sys.exc_info()[1]}")
                break

    def _card_insert_payload(self) -> bytes:
        # status(uint32, 1=success) + card_id(uint64 LE)
        status = struct.pack("<I", 1)
        card = struct.pack("<Q", self.card_id)
        return status + card

    def _dispatch(self, cmd_id: int, payload: bytes) -> list[bytes | None]:
        # Per the reference tools/nesys_tcp_stub.py: the pipes are message-mode,
        # so a command may produce MULTIPLE frames (reply + notices). Each frame is
        # a separate pipe message. CONNECT must emit the cert-init notice sequence,
        # which is what completes the certificate auth and sets bNesysServerLive.
        if cmd_id == LCOMMAND_CLIENT_START:
            return [pack_message(SCOMMAND_CLIENT_START_REPLY, b"\x00" * 4)]

        # Inject CARD_INSERT_REPLY so the game populates NESiCA_ID even when
        # bUseNesys[0] (local RFID path).  The RFIDReadSerialAndID success
        # from the GALAXYIO proxy reads the card, but the card screen still
        # needs the Nesys card-insert flow to set NESiCA_ID.

        if cmd_id == LCOMMAND_PING:
            return [
                pack_message(SCOMMAND_PING_RESPONSE, payload),
                pack_message(SCOMMAND_CARD_INSERT_REPLY, self._card_insert_payload()),
            ]

        if cmd_id == LCOMMAND_CONNECT_REQUEST:
            frames = [
                pack_message(SCOMMAND_CONNECT_REPLY, b"\x00" * 4),
                pack_message(SCOMMAND_NWRECOVER_NOTICE, b""),
                build_cert_init_notice(self.card_id),
                pack_message(SCOMMAND_LINKUP_NOTICE, b""),
                pack_message(SCOMMAND_CERT_REGULAR_NOTICE, struct.pack("<I", 1)),
                pack_message(SCOMMAND_EFFECTIVE_EVENT_NOTICE, b""),
            ]
            return frames

        if cmd_id == LCOMMAND_ECHO_REQUEST:
            return [pack_message(SCOMMAND_ECHO_REPLY, payload)]

        if cmd_id == LCOMMAND_SERVICE_VERSION_REQUEST:
            ver = b"2.85(x64) 2014/07/08".ljust(32, b"\x00")
            return [pack_message(SCOMMAND_SERVICE_VERSION_REPLY, ver)]

        if cmd_id == LCOMMAND_ADAPTER_INFO_REQUEST:
            return [pack_message(SCOMMAND_ADAPTER_INFO_REPLY, build_adapter_info_reply())]

        if cmd_id == LCOMMAND_LOCALNW_INFO_REQUEST:
            return [
                pack_message(SCOMMAND_LOCALNW_INFO_REPLY, b""),
                build_localnw_info_notice(),
            ]

        if cmd_id == LCOMMAND_GLOBALADDR_REQUEST:
            return [build_globaladdr_reply()]

        if cmd_id in (LCOMMAND_GAME_START_REQUEST,
                      LCOMMAND_GAME_END_REQUEST,
                      LCOMMAND_GAME_CONTINUE_REQUEST,
                      LCOMMAND_GAME_FREE_START_REQUEST,
                      LCOMMAND_GAME_FREE_END_REQUEST):
            return [pack_message(SCOMMAND_GAME_STATUS_REPLY, b"")]

        if cmd_id in (LCOMMAND_INCOME_START_REQUEST,
                      LCOMMAND_INCOME_END_REQUEST,
                      LCOMMAND_INCOME_CONTINUE_REQUEST,
                      LCOMMAND_INCOME_FREE_START_REQUEST,
                      LCOMMAND_INCOME_FREE_END_REQUEST,
                      LCOMMAND_INCOME_FREE_CONTINUE_REQUEST):
            return [pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<II", 0, 10))]

        if cmd_id == LCOMMAND_SET_INCOME_MODE_REQUEST:
            return [pack_message(SCOMMAND_INCOME_STATUS_REPLY, struct.pack("<I", 0))]

        if cmd_id == LCOMMAND_GAMESTATUS_RESET_REQUEST:
            return [pack_message(SCOMMAND_ROW_EVENTDATA_LIST_REPLY, b"")]

        if cmd_id == LCOMMAND_ROW_EVENTDATA_LIST_REQUEST:
            return [pack_message(SCOMMAND_ROW_EVENTDATA_LIST_REPLY, b""), struct.pack("<I", 2112) + b"\x00" * 2112]

        if cmd_id == LCOMMAND_GAME_FREE_END_REQUEST:
            return [pack_message(SCOMMAND_FREE_TICKET_REPLY, b"\x00" * 8)]

        if cmd_id == LCOMMAND_CARD_SELECT_REQUEST:
            return [pack_message(SCOMMAND_CARD_SELECT_REPLY, self._card_insert_payload())]

        if cmd_id == LCOMMAND_CARD_INSERT_REQUEST:
            return [pack_message(SCOMMAND_CARD_INSERT_REPLY, self._card_insert_payload())]

        if cmd_id == LCOMMAND_CARD_UPDATE_REQUEST:
            return [pack_message(SCOMMAND_CARD_UPDATE_REPLY, struct.pack("<I", 1))]

        if cmd_id == LCOMMAND_CARD_BUYS_ITEM_REQUEST:
            return [pack_message(SCOMMAND_CARD_BUYS_ITEM_REPLY, struct.pack("<I", 1))]

        if cmd_id == LCOMMAND_CARD_TAKEOVER_REQUEST:
            return [pack_message(SCOMMAND_CARD_TAKEOVER_REPLY, struct.pack("<I", 1))]

        if cmd_id == LCOMMAND_CARD_DECREASE_REQUEST:
            return [pack_message(SCOMMAND_CARD_DECREASE_REPLY, struct.pack("<I", 1))]

        if cmd_id == LCOMMAND_CARD_REISSUE_REQUEST:
            return [pack_message(SCOMMAND_CARD_REISSUE_REPLY, b"")]

        if cmd_id == LCOMMAND_CARD_PLAYED_LIST_REQUES:
            return [pack_message(SCOMMAND_CARD_PLAYED_LIST_REPLY, b"")]

        if cmd_id == LCOMMAND_RANKING_DATA_REQUEST:
            return [pack_message(SCOMMAND_RANKING_DATA_REPLY, b"")]

        if cmd_id == LCOMMAND_HTTPACCESS_GET_REQUEST:
            return [
                pack_message(SCOMMAND_HTTPACCESS_START, b""),
                pack_message(SCOMMAND_HTTPACCESS_REPLY, b""),
            ]

        if cmd_id == LCOMMAND_HTTPACCESS_POST_REQUEST:
            return [
                pack_message(SCOMMAND_HTTPACCESS_START, b""),
                pack_message(SCOMMAND_HTTPACCESS_REPLY, b""),
            ]

        if cmd_id == LCOMMAND_UPLOAD_CONFIG_REQUEST:
            return [pack_message(SCOMMAND_UPLOAD_CONFIG_REPLY, b"")]

        if cmd_id == LCOMMAND_EVENT_DOWNLOAD_REQUEST:
            return [pack_message(SCOMMAND_ROW_EVENTDATA_LIST_REPLY, b"")]

        if cmd_id == LCOMMAND_SHOPPING_REQUEST:
            return [pack_message(SCOMMAND_SHOPPING_REPLY, b"")]

        if cmd_id == LCOMMAND_DESTROY_MY_SERVICE:
            return [pack_message(SCOMMAND_DESTROY_MY_SERVICE_REPLY, b"")]

        if cmd_id == LCOMMAND_DISCONNECT_REQUEST:
            return [pack_message(SCOMMAND_DISCONNECT_REPLY, b"")]

        if cmd_id == LCOMMAND_CLIENT_END:
            return [pack_message(SCOMMAND_CLIENT_END_REPLY, b"")]

        return [pack_message(SCOMMAND_NONE, b"")]