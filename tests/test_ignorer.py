"""Tests for envdiff.ignorer."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.ignorer import (
    IgnoreConfig,
    apply_ignore,
    build_ignore_config,
    should_ignore,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"SECRET_KEY": "abc", "DB_HOST": "localhost"},
        missing_in_left={"API_TOKEN": "xyz"},
        mismatched={"DEBUG": ("true", "false"), "SECRET_SALT": ("a", "b")},
        common_keys={"DEBUG", "SECRET_SALT", "APP_NAME"},
    )


# --- should_ignore ---

def test_exact_key_ignored():
    cfg = IgnoreConfig(exact_keys={"SECRET_KEY"})
    assert should_ignore("SECRET_KEY", cfg) is True


def test_exact_key_not_ignored_when_absent():
    cfg = IgnoreConfig(exact_keys={"OTHER_KEY"})
    assert should_ignore("SECRET_KEY", cfg) is False


def test_wildcard_pattern_matches():
    cfg = IgnoreConfig(patterns=["SECRET_*"])
    assert should_ignore("SECRET_KEY", cfg) is True
    assert should_ignore("SECRET_SALT", cfg) is True


def test_wildcard_pattern_no_match():
    cfg = IgnoreConfig(patterns=["SECRET_*"])
    assert should_ignore("DB_HOST", cfg) is False


def test_multiple_patterns():
    cfg = IgnoreConfig(patterns=["SECRET_*", "DB_*"])
    assert should_ignore("DB_HOST", cfg) is True
    assert should_ignore("SECRET_KEY", cfg) is True
    assert should_ignore("API_TOKEN", cfg) is False


def test_empty_config_ignores_nothing():
    cfg = IgnoreConfig()
    assert should_ignore("ANYTHING", cfg) is False


# --- apply_ignore ---

def test_apply_ignore_removes_exact_key(sample_result):
    cfg = build_ignore_config(exact_keys=["SECRET_KEY"])
    result = apply_ignore(sample_result, cfg)
    assert "SECRET_KEY" not in result.missing_in_right
    assert "DB_HOST" in result.missing_in_right


def test_apply_ignore_wildcard_across_sections(sample_result):
    cfg = build_ignore_config(patterns=["SECRET_*"])
    result = apply_ignore(sample_result, cfg)
    assert "SECRET_KEY" not in result.missing_in_right
    assert "SECRET_SALT" not in result.mismatched
    assert "SECRET_SALT" not in result.common_keys


def test_apply_ignore_missing_in_left(sample_result):
    cfg = build_ignore_config(exact_keys=["API_TOKEN"])
    result = apply_ignore(sample_result, cfg)
    assert "API_TOKEN" not in result.missing_in_left


def test_apply_ignore_empty_config_unchanged(sample_result):
    cfg = IgnoreConfig()
    result = apply_ignore(sample_result, cfg)
    assert result.missing_in_right == sample_result.missing_in_right
    assert result.missing_in_left == sample_result.missing_in_left
    assert result.mismatched == sample_result.mismatched
    assert result.common_keys == sample_result.common_keys


# --- build_ignore_config ---

def test_build_ignore_config_defaults():
    cfg = build_ignore_config()
    assert cfg.patterns == []
    assert cfg.exact_keys == set()


def test_build_ignore_config_with_values():
    cfg = build_ignore_config(patterns=["FOO_*"], exact_keys=["BAR"])
    assert "FOO_*" in cfg.patterns
    assert "BAR" in cfg.exact_keys
