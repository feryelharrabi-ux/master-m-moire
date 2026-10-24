"""SHA-256 Merkle tree and inclusion proofs."""

from __future__ import annotations

import hashlib
from typing import Any

from src.crypto.hash_chain import canonical_json


def hash_leaf(value: Any) -> str:
    """Hash a value as a leaf, with domain separation from internal nodes."""
    data = value if isinstance(value, bytes) else canonical_json(value).encode("utf-8")
    return hashlib.sha256(b"\x00" + data).hexdigest()


def hash_pair(left: str, right: str) -> str:
    return hashlib.sha256(b"\x01" + bytes.fromhex(left) + bytes.fromhex(right)).hexdigest()


class MerkleTree:
    def __init__(self, leaves: list[Any]) -> None:
        if not leaves:
            raise ValueError("A Merkle tree requires at least one leaf.")
        self.leaf_hashes = [hash_leaf(leaf) for leaf in leaves]
        self.levels: list[list[str]] = [self.leaf_hashes]
        while len(self.levels[-1]) > 1:
            current = self.levels[-1]
            next_level = [
                hash_pair(current[i], current[i + 1] if i + 1 < len(current) else current[i])
                for i in range(0, len(current), 2)
            ]
            self.levels.append(next_level)

    @property
    def root(self) -> str:
        return self.levels[-1][0]

    def proof(self, index: int) -> list[dict[str, str]]:
        if not 0 <= index < len(self.leaf_hashes):
            raise IndexError("Leaf index is outside the tree.")
        proof: list[dict[str, str]] = []
        position = index
        for level in self.levels[:-1]:
            sibling_index = position ^ 1
            sibling = level[sibling_index] if sibling_index < len(level) else level[position]
            proof.append(
                {"hash": sibling, "side": "left" if sibling_index < position else "right"}
            )
            position //= 2
        return proof


def verify_proof(leaf: Any, proof: list[dict[str, str]], root: str) -> bool:
    try:
        current = hash_leaf(leaf)
        for item in proof:
            if item["side"] == "left":
                current = hash_pair(item["hash"], current)
            elif item["side"] == "right":
                current = hash_pair(current, item["hash"])
            else:
                return False
        return current == root
    except (KeyError, TypeError, ValueError):
        return False


def build_merkle_proof(leaves: list[Any], index: int) -> tuple[str, list[dict[str, str]]]:
    tree = MerkleTree(leaves)
    return tree.root, tree.proof(index)


def verify_merkle_proof(leaf: Any, proof: list[dict[str, str]], root: str) -> bool:
    return verify_proof(leaf, proof, root)