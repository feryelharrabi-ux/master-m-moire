"""Append-only SHA-256 hash chain for structured log events."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

GENESIS_HASH = "0" * 64


def canonical_json(value: Any) -> str:
    """Serialize JSON deterministically so hashes are stable across runs."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class ChainEntry:
    index: int
    timestamp: str
    event: Any
    previous_hash: str
    hash: str


class HashChain:
    """A verifiable in-memory chain; persist ``to_list()`` to store it."""

    def __init__(self, entries: Iterable[dict[str, Any]] | None = None) -> None:
        self.entries: list[ChainEntry] = []
        if entries:
            for raw in entries:
                self.entries.append(ChainEntry(**raw))

    @staticmethod
    def calculate_hash(
        index: int, timestamp: str, event: Any, previous_hash: str
    ) -> str:
        payload = {
            "event": event,
            "index": index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
        }
        return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

    def append(self, event: Any, timestamp: str | None = None) -> ChainEntry:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        previous_hash = self.entries[-1].hash if self.entries else GENESIS_HASH
        index = len(self.entries)
        entry = ChainEntry(
            index=index,
            timestamp=timestamp,
            event=event,
            previous_hash=previous_hash,
            hash=self.calculate_hash(index, timestamp, event, previous_hash),
        )
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous_hash = GENESIS_HASH
        for index, entry in enumerate(self.entries):
            if entry.index != index or entry.previous_hash != previous_hash:
                return False
            expected = self.calculate_hash(
                entry.index, entry.timestamp, entry.event, entry.previous_hash
            )
            if entry.hash != expected:
                return False
            previous_hash = entry.hash
        return True

    def to_list(self) -> list[dict[str, Any]]:
        return [asdict(entry) for entry in self.entries]