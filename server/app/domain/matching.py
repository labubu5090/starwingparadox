"""Matching state machine."""

from __future__ import annotations

from enum import Enum


class MatchingState(Enum):
    """Lifecycle states for a matching session."""

    CREATED = "created"
    QUEUED = "queued"
    CANDIDATE_FOUND = "candidate_found"
    ROOM_CREATED = "room_created"
    WAITING_READY = "waiting_ready"
    READY = "ready"
    BATTLE_ASSIGNED = "battle_assigned"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
