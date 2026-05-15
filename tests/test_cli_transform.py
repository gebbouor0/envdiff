"""Tests for envdiff.cli_transform."""

import argparse
import pytest

from envdiff.cli_transform import add_transform_args, handle_transform


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_transform_args(p)
    return p


@pytest.fixture
def sample_env() -> dict:
    return {"db_host": "  localhost  ", "api_key": "secret"}


def test_add_transform_args_creates_flag(parser):
    args = parser.parse_args([])
    assert hasattr(args, "transform_rules")


def test_transform_rules_default_none(parser):
    args = parser.parse_args([])
    assert args.transform_rules is None


def test_transform_rules_accepts_single(parser):
    args = parser.parse_args(["--transform", "uppercase_keys"])
    assert args.transform_rules == ["uppercase_keys"]


def test_transform_rules_accepts_multiple(parser):
    args = parser.parse_args(["--transform", "uppercase_keys", "strip_values"])
    assert args.transform_rules == ["uppercase_keys", "strip_values"]


def test_handle_transform_returns_env_unchanged_when_no_rules(sample_env):
    args = argparse.Namespace(transform_rules=None)
    result = handle_transform(args, sample_env)
    assert result == sample_env


def test_handle_transform_uppercase_keys(sample_env):
    args = argparse.Namespace(transform_rules=["uppercase_keys"])
    result = handle_transform(args, sample_env)
    assert "DB_HOST" in result
    assert "db_host" not in result


def test_handle_transform_strip_values(sample_env):
    args = argparse.Namespace(transform_rules=["strip_values"])
    result = handle_transform(args, sample_env)
    assert result["db_host"] == "localhost"


def test_handle_transform_multiple_rules(sample_env):
    args = argparse.Namespace(transform_rules=["uppercase_keys", "strip_values"])
    result = handle_transform(args, sample_env)
    assert "DB_HOST" in result
    assert result["DB_HOST"] == "localhost"


def test_handle_transform_unknown_rule_raises(sample_env):
    args = argparse.Namespace(transform_rules=["nonexistent_rule"])
    with pytest.raises(ValueError, match="Unknown transform rule"):
        handle_transform(args, sample_env)


def test_handle_transform_empty_env():
    args = argparse.Namespace(transform_rules=["uppercase_keys"])
    result = handle_transform(args, {})
    assert result == {}
