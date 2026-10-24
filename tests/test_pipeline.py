import pytest

from src.attacks.inject_attack import inject_event
from src.attacks.modify_attack import modify_event
from src.attacks.reorder_attack import reorder_events
from src.attacks.replay_attack import replay_event
from src.parsing.drain_parser import parse_line
from src.parsing.sequence_builder import build_sequences


def test_parser_extracts_fields_and_normalizes_variables() -> None:
    parsed = parse_line(
        "2025-01-02T10:20:30Z ERROR api[12]: Request from 10.1.2.3 failed with 503",
        source="app.log",
    )

    assert parsed["timestamp"] == "2025-01-02T10:20:30Z"
    assert parsed["level"] == "ERROR"
    assert parsed["component"] == "api"
    assert parsed["template"] == "Request from <IP> failed with <NUM>"


def test_sequence_builder_groups_and_labels_windows() -> None:
    events = [
        {"source": "a", "label": 0},
        {"source": "a", "label": 1},
        {"source": "b", "label": 0},
    ]

    windows = build_sequences(events, window_size=1)

    assert len(windows) == 3
    assert [window["label"] for window in windows] == [0, 1, 0]


def test_attack_helpers_copy_and_mark_changed_events() -> None:
    original = [{"message": "first"}, {"message": "second"}]

    injected = inject_event(original, {"message": "fake"})
    modified = modify_event(original, 0, "message", "changed")
    reordered = reorder_events(original, 0, 1)
    replayed = replay_event(original, 0)

    assert len(injected) == 3 and injected[-1]["label"] == 1
    assert modified[0]["label"] == 1
    assert [event["message"] for event in reordered] == ["second", "first"]
    assert reordered[0]["label"] == reordered[1]["label"] == 1
    assert len(replayed) == 3 and replayed[-1]["label"] == 1
    assert original == [{"message": "first"}, {"message": "second"}]


def test_invalid_sequence_window_size_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_sequences([], window_size=0)
