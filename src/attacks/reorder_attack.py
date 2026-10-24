"""In-memory simulation of reordering adjacent log records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def reorder_events(
    events: list[dict[str, Any]], first_index: int, second_index: int | None = None
) -> list[dict[str, Any]]:
    if second_index is None:
        second_index = first_index + 1
    if not (0 <= first_index < len(events) and 0 <= second_index < len(events)):
        raise IndexError("Event index is outside the log.")
    if first_index == second_index:
        raise ValueError("Choose two different event indexes.")
    result = deepcopy(events)
    result[first_index], result[second_index] = result[second_index], result[first_index]
    result[first_index]["label"] = 1
    result[second_index]["label"] = 1
    return result