"""Tests for envdiff.cli_pin."""

import argparse
import json
import pytest
from pathlib import Path

from envdiff.cli_pin import add_pin_args, handle_pin


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_pin_args(p)
    return p


@pytest.fixture
def tmp_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    return str(f)


def test_add_pin_args_creates_flags(parser):
    args = parser.parse_args([])
    assert args.pin is None
    assert args.check_drift is None
    assert args.pin_label == "baseline"


def test_pin_flag_saves_file(parser, tmp_env, tmp_path):
    out = str(tmp_path / "pin.json")
    args = parser.parse_args(["--pin", out, "--pin-label", "ci"])
    result = handle_pin(args, tmp_env)
    assert result is True
    data = json.loads(Path(out).read_text())
    assert data["label"] == "ci"
    assert "DB_HOST" in data["pinned"]


def test_handle_pin_returns_false_when_not_requested(parser, tmp_env):
    args = parser.parse_args([])
    assert handle_pin(args, tmp_env) is False


def test_check_drift_no_drift(parser, tmp_env, tmp_path, capsys):
    pin_file = str(tmp_path / "pin.json")
    # First pin
    args = parser.parse_args(["--pin", pin_file])
    handle_pin(args, tmp_env)
    # Then check drift with same env
    args2 = parser.parse_args(["--check-drift", pin_file])
    result = handle_pin(args2, tmp_env)
    assert result is True
    captured = capsys.readouterr()
    assert "No drift" in captured.out


def test_check_drift_detects_change(parser, tmp_path, capsys):
    env1 = tmp_path / "env1"
    env1.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    env2 = tmp_path / "env2"
    env2.write_text("DB_HOST=remotehost\nDB_PORT=5432\n")
    pin_file = str(tmp_path / "pin.json")

    args = parser.parse_args(["--pin", pin_file])
    handle_pin(args, str(env1))

    args2 = parser.parse_args(["--check-drift", pin_file])
    result = handle_pin(args2, str(env2))
    assert result is True
    captured = capsys.readouterr()
    assert "Drift detected" in captured.out
    assert "DB_HOST" in captured.out
