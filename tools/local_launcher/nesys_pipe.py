"""NESYS Named Pipe Stub Server.

Creates a named pipe at \\\\.\\pipe\\nesys_games that responds to the
LCOMMAND/SCOMMAND protocol. This flips bNesysServerLive=1 in the game's
observer object, allowing the online gate to pass.

Protocol reference: docs/NESYSERVICE_PIPE_PROTOCOL.md
"""
from __future__ import annotations

import struct
import threading
import time

import win32file
import win32pipe

PIPE_NAME = r"\\.\pipe\nesys_games"

# LCOMMAND IDs (Game -> Service)
LCOMMAND_NONE = 0x00
LCOMMAND_ERROR = 0x01
LCOMMAND_CLIENT_START = 0x02
LCOMMAND_CONNECT_REQUEST = 0x03
LCOMMAND_DISCONNECT_REQUEST = 0x04
LCOMMAND_GAME_START_REQUEST = 0x05
LCOMMAND_GAME_END_REQUEST = 0x06
LCOMMAND_GAME_CONTINUE_REQUEST = 0x07
LCOMMAND_CARD_SELECT_REQUEST = 0x0A
LCOMMAND_CARD_INSERT_REQUEST = 0x0B
LCOMMAND_PING = 0x66
LCOMMAND_SERVICE_VERSION_REQUEST = 0x19
LCOMMAND_ADAPTER_INFO_REQUEST = 0x18
LCOMMAND_LOCALNW_INFO_REQUEST = 0x15
LCOMMAND_CLIENT_END = 0x2E

# SCOMMAND IDs (Service -> Game)
SCOMMAND_NONE = 0x00
SCOMMAND_NW_ERROR = 0x01
SCOMMAND_CERT_ERROR = 0x02
SCOMMAND_LINKUP_NOTICE = 0x05
SCOMMAND_CERT_INIT_NOTICE = 0x07
SCOMMAND_CERT_REGULAR_NOTICE = 0x08
SCOMMAND_CLIENT_START_REPLY = 0x0D
SCOMMAND_CONNECT_REPLY = 0x0E
SCOMMAND_GAME_STATUS_REPLY = 0x10
SCOMMAND_CARD_SELECT_REPLY = 0x11
SCOMMAND_CARD_INSERT_REPLY = 0x12
SCOMMAND_ADAPTER_INFO_REPLY = 0x1F
SCOMMAND_SERVICE_VERSION_REPLY = 0x20
SCOMMAND_LOCALNW_INFO_REPLY = 0x1B
SCOMMAND_PING_RESPONSE = 0x67
SCOMMAND_CLIENT_END = 0x2B

HEADER_SIZE = 8  # 4 bytes cmd_id + 4 bytes data_size


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


class NesysPipeServer:
    def __init__(self) -> None:
        self._pipe_handle: int | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._client_connected = False
        self._command_count = 0

    @property
    def running(self) -> bool:
        return self._running

    @property
    def client_connected(self) -> bool:
        return self._client_connected

    @property
    def command_count(self) -> int:
        return self._command_count

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
                response = self._dispatch(cmd_id, payload)
                if response is not None:
                    win32file.WriteFile(self._pipe_handle, response, None)
            except OSError:
                break

    def _dispatch(self, cmd_id: int, payload: bytes) -> bytes | None:
        if cmd_id == LCOMMAND_CLIENT_START:
            return pack_message(SCOMMAND_CLIENT_START_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_PING:
            return pack_message(SCOMMAND_PING_RESPONSE, payload)

        if cmd_id == LCOMMAND_CONNECT_REQUEST:
            return pack_message(SCOMMAND_CONNECT_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_SERVICE_VERSION_REQUEST:
            return pack_message(SCOMMAND_SERVICE_VERSION_REPLY, build_service_version_reply())

        if cmd_id == LCOMMAND_ADAPTER_INFO_REQUEST:
            return pack_message(SCOMMAND_ADAPTER_INFO_REPLY, build_adapter_info_reply())

        if cmd_id == LCOMMAND_LOCALNW_INFO_REQUEST:
            return pack_message(SCOMMAND_LOCALNW_INFO_REPLY, build_localnw_info_reply())

        if cmd_id == LCOMMAND_GAME_START_REQUEST:
            return pack_message(SCOMMAND_GAME_STATUS_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_GAME_END_REQUEST:
            return pack_message(SCOMMAND_GAME_STATUS_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_GAME_CONTINUE_REQUEST:
            return pack_message(SCOMMAND_GAME_STATUS_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_CARD_SELECT_REQUEST:
            return pack_message(SCOMMAND_CARD_SELECT_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_CARD_INSERT_REQUEST:
            return pack_message(SCOMMAND_CARD_INSERT_REPLY, b"\x00" * 4)

        if cmd_id == LCOMMAND_DISCONNECT_REQUEST:
            return None

        if cmd_id == LCOMMAND_CLIENT_END:
            return pack_message(SCOMMAND_CLIENT_END, b"")

        return pack_message(SCOMMAND_NONE, b"")
