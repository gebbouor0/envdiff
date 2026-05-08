"""Tests for envdiff.profiler."""

import os
import tempfile

import pytest

from envdiff.profiler import (
    ProfileResult,
    format_profile,
    profile,
    profile_file,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: str, content: str) -> None:
    with open(path, "w") as fh:
        fh.write(content)


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


# ---------------------------------------------------------------------------
# profile()
# ---------------------------------------------------------------------------


def test_no_issues_clean_dict():
    result = profile({"HOST": "localhost", "PORT": "5432"})
    assert not result.has_issues
    assert result.total_keys == 2


def test_empty_value_detected():
    result = profile({"HOST": "localhost", "SECRET": ""})
    assert "SECRET" in result.empty_values
    assert result.has_issues


def test_suspicious_key_with_space():
    result = profile({"MY KEY": "value"})
    assert "MY KEY" in result.suspicious_keys
    assert result.has_issues


def test_suspicious_key_with_special_char():
    result = profile({"KEY#1": "val"})
    assert "KEY#1" in result.suspicious_keys


def test_clean_key_not_suspicious():
    result = profile({"DATABASE_URL": "postgres://localhost/db"})
    assert result.suspicious_keys == []


def test_empty_dict():
    result = profile({})
    assert result.total_keys == 0
    assert not result.has_issues


# ---------------------------------------------------------------------------
# ProfileResult.summary()
# ---------------------------------------------------------------------------


def test_summary_no_issues():
    result = ProfileResult(total_keys=3)
    assert "No issues" in result.summary()


def test_summary_with_issues():
    result = ProfileResult(empty_values=["A"], duplicate_keys=[], suspicious_keys=[], total_keys=5)
    text = result.summary()
    assert "empty value" in text


# ---------------------------------------------------------------------------
# profile_file()
# ---------------------------------------------------------------------------


def test_profile_file_reads_empty_value(tmp):
    p = str(tmp / ".env")
    _write(p, "HOST=localhost\nSECRET=\n")
    result = profile_file(p)
    assert "SECRET" in result.empty_values


def test_profile_file_clean(tmp):
    p = str(tmp / ".env")
    _write(p, "HOST=localhost\nPORT=5432\n")
    result = profile_file(p)
    assert not result.has_issues


# ---------------------------------------------------------------------------
# format_profile()
# ---------------------------------------------------------------------------


def test_format_profile_contains_filename():
    result = ProfileResult(total_keys=2)
    report = format_profile(result, filename=".env.prod")
    assert ".env.prod" in report


def test_format_profile_shows_totals():
    result = ProfileResult(empty_values=["X"], total_keys=4)
    report = format_profile(result)
    assert "4" in report
    assert "X" in report
