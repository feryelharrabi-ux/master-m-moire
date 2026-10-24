"""In-memory simulation of injecting a fabricated log record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def inject_event(
    events: list[dict[str, Any]], event: dict[str, Any], index: int | None = None
) -> list[dict[str, Any]]:
    result = deepcopy(events)
    injected = deepcopy(event)
    injected["label"] = 1
    if index is None:
        result.append(injected)
    elif 0 <= index <= len(result):
        result.insert(index, injected)
    else:
        raise IndexError("Insertion index is outside the log.")
    return result