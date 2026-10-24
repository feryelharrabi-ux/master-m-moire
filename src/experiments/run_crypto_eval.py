"""Measure local hash-chain and Merkle-tree construction time."""

from __future__ import annotations

import json
import time

from src.crypto.hash_chain import HashChain
from src.crypto.merkle_tree import MerkleTree


def run(count: int = 10_000) -> dict[str, float | int | bool | str]:
    if count <= 0:
        raise ValueError("count must be greater than zero.")
    events = [{"index": index, "message": f"sample event {index}"} for index in range(count)]
    start = time.perf_counter()
    chain = HashChain()
    for event in events:
        chain.append(event, timestamp="2025-01-01T00:00:00Z")
    chain_seconds = time.perf_counter() - start
    start = time.perf_counter()
    tree = MerkleTree(events)
    merkle_seconds = time.perf_counter() - start
    return {
        "events": count,
        "chain_seconds": chain_seconds,
        "merkle_seconds": merkle_seconds,
        "chain_valid": chain.verify(),
        "merkle_root": tree.root,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))