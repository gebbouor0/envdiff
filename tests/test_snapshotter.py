"""Tests for envdiff.snapshotter."""

import json
import os
import pytest

from envdiff.comparator import DiffResult
from envdiff.snapshotter import (
    Snapshot,
    take_snapshot,
    save_snapshot,
    load_snapshot,
)


@pytest.fixture
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"ONLY_LEFT": "val1"},
        missing_in_left={"ONLY_RIGHT": "val2"},
        mismatched={"SHARED": ("aaa", "bbb")},
    )


def test_take_snapshot_label(diff_result):
    snap = take_snapshot(diff_result, label="prod")
    assert snap.label == "prod"


def test_take_snapshot_timestamp_is_iso(diff_result):
    snap = take_snapshot(diff_result, label="test")
    # basic check: contains a T separator and a timezone marker
    assert "T" in snap.timestamp


def test_take_snapshot_copies_missing_in_right(diff_result):
    snap = take_snapshot(diff_result, label="x")
    assert snap.missing_in_right == {"ONLY_LEFT": "val1"}


def test_take_snapshot_copies_missing_in_left(diff_result):
    snap = take_snapshot(diff_result, label="x")
    assert snap.missing_in_left == {"ONLY_RIGHT": "val2"}


def test_take_snapshot_copies_mismatched(diff_result):
    snap = take_snapshot(diff_result, label="x")
    assert snap.mismatched == {"SHARED": ("aaa", "bbb")}


def test_take_snapshot_metadata_stored(diff_result):
    snap = take_snapshot(diff_result, label="x", metadata={"env": "staging"})
    assert snap.metadata["env"] == "staging"


def test_take_snapshot_empty_metadata_by_default(diff_result):
    snap = take_snapshot(diff_result, label="x")
    assert snap.metadata == {}


def test_as_dict_mismatched_values_are_lists(diff_result):
    snap = take_snapshot(diff_result, label="x")
    d = snap.as_dict()
    assert d["mismatched"]["SHARED"] == ["aaa", "bbb"]


def test_from_dict_round_trip(diff_result):
    snap = take_snapshot(diff_result, label="round-trip")
    restored = Snapshot.from_dict(snap.as_dict())
    assert restored.label == snap.label
    assert restored.missing_in_right == snap.missing_in_right
    assert restored.mismatched["SHARED"] == ("aaa", "bbb")


def test_save_and_load_snapshot(diff_result, tmp_path):
    snap = take_snapshot(diff_result, label="save-load")
    path = str(tmp_path / "snaps" / "result.json")
    save_snapshot(snap, path)
    assert os.path.exists(path)
    loaded = load_snapshot(path)
    assert loaded.label == "save-load"
    assert loaded.missing_in_left == {"ONLY_RIGHT": "val2"}
    assert loaded.mismatched["SHARED"] == ("aaa", "bbb")


def test_save_snapshot_creates_directories(diff_result, tmp_path):
    path = str(tmp_path / "deep" / "nested" / "snap.json")
    snap = take_snapshot(diff_result, label="nested")
    save_snapshot(snap, path)
    assert os.path.isfile(path)


def test_saved_file_is_valid_json(diff_result, tmp_path):
    path = str(tmp_path / "snap.json")
    snap = take_snapshot(diff_result, label="json-check")
    save_snapshot(snap, path)
    with open(path) as fh:
        data = json.load(fh)
    assert data["label"] == "json-check"
