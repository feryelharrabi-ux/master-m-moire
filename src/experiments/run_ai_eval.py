"""Train the baseline classifiers on a labeled JSON Lines file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.ai.train_baselines import train_baselines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/parsed/ai_metrics.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    events = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    result = train_baselines(events, random_state=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()