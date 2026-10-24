"""High-level checks for local chains, Merkle inclusion, and signatures."""

from __future__ import annotations

from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from src.crypto.hash_chain import HashChain
from src.crypto.merkle_tree import verify_proof
from src.crypto.signature import verify_signature


def verify_integrity(
    chain: HashChain,
    *,
    leaf: Any | None = None,
    proof: list[dict[str, str]] | None = None,
    merkle_root: str | None = None,
    public_key: Ed25519PublicKey | None = None,
    message: bytes | str | None = None,
    signature: str | None = None,
) -> dict[str, bool]:
    checks = {"chain_valid": chain.verify()}
    if any(value is not None for value in (leaf, proof, merkle_root)):
        checks["merkle_valid"] = (
            leaf is not None
            and proof is not None
            and merkle_root is not None
            and verify_proof(leaf, proof, merkle_root)
        )
    if any(value is not None for value in (public_key, message, signature)):
        checks["signature_valid"] = (
            public_key is not None
            and message is not None
            and signature is not None
            and verify_signature(public_key, message, signature)
        )
    checks["valid"] = all(checks.values())
    return checks


def verify_chain(entries: list[dict[str, Any]]) -> bool:
    return HashChain(entries).verify()