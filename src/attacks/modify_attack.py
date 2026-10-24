"""In-memory simulation of changing a log record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def modify_event(
    events: list[dict[str, Any]], index: int, field: str, value: Any
) -> list[dict[str, Any]]:
    if not 0 <= index < len(events):
        raise IndexError("Event index is outside the log.")
    if field in {"label", "hash", "previous_hash"}:
        raise ValueError(f"Field {field!r} cannot be used as a tamper target.")
    result = deepcopy(events)
    result[index][field] = value
    result[index]["label"] = 1
    return result