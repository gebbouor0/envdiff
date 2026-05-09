"""Tests for envdiff.watcher."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envdiff.watcher import WatchState, watch
from envdiff.comparator import DiffResult


@pytest.fixture()
def tmp(tmp_path: Path):
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)
    # Ensure mtime advances even on fast filesystems.
    ts = path.stat().st_mtime + 1
    import os
    os.utime(path, (ts, ts))


def test_watch_state_refresh_detects_change(tmp: Path) -> None:
    f = tmp / "a.env"
    f.write_text("KEY=1\n")
    state = WatchState(path=f)
    changed = state.refresh()
    assert changed
    assert state.env == {"KEY": "1"}


def test_watch_state_no_change_when_mtime_same(tmp: Path) -> None:
    f = tmp / "a.env"
    f.write_text("KEY=1\n")
    state = WatchState(path=f)
    state.refresh()
    changed = state.refresh()
    assert not changed


def test_watch_state_missing_file_returns_false(tmp: Path) -> None:
    state = WatchState(path=tmp / "nonexistent.env")
    assert not state.refresh()
    assert state.env == {}


def test_watch_calls_on_change_when_file_modified(tmp: Path) -> None:
    left = tmp / "left.env"
    right = tmp / "right.env"
    left.write_text("A=1\n")
    right.write_text("A=1\n")

    calls: list[DiffResult] = []

    def _cb(result: DiffResult) -> None:
        calls.append(result)

    # Run one cycle without change — no callback.
    watch(str(left), str(right), _cb, interval=0, max_cycles=1)
    assert len(calls) == 0

    # Modify right file, then run one cycle — callback fires.
    _write(right, "A=2\n")
    watch(str(left), str(right), _cb, interval=0, max_cycles=1)
    assert len(calls) == 1
    assert "A" in calls[0].mismatched_values


def test_watch_no_callback_when_no_change(tmp: Path) -> None:
    left = tmp / "left.env"
    right = tmp / "right.env"
    left.write_text("X=hello\n")
    right.write_text("X=hello\n")

    calls: list[DiffResult] = []
    watch(str(left), str(right), lambda r: calls.append(r), interval=0, max_cycles=3)
    assert calls == []


def test_watch_detects_new_key_added(tmp: Path) -> None:
    left = tmp / "left.env"
    right = tmp / "right.env"
    left.write_text("A=1\nB=2\n")
    right.write_text("A=1\n")

    calls: list[DiffResult] = []
    watch(str(left), str(right), lambda r: calls.append(r), interval=0, max_cycles=1)
    assert calls == []

    _write(right, "A=1\nB=2\n")
    watch(str(left), str(right), lambda r: calls.append(r), interval=0, max_cycles=1)
    assert len(calls) == 1
    assert calls[0].missing_in_right == []
