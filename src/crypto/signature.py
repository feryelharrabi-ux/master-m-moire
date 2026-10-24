"""Ed25519 signing helpers with PEM key serialization."""

from __future__ import annotations

import base64
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_key_pair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def save_private_key(private_key: Ed25519PrivateKey, path: str | Path) -> None:
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    Path(path).write_bytes(pem)


def save_public_key(public_key: Ed25519PublicKey, path: str | Path) -> None:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    Path(path).write_bytes(pem)


def load_private_key(path: str | Path) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("Expected an Ed25519 private key.")
    return key


def load_public_key(path: str | Path) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(Path(path).read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError("Expected an Ed25519 public key.")
    return key


def sign_message(private_key: Ed25519PrivateKey, message: bytes | str) -> str:
    data = message.encode("utf-8") if isinstance(message, str) else message
    return base64.b64encode(private_key.sign(data)).decode("ascii")


def verify_signature(
    public_key: Ed25519PublicKey, message: bytes | str, signature: str
) -> bool:
    data = message.encode("utf-8") if isinstance(message, str) else message
    try:
        public_key.verify(base64.b64decode(signature, validate=True), data)
    except (InvalidSignature, ValueError, TypeError):
        return False
    return True