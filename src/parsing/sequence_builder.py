"""Group parsed events into fixed-size windows and write JSON Lines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def build_sequences(
    events: Iterable[dict[str, Any]], window_size: int = 20, group_by: str = "source"
) -> list[dict[str, Any]]:
    if window_size <= 0:
        raise ValueError("window_size must be greater than zero.")
    groups: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        groups.setdefault(str(event.get(group_by, "unknown")), []).append(event)
    sequences: list[dict[str, Any]] = []
    for group, group_events in sorted(groups.items()):
        for start in range(0, len(group_events), window_size):
            chunk = group_events[start : start + window_size]
            sequences.append(
                {
                    "group": group,
                    "start": start,
                    "events": chunk,
                    "label": int(any(int(event.get("label", 0)) for event in chunk)),
                }
            )
    return sequences


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-size", type=int, default=20)
    parser.add_argument("--group-by", default="source")
    args = parser.parse_args()
    with args.input.open("r", encoding="utf-8") as stream:
        events = [json.loads(line) for line in stream if line.strip()]
    sequences = build_sequences(events, args.window_size, args.group_by)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for sequence in sequences:
            stream.write(json.dumps(sequence, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()