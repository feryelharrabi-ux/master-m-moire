"""In-memory simulation of replaying an existing event."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def replay_event(
    events: list[dict[str, Any]], index: int, insertion_index: int | None = None
) -> list[dict[str, Any]]:
    if not 0 <= index < len(events):
        raise IndexError("Event index is outside the log.")
    result = deepcopy(events)
    replay = deepcopy(result[index])
    replay["label"] = 1
    if insertion_index is None:
        result.append(replay)
    elif 0 <= insertion_index <= len(result):
        result.insert(insertion_index, replay)
    else:
        raise IndexError("Insertion index is outside the log.")
    return result