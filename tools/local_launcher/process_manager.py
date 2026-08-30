"""Process manager for the Starwing local launcher.

Tracks and manages only launcher-owned processes. Never kills unrelated processes.
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field


@dataclass
class OwnedProcess:
    name: str
    pid: int
    executable: str
    cmd_line: str
    start_time: float
    expected_port: int | None = None
    log_path: str | None = None
    process: subprocess.Popen | None = field(default=None, repr=False)

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None


class ProcessManager:
    def __init__(self) -> None:
        self._owned: dict[str, OwnedProcess] = {}

    @property
    def owned_processes(self) -> dict[str, OwnedProcess]:
        return dict(self._owned)

    def register(self, name: str, proc: subprocess.Popen,
                 executable: str = "", cmd_line: str = "",
                 expected_port: int | None = None,
                 log_path: str | None = None) -> OwnedProcess:
        exe_path = ""
        try:
            args = getattr(proc, "args", None)
            if args is not None:
                first = args[0]  # type: ignore[index]
                exe_path = str(first)
        except (TypeError, IndexError, AttributeError):
            pass
        op = OwnedProcess(
            name=name,
            pid=proc.pid,
            executable=executable or exe_path,
            cmd_line=cmd_line,
            start_time=time.time(),
            expected_port=expected_port,
            log_path=log_path,
            process=proc,
        )
        self._owned[name] = op
        return op

    def is_running(self, name: str) -> bool:
        op = self._owned.get(name)
        if op is None:
            return False
        return op.is_running

    def stop(self, name: str) -> bool:
        op = self._owned.get(name)
        if op is None:
            return False
        if not op.is_running:
            del self._owned[name]
            return True
        try:
            op.process.terminate()  # type: ignore[union-attr]
            try:
                op.process.wait(timeout=5)  # type: ignore[union-attr]
            except subprocess.TimeoutExpired:
                op.process.kill()  # type: ignore[union-attr]
                op.process.wait(timeout=3)  # type: ignore[union-attr]
        except (OSError, ProcessLookupError):
            pass
        del self._owned[name]
        return True

    def stop_all(self) -> list[str]:
        stopped = []
        for name in list(self._owned):
            if self.stop(name):
                stopped.append(name)
        return stopped

    def status_summary(self) -> dict[str, bool]:
        return {name: op.is_running for name, op in self._owned.items()}
