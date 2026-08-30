"""Session logging for the Starwing local launcher.

Creates one timestamped session directory per launcher run.
Records launcher events, process events, server logs, and status changes.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

SESSION_BASE = Path(r"C:\Users\KAHO\Pictures\Starwing\tools\local_launcher\sessions")


class SessionLog:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base = base_dir or SESSION_BASE
        self._session_id = time.strftime("session_%Y%m%d_%H%M%S")
        self._dir = self._base / self._session_id
        self._events: list[dict[str, Any]] = []

    @property
    def session_dir(self) -> Path:
        return self._dir

    @property
    def session_id(self) -> str:
        return self._session_id

    def start(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self.log_event("session_start", {"session_id": self._session_id})

    def log_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        entry = {
            "timestamp": time.time(),
            "time_iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "event": event_type,
            "data": data or {},
        }
        self._events.append(entry)
        events_file = self._dir / "events.jsonl"
        with open(events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def log_process_event(self, name: str, action: str, pid: int | None = None) -> None:
        self.log_event("process", {"name": name, "action": action, "pid": pid})

    def log_server_event(self, component: str, status: str, detail: str = "") -> None:
        self.log_event("server", {"component": component, "status": status, "detail": detail})

    def log_controller_event(self, status: str, detail: str = "") -> None:
        self.log_event("controller", {"status": status, "detail": detail})

    def log_profile_event(self, action: str, profile_name: str = "", profile_id: int | None = None) -> None:
        self.log_event("profile", {"action": action, "name": profile_name, "id": profile_id})

    def log_game_event(self, phase: str, detail: str = "") -> None:
        self.log_event("game", {"phase": phase, "detail": detail})

    def log_error(self, message: str) -> None:
        self.log_event("error", {"message": message})

    def save_summary(self, summary: dict[str, Any]) -> None:
        summary_file = self._dir / "summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

    def stop(self) -> None:
        self.log_event("session_stop", {"total_events": len(self._events)})
