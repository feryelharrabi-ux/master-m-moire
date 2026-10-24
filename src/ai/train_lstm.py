"""Optional Keras LSTM trainer for fixed-size event windows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

from src.ai.features import FEATURE_NAMES, extract_features, labels_from_events


def train_lstm(
    events: list[dict],
    window_size: int = 20,
    epochs: int = 10,
    model_path: str | Path = "data/parsed/log_integrity_lstm.keras",
) -> dict[str, float]:
    try:
        from tensorflow import keras
    except ModuleNotFoundError as error:
        raise RuntimeError("The LSTM trainer requires TensorFlow; install it separately.") from error
    if window_size <= 0:
        raise ValueError("window_size must be greater than zero.")
    if epochs <= 0:
        raise ValueError("epochs must be greater than zero.")
    labels = labels_from_events(events)
    if len(set(labels)) < 2:
        raise ValueError("Training requires both normal and tampered (0/1) labels.")
    vectors = [
        [extract_features(event)[name] for name in FEATURE_NAMES] for event in events
    ]
    x = np.zeros((len(events), window_size, len(FEATURE_NAMES)), dtype=np.float32)
    for index, vector in enumerate(vectors):
        x[index, -min(index + 1, window_size) :, :] = np.asarray(
            vectors[max(0, index - window_size + 1) : index + 1][-window_size:],
            dtype=np.float32,
        )
    y = np.asarray(labels, dtype=np.float32)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(window_size, len(FEATURE_NAMES))),
            keras.layers.Masking(mask_value=0.0),
            keras.layers.LSTM(32),
            keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    model.fit(x_train, y_train, epochs=epochs, batch_size=32, verbose=0)
    loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
    output_path = Path(model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(output_path)
    return {"loss": float(loss), "accuracy": float(accuracy), "samples": float(len(y_test))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/parsed/log_integrity_lstm.keras"))
    parser.add_argument("--window-size", type=int, default=20)
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    events = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    print(json.dumps(train_lstm(events, args.window_size, args.epochs, args.output), indent=2))


if __name__ == "__main__":
    main()