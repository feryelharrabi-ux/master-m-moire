"""Train and compare logistic-regression and random-forest baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.ai.evaluate import evaluate_predictions
from src.ai.features import feature_matrix, labels_from_events


def train_baselines(
    events: list[dict], test_size: float = 0.2, random_state: int = 42
) -> dict[str, dict]:
    labels = labels_from_events(events)
    if len(set(labels)) < 2:
        raise ValueError("Training requires both normal and tampered (0/1) labels.")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")
    x_train, x_test, y_train, y_test = train_test_split(
        feature_matrix(events),
        labels,
        test_size=test_size,
        random_state=random_state,
        stratify=labels,
    )
    models = {
        "logistic_regression": make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, random_state=random_state)
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200, random_state=random_state, class_weight="balanced"
        ),
    }
    return {
        name: evaluate_predictions(y_test, model.fit(x_train, y_train).predict(x_test))
        for name, model in models.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON Lines with binary event labels")
    parser.add_argument("--output", type=Path, default=Path("data/parsed/baseline_metrics.json"))
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    events = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    results = train_baselines(events, args.test_size, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()