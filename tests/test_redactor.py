"""Tests for envdiff.redactor."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.redactor import (
    REDACTED,
    RedactConfig,
    _matches_any,
    build_redact_config,
    redact_result,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"DB_PASSWORD": "secret123", "HOST": "localhost"},
        missing_in_left={"API_KEY": "abc", "PORT": "5432"},
        mismatched_values={
            "SECRET_TOKEN": ("tok_a", "tok_b"),
            "APP_NAME": ("myapp", "otherapp"),
        },
    )


def test_matches_any_default_patterns():
    assert _matches_any("DB_PASSWORD", [r".*PASSWORD.*"], False)
    assert _matches_any("db_password", [r".*PASSWORD.*"], False)  # case-insensitive
    assert not _matches_any("HOST", [r".*PASSWORD.*"], False)


def test_matches_any_case_sensitive():
    assert not _matches_any("db_password", [r".*PASSWORD.*"], True)
    assert _matches_any("DB_PASSWORD", [r".*PASSWORD.*"], True)


def test_redact_missing_in_right(sample_result):
    out = redact_result(sample_result)
    assert out.missing_in_right["DB_PASSWORD"] == REDACTED
    assert out.missing_in_right["HOST"] == "localhost"  # not sensitive


def test_redact_missing_in_left(sample_result):
    out = redact_result(sample_result)
    assert out.missing_in_left["API_KEY"] == REDACTED
    assert out.missing_in_left["PORT"] == "5432"  # not sensitive


def test_redact_mismatched_values(sample_result):
    out = redact_result(sample_result)
    assert out.mismatched_values["SECRET_TOKEN"] == (REDACTED, REDACTED)
    assert out.mismatched_values["APP_NAME"] == ("myapp", "otherapp")  # safe


def test_original_result_not_mutated(sample_result):
    redact_result(sample_result)
    assert sample_result.missing_in_right["DB_PASSWORD"] == "secret123"
    assert sample_result.mismatched_values["SECRET_TOKEN"] == ("tok_a", "tok_b")


def test_custom_placeholder(sample_result):
    config = RedactConfig(placeholder="<hidden>")
    out = redact_result(sample_result, config)
    assert out.missing_in_right["DB_PASSWORD"] == "<hidden>"


def test_custom_patterns(sample_result):
    config = build_redact_config(patterns=[r"HOST"])
    out = redact_result(sample_result, config)
    assert out.missing_in_right["HOST"] == REDACTED
    assert out.missing_in_right["DB_PASSWORD"] == "secret123"  # not in custom list


def test_empty_result_no_error():
    empty = DiffResult(missing_in_right={}, missing_in_left={}, mismatched_values={})
    out = redact_result(empty)
    assert out.missing_in_right == {}
    assert out.missing_in_left == {}
    assert out.mismatched_values == {}


def test_build_redact_config_defaults():
    cfg = build_redact_config()
    assert cfg.placeholder == REDACTED
    assert cfg.case_sensitive is False
    assert any("SECRET" in p for p in cfg.patterns)


def test_build_redact_config_custom():
    cfg = build_redact_config(patterns=[r"CUSTOM_.*"], placeholder="XXX", case_sensitive=True)
    assert cfg.patterns == [r"CUSTOM_.*"]
    assert cfg.placeholder == "XXX"
    assert cfg.case_sensitive is True
