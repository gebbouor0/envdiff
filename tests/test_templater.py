"""Tests for envdiff.templater."""

import os
import pytest

from envdiff.comparator import DiffResult
from envdiff.templater import TemplateResult, from_dict, from_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_right=missing_in_right or [],
        missing_in_left=missing_in_left or [],
        mismatched=mismatched or {},
    )


# ---------------------------------------------------------------------------
# TemplateResult
# ---------------------------------------------------------------------------

def test_render_joins_lines():
    tr = TemplateResult(lines=["A=1", "B=2"])
    assert tr.render() == "A=1\nB=2"


def test_render_empty():
    assert TemplateResult().render() == ""


def test_write_creates_file(tmp_path):
    tr = TemplateResult(lines=["KEY=value"])
    dest = tmp_path / "out.env"
    tr.write(str(dest))
    assert dest.read_text() == "KEY=value\n"


# ---------------------------------------------------------------------------
# from_dict
# ---------------------------------------------------------------------------

def test_from_dict_basic():
    env = {"HOST": "localhost", "PORT": "5432"}
    tr = from_dict(env)
    assert "HOST=localhost" in tr.lines
    assert "PORT=5432" in tr.lines


def test_from_dict_redacts_sensitive_keys():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    tr = from_dict(env, redact_keys=["password"])
    assert "DB_PASSWORD=<db_password>" in tr.lines
    assert "APP_NAME=myapp" in tr.lines


def test_from_dict_custom_placeholder():
    env = {"SECRET_KEY": "abc123"}
    tr = from_dict(env, redact_keys=["secret"], placeholder="CHANGEME")
    assert "SECRET_KEY=CHANGEME" in tr.lines


def test_from_dict_sorted_keys():
    env = {"Z_KEY": "z", "A_KEY": "a", "M_KEY": "m"}
    tr = from_dict(env)
    assert tr.lines == ["A_KEY=a", "M_KEY=m", "Z_KEY=z"]


# ---------------------------------------------------------------------------
# from_diff
# ---------------------------------------------------------------------------

def test_from_diff_missing_in_right_gets_placeholder():
    result = _make_result(missing_in_right=["ONLY_LEFT"])
    tr = from_diff(result)
    assert any("ONLY_LEFT=" in line for line in tr.lines)
    assert "ONLY_LEFT=<only_left>" in tr.lines


def test_from_diff_missing_in_left_gets_placeholder():
    result = _make_result(missing_in_left=["ONLY_RIGHT"])
    tr = from_diff(result)
    assert "ONLY_RIGHT=<only_right>" in tr.lines


def test_from_diff_mismatched_uses_left_value():
    result = _make_result(mismatched={"DB_HOST": ("prod-db", "dev-db")})
    tr = from_diff(result)
    assert "DB_HOST=prod-db" in tr.lines


def test_from_diff_mismatched_with_custom_placeholder():
    result = _make_result(mismatched={"DB_HOST": ("prod-db", "dev-db")})
    tr = from_diff(result, placeholder="FILL_ME")
    assert "DB_HOST=FILL_ME" in tr.lines


def test_from_diff_exclude_mismatched():
    result = _make_result(mismatched={"DB_HOST": ("prod-db", "dev-db")})
    tr = from_diff(result, include_mismatched=False)
    assert not any("DB_HOST" in line for line in tr.lines)


def test_from_diff_empty_result():
    result = _make_result()
    tr = from_diff(result)
    assert tr.lines == []
