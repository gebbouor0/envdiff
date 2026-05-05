"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare, DiffResult


ENV_A = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "SECRET_KEY": "abc123",
    "DATABASE_URL": "postgres://localhost/dev",
}

ENV_B = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DATABASE_URL": "postgres://localhost/prod",
    "REDIS_URL": "redis://localhost:6379",
}


def test_missing_in_right():
    result = compare(ENV_A, ENV_B)
    assert "SECRET_KEY" in result.missing_in_right


def test_missing_in_left():
    result = compare(ENV_A, ENV_B)
    assert "REDIS_URL" in result.missing_in_left


def test_mismatched_values():
    result = compare(ENV_A, ENV_B)
    assert "DEBUG" in result.mismatched
    assert result.mismatched["DEBUG"] == ("true", "false")
    assert "DATABASE_URL" in result.mismatched


def test_no_mismatch_for_equal_keys():
    result = compare(ENV_A, ENV_B)
    assert "APP_NAME" not in result.mismatched
    assert "APP_NAME" not in result.missing_in_left
    assert "APP_NAME" not in result.missing_in_right


def test_identical_envs_no_differences():
    result = compare(ENV_A, ENV_A, left_name="dev", right_name="dev2")
    assert not result.has_differences


def test_empty_envs():
    result = compare({}, {})
    assert not result.has_differences


def test_one_empty_env():
    result = compare(ENV_A, {})
    assert set(result.missing_in_right) == set(ENV_A.keys())
    assert result.missing_in_left == []
    assert result.mismatched == {}


def test_custom_names_in_summary():
    result = compare(ENV_A, ENV_B, left_name="dev", right_name="prod")
    summary = result.summary()
    assert "dev" in summary
    assert "prod" in summary


def test_summary_no_differences():
    result = compare(ENV_A, ENV_A)
    assert "No differences found" in result.summary()


def test_summary_contains_diff_info():
    result = compare(ENV_A, ENV_B)
    summary = result.summary()
    assert "SECRET_KEY" in summary
    assert "REDIS_URL" in summary
    assert "DEBUG" in summary


def test_none_values_compared():
    left = {"KEY": None}
    right = {"KEY": "value"}
    result = compare(left, right)
    assert "KEY" in result.mismatched
    assert result.mismatched["KEY"] == (None, "value")
