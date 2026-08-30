"""Status tracking for the Starwing local launcher.

Maintains real-time status of all launcher components.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class LauncherState(Enum):
    IDLE = "idle"
    CHECKING = "checking_environment"
    STARTING = "starting_server_stack"
    RUNNING = "running"
    LAUNCHING_GAME = "launching_game"
    GAME_RUNNING = "game_running"
    STOPPING = "stopping"
    ERROR = "error"


class GamePhase(Enum):
    LAUNCHING = "Launching"
    BOOTING = "Booting"
    TITLE = "Title"
    LOCAL_TUTORIAL = "Local Tutorial"
    BATTLE = "Battle"
    RETURNED_TO_TITLE = "Returned to Title"
    CLOSED = "Closed"
    UNKNOWN = "Unknown"


@dataclass
class PortStatus:
    port: int
    label: str
    listening: bool = False
    owner_pid: int | None = None


@dataclass
class PingPongStatus:
    ping_count: int = 0
    last_pong_time: float | None = None
    connected: bool = False

    @property
    def latency_ms(self) -> float | None:
        if self.last_pong_time is None:
            return None
        return (time.time() - self.last_pong_time) * 1000


@dataclass
class ControllerStatus:
    connected: bool = False
    xinput_slot: int | None = None
    selected_mapping: str = ""
    enabled: bool = False
    starwing_foreground: bool = False
    output_keys: list[str] = field(default_factory=list)
    emergency_stop: bool = False


@dataclass
class ProfileStatus:
    selected_name: str = ""
    selected_id: int | None = None
    session_active: bool = False
    tutorial_attempts: int = 0


@dataclass
class NESYSStatus:
    authentication: str = "Unavailable"
    b_nesys_server_live: str = "Unavailable"
    production_matching: str = "Disabled"


@dataclass
class LauncherStatus:
    state: LauncherState = LauncherState.IDLE
    game_phase: GamePhase = GamePhase.UNKNOWN
    ports: list[PortStatus] = field(default_factory=lambda: [
        PortStatus(80, "HTTP Proxy"),
        PortStatus(4001, "Python HTTP"),
        PortStatus(6666, "TCP Matching"),
    ])
    ping_pong: PingPongStatus = field(default_factory=PingPongStatus)
    controller: ControllerStatus = field(default_factory=ControllerStatus)
    profile: ProfileStatus = field(default_factory=ProfileStatus)
    nesys: NESYSStatus = field(default_factory=NESYSStatus)
    proxy_request_count: int = 0
    last_matching_request: str | None = None
    game_pid: int | None = None
    game_log_path: str | None = None
    last_local_battle_result: str = ""
    error_message: str = ""
    startup_log: list[str] = field(default_factory=list)

    def add_log(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self.startup_log.append(f"[{ts}] {msg}")
