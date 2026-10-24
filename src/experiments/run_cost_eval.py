"""Estimate storage size and illustrative EVM gas for a batch root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.crypto.hash_chain import canonical_json
from src.crypto.merkle_tree import MerkleTree


def estimate(events: list[dict[str, Any]]) -> dict[str, int | str]:
    if not events:
        raise ValueError("At least one event is required.")
    payload_bytes = sum(len(canonical_json(event).encode("utf-8")) for event in events)
    return {
        "events": len(events),
        "payload_bytes": payload_bytes,
        "root_bytes": 32,
        "merkle_root": MerkleTree(events).root,
        "estimated_anchor_gas": 55_000,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    events = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    print(json.dumps(estimate(events), indent=2))
    print("Gas figure is an illustrative constant, not an RPC measurement.")


if __name__ == "__main__":
    main()