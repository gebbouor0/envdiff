"""Tests for envdiff.history — saving, loading, and listing snapshots."""

import json
import os
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from envdiff.comparator import DiffResult
from envdiff.history import (
    _history_dir,
    list_snapshots,
    load_all_snapshots,
    load_snapshot,
    save_to_history,
)
from envdiff.snapshotter import Snapshot, take_snapshot


@pytest.fixture()
def diff_result():
    return DiffResult(
        missing_in_right={"ALPHA": "1"},
        missing_in_left={"BETA": "2"},
        mismatched={"GAMMA": ("old", "new")},
    )


@pytest.fixture()
def snapshot(diff_result):
    return take_snapshot(diff_result, label="test-snap")


@pytest.fixture()
def tmp_history(tmp_path, monkeypatch):
    """Redirect history storage to a temp directory."""
    history = tmp_path / ".envdiff_history"
    history.mkdir()
    monkeypatch.setattr("envdiff.history.HISTORY_DIR", str(history))
    return history


# ---------------------------------------------------------------------------
# _history_dir
# ---------------------------------------------------------------------------

def test_history_dir_returns_string():
    d = _history_dir()
    assert isinstance(d, str)


def test_history_dir_default_contains_envdiff():
    d = _history_dir()
    assert "envdiff" in d.lower()


# ---------------------------------------------------------------------------
# save_to_history
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_history, snapshot):
    path = save_to_history(snapshot, base_dir=str(tmp_history))
    assert Path(path).exists()


def test_save_file_is_valid_json(tmp_history, snapshot):
    path = save_to_history(snapshot, base_dir=str(tmp_history))
    with open(path) as f:
        data = json.load(f)
    assert "label" in data
    assert data["label"] == "test-snap"


def test_save_filename_contains_label(tmp_history, snapshot):
    path = save_to_history(snapshot, base_dir=str(tmp_history))
    assert "test-snap" in Path(path).name


def test_save_creates_dir_if_missing(tmp_path, snapshot):
    new_dir = tmp_path / "new_history"
    assert not new_dir.exists()
    save_to_history(snapshot, base_dir=str(new_dir))
    assert new_dir.exists()


# ---------------------------------------------------------------------------
# load_snapshot
# ---------------------------------------------------------------------------

def test_load_snapshot_roundtrip(tmp_history, snapshot):
    path = save_to_history(snapshot, base_dir=str(tmp_history))
    loaded = load_snapshot(path)
    assert isinstance(loaded, Snapshot)
    assert loaded.label == snapshot.label


def test_load_snapshot_preserves_missing_in_right(tmp_history, snapshot):
    path = save_to_history(snapshot, base_dir=str(tmp_history))
    loaded = load_snapshot(path)
    assert loaded.missing_in_right == snapshot.missing_in_right


def test_load_snapshot_preserves_mismatched(tmp_history, snapshot):
    path = save_to_history(snapshot, base_dir=str(tmp_history))
    loaded = load_snapshot(path)
    assert loaded.mismatched == snapshot.mismatched


def test_load_snapshot_missing_file_raises(tmp_history):
    with pytest.raises(FileNotFoundError):
        load_snapshot(str(tmp_history / "ghost.json"))


# ---------------------------------------------------------------------------
# list_snapshots
# ---------------------------------------------------------------------------

def test_list_snapshots_empty_dir(tmp_history):
    result = list_snapshots(base_dir=str(tmp_history))
    assert result == []


def test_list_snapshots_returns_paths(tmp_history, snapshot):
    save_to_history(snapshot, base_dir=str(tmp_history))
    result = list_snapshots(base_dir=str(tmp_history))
    assert len(result) == 1
    assert result[0].endswith(".json")


def test_list_snapshots_sorted_by_name(tmp_history, diff_result):
    for label in ["beta", "alpha", "gamma"]:
        snap = take_snapshot(diff_result, label=label)
        save_to_history(snap, base_dir=str(tmp_history))
        time.sleep(0.01)  # ensure distinct filenames
    result = list_snapshots(base_dir=str(tmp_history))
    names = [Path(p).name for p in result]
    assert names == sorted(names)


def test_list_snapshots_missing_dir_returns_empty(tmp_path):
    result = list_snapshots(base_dir=str(tmp_path / "nonexistent"))
    assert result == []


# ---------------------------------------------------------------------------
# load_all_snapshots
# ---------------------------------------------------------------------------

def test_load_all_empty(tmp_history):
    result = load_all_snapshots(base_dir=str(tmp_history))
    assert result == []


def test_load_all_returns_snapshot_objects(tmp_history, snapshot):
    save_to_history(snapshot, base_dir=str(tmp_history))
    result = load_all_snapshots(base_dir=str(tmp_history))
    assert len(result) == 1
    assert isinstance(result[0], Snapshot)


def test_load_all_multiple_snapshots(tmp_history, diff_result):
    for label in ["one", "two", "three"]:
        snap = take_snapshot(diff_result, label=label)
        save_to_history(snap, base_dir=str(tmp_history))
    result = load_all_snapshots(base_dir=str(tmp_history))
    assert len(result) == 3
    labels = {s.label for s in result}
    assert labels == {"one", "two", "three"}
