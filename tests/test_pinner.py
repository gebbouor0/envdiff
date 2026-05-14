"""Tests for envdiff.pinner."""

import json
import pytest
from pathlib import Path

from envdiff.pinner import (
    PinResult,
    pin_env,
    check_drift,
    save_pin,
    load_pin,
)


@pytest.fixture
def baseline_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


def test_pin_env_stores_all_keys(baseline_env):
    result = pin_env(baseline_env, label="prod")
    assert result.pinned == baseline_env
    assert result.label == "prod"


def test_pin_env_no_drift_initially(baseline_env):
    result = pin_env(baseline_env, label="prod")
    assert not result.has_drift()


def test_check_drift_no_changes(baseline_env):
    pin = pin_env(baseline_env, label="prod")
    result = check_drift(pin, dict(baseline_env))
    assert not result.has_drift()
    assert result.summary() == "no drift"


def test_check_drift_value_changed(baseline_env):
    pin = pin_env(baseline_env, label="prod")
    current = dict(baseline_env)
    current["DB_HOST"] = "remotehost"
    result = check_drift(pin, current)
    assert result.has_drift()
    assert "DB_HOST" in result.drifted
    assert result.drifted["DB_HOST"] == "remotehost"


def test_check_drift_new_key(baseline_env):
    pin = pin_env(baseline_env, label="prod")
    current = dict(baseline_env)
    current["NEW_KEY"] = "value"
    result = check_drift(pin, current)
    assert "NEW_KEY" in result.new_keys
    assert result.has_drift()


def test_check_drift_removed_key(baseline_env):
    pin = pin_env(baseline_env, label="prod")
    current = {k: v for k, v in baseline_env.items() if k != "SECRET"}
    result = check_drift(pin, current)
    assert "SECRET" in result.removed_keys
    assert result.has_drift()


def test_summary_multiple_issues(baseline_env):
    pin = pin_env(baseline_env, label="prod")
    current = {"DB_HOST": "changed", "NEW_KEY": "x"}
    result = check_drift(pin, current)
    s = result.summary()
    assert "drifted" in s
    assert "new" in s
    assert "removed" in s


def test_as_dict_structure(baseline_env):
    pin = pin_env(baseline_env, label="staging")
    d = pin.as_dict()
    assert d["label"] == "staging"
    assert d["pinned"] == baseline_env
    assert "drifted" in d
    assert "new_keys" in d
    assert "removed_keys" in d


def test_save_and_load_pin(tmp_path, baseline_env):
    pin = pin_env(baseline_env, label="ci")
    out = tmp_path / "pin.json"
    save_pin(pin, out)
    loaded = load_pin(out)
    assert loaded.label == "ci"
    assert loaded.pinned == baseline_env


def test_load_pin_preserves_drift(tmp_path, baseline_env):
    pin = pin_env(baseline_env, label="dev")
    current = dict(baseline_env)
    current["DB_PORT"] = "9999"
    result = check_drift(pin, current)
    out = tmp_path / "drift.json"
    save_pin(result, out)
    loaded = load_pin(out)
    assert loaded.drifted == {"DB_PORT": "9999"}
