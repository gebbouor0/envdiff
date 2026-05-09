"""Tests for envdiff.cli_watch."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envdiff.cli_watch import add_watch_args, handle_watch
from envdiff.comparator import DiffResult


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("left")
    p.add_argument("right")
    add_watch_args(p)
    return p


def test_add_watch_args_creates_flags(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args(["a.env", "b.env"])
    assert hasattr(args, "watch")
    assert hasattr(args, "watch_interval")


def test_watch_flag_default_false(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args(["a.env", "b.env"])
    assert args.watch is False


def test_watch_interval_default(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args(["a.env", "b.env"])
    assert args.watch_interval == 1.0


def test_handle_watch_returns_false_when_not_requested(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args(["a.env", "b.env"])
    assert handle_watch(args) is False


def test_handle_watch_returns_true_and_calls_watch(parser: argparse.ArgumentParser, tmp_path: Path) -> None:
    left = tmp_path / "l.env"
    right = tmp_path / "r.env"
    left.write_text("KEY=1\n")
    right.write_text("KEY=1\n")

    args = parser.parse_args([str(left), str(right), "--watch", "--watch-interval", "0"])

    with patch("envdiff.cli_watch.watch") as mock_watch:
        mock_watch.side_effect = KeyboardInterrupt  # simulate Ctrl-C immediately
        result = handle_watch(args)

    assert result is True
    mock_watch.assert_called_once()
    _, kwargs = mock_watch.call_args
    assert kwargs["interval"] == 0.0


def test_on_change_callback_prints_report(capsys: pytest.CaptureFixture) -> None:
    """The internal callback should print a formatted report."""
    diff = DiffResult(
        missing_in_right=["GONE"],
        missing_in_left=[],
        mismatched_values={},
    )

    # Reconstruct callback by calling handle_watch with a mock watch.
    p = argparse.ArgumentParser()
    p.add_argument("left")
    p.add_argument("right")
    add_watch_args(p)
    args = p.parse_args(["a.env", "b.env", "--watch"])

    captured_cb: list = []

    def fake_watch(left, right, on_change, interval):
        captured_cb.append(on_change)
        raise KeyboardInterrupt

    with patch("envdiff.cli_watch.watch", side_effect=fake_watch):
        handle_watch(args)

    assert captured_cb
    captured_cb[0](diff)
    out = capsys.readouterr().out
    assert "GONE" in out
