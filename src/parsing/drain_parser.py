"""Small Drain-style parser that extracts common fields and templates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterator

TIMESTAMP_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ][0-9:.+-]+Z?)\s+(?P<rest>.*)$"
)
LEVEL_RE = re.compile(
    r"^\[?(?P<level>TRACE|DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|CRITICAL)\]?\s*(?P<rest>.*)$",
    re.IGNORECASE,
)
COMPONENT_RE = re.compile(r"^(?P<component>[\w.$/-]+)(?:\[\d+\])?:\s*(?P<message>.*)$")
VARIABLE_PATTERNS = (
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}\b"), "<UUID>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),
    (re.compile(r"\b0x[0-9a-fA-F]+\b"), "<HEX>"),
    (re.compile(r"\b\d+\b"), "<NUM>"),
)


def normalize_template(message: str) -> str:
    template = message
    for pattern, replacement in VARIABLE_PATTERNS:
        template = pattern.sub(replacement, template)
    return template


def parse_line(line: str, source: str = "unknown") -> dict[str, str]:
    raw = line.rstrip("\r\n")
    rest = raw
    timestamp = ""
    level = "UNKNOWN"
    component = "unknown"

    match = TIMESTAMP_RE.match(rest)
    if match:
        timestamp, rest = match.group("timestamp"), match.group("rest")
    match = LEVEL_RE.match(rest)
    if match:
        level, rest = match.group("level").upper(), match.group("rest")
    match = COMPONENT_RE.match(rest)
    if match:
        component, rest = match.group("component"), match.group("message")
    message = rest.strip()
    return {
        "timestamp": timestamp,
        "level": level,
        "component": component,
        "message": message,
        "template": normalize_template(message),
        "source": source,
        "raw": raw,
    }


def parse_file(path: str | Path) -> Iterator[dict[str, str]]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.strip():
                yield parse_line(line, source=file_path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for event in parse_file(args.input):
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()