"""Battle state machine."""

from __future__ import annotations

from enum import Enum


class BattleState(Enum):
    """Lifecycle states for an active battle."""

    CREATED = "created"
    ASSIGNED = "assigned"
    WAITING_READY = "waiting_ready"
    READY = "ready"
    RUNNING = "running"
    RESULT_PENDING = "result_pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    FAILED = "failed"
