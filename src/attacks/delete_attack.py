"""In-memory simulation of deleting a log record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def delete_event(events: list[dict[str, Any]], index: int) -> list[dict[str, Any]]:
    if not 0 <= index < len(events):
        raise IndexError("Event index is outside the log.")
    result = deepcopy(events)
    del result[index]
    return result