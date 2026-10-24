"""Deterministic numeric features for individual log records."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

FEATURE_NAMES = (
    "message_length",
    "token_count",
    "digit_count",
    "uppercase_ratio",
    "punctuation_count",
    "is_error_level",
    "is_warning_level",
    "template_length",
)


def extract_features(event: Mapping[str, Any]) -> dict[str, float]:
    message = str(event.get("message", event.get("raw", "")))
    template = str(event.get("template", message))
    letters = [character for character in message if character.isalpha()]
    uppercase_ratio = (
        sum(character.isupper() for character in letters) / len(letters) if letters else 0.0
    )
    level = str(event.get("level", "")).upper()
    return {
        "message_length": float(len(message)),
        "token_count": float(len(message.split())),
        "digit_count": float(sum(character.isdigit() for character in message)),
        "uppercase_ratio": uppercase_ratio,
        "punctuation_count": float(len(re.findall(r"[^\w\s]", message))),
        "is_error_level": float(level in {"ERROR", "FATAL", "CRITICAL"}),
        "is_warning_level": float(level in {"WARN", "WARNING"}),
        "template_length": float(len(template)),
    }


def feature_matrix(events: Iterable[Mapping[str, Any]]) -> list[list[float]]:
    return [
        [extract_features(event)[name] for name in FEATURE_NAMES] for event in events
    ]


def labels_from_events(events: Iterable[Mapping[str, Any]]) -> list[int]:
    labels: list[int] = []
    for event in events:
        label = int(event.get("label", 0))
        if label not in (0, 1):
            raise ValueError("Each event label must be 0 (normal) or 1 (tampered).")
        labels.append(label)
    return labels