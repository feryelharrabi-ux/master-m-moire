"""Evaluation helpers and CLI for saved baseline prediction files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


def evaluate_predictions(
    expected: Sequence[int], predicted: Sequence[int]
) -> dict[str, object]:
    if len(expected) == 0 or len(expected) != len(predicted):
        raise ValueError("Expected and predicted labels must have equal non-zero lengths.")
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "precision": float(precision_score(expected, predicted, zero_division=0)),
        "recall": float(recall_score(expected, predicted, zero_division=0)),
        "f1": float(f1_score(expected, predicted, zero_division=0)),
        "confusion_matrix": confusion_matrix(expected, predicted, labels=[0, 1]).tolist(),
        "samples": len(expected),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, help="JSON: {expected: [], predicted: []}")
    args = parser.parse_args()
    values = json.loads(args.predictions.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_predictions(values["expected"], values["predicted"]), indent=2))


if __name__ == "__main__":
    main()