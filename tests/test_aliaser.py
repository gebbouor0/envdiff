"""Tests for envdiff.aliaser."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.aliaser import (
    AliasConfig,
    AliasResult,
    build_alias_config,
    resolve_aliases,
    _find_canonical,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right=["DATABASE_URL", "REDIS_HOST"],
        missing_in_left=["DB_URL"],
        mismatched_values={"APP_SECRET": ("abc", "xyz"), "aws_key": ("A", "B")},
    )


@pytest.fixture()
def config() -> AliasConfig:
    return build_alias_config(
        {
            "DATABASE_URL": ["DB_URL", "DB_CONNECTION"],
            "SECRET_KEY": ["APP_SECRET", "SECRET"],
            "AWS_ACCESS_KEY": ["aws_key", "AWS_KEY*"],
        }
    )


def test_build_alias_config_stores_mappings(config: AliasConfig) -> None:
    assert "DATABASE_URL" in config.mappings
    assert "DB_URL" in config.mappings["DATABASE_URL"]


def test_find_canonical_exact_match(config: AliasConfig) -> None:
    assert _find_canonical("DB_URL", config) == "DATABASE_URL"


def test_find_canonical_wildcard_match(config: AliasConfig) -> None:
    assert _find_canonical("AWS_KEY_ID", config) == "AWS_ACCESS_KEY"


def test_find_canonical_no_match(config: AliasConfig) -> None:
    assert _find_canonical("UNKNOWN_KEY", config) is None


def test_resolved_contains_matched_aliases(
    sample_result: DiffResult, config: AliasConfig
) -> None:
    ar = resolve_aliases(sample_result, config)
    # DB_URL (missing_in_left) -> DATABASE_URL
    assert ar.resolved.get("DB_URL") == "DATABASE_URL"
    # APP_SECRET (mismatched) -> SECRET_KEY
    assert ar.resolved.get("APP_SECRET") == "SECRET_KEY"
    # aws_key (mismatched) -> AWS_ACCESS_KEY
    assert ar.resolved.get("aws_key") == "AWS_ACCESS_KEY"


def test_unresolved_missing_right_contains_no_alias_match(
    sample_result: DiffResult, config: AliasConfig
) -> None:
    ar = resolve_aliases(sample_result, config)
    # DATABASE_URL itself is the canonical; it has no alias pointing to it
    assert "DATABASE_URL" in ar.unresolved_missing_right
    assert "REDIS_HOST" in ar.unresolved_missing_right


def test_has_unresolved_true_when_leftovers(
    sample_result: DiffResult, config: AliasConfig
) -> None:
    ar = resolve_aliases(sample_result, config)
    assert ar.has_unresolved() is True


def test_has_unresolved_false_when_all_resolved() -> None:
    result = DiffResult(
        missing_in_right=[],
        missing_in_left=["DB_URL"],
        mismatched_values={},
    )
    cfg = build_alias_config({"DATABASE_URL": ["DB_URL"]})
    ar = resolve_aliases(result, cfg)
    assert ar.has_unresolved() is False


def test_summary_string(sample_result: DiffResult, config: AliasConfig) -> None:
    ar = resolve_aliases(sample_result, config)
    s = ar.summary()
    assert "resolved" in s
    assert "unresolved" in s


def test_empty_result_no_unresolved() -> None:
    result = DiffResult(missing_in_right=[], missing_in_left=[], mismatched_values={})
    cfg = build_alias_config({})
    ar = resolve_aliases(result, cfg)
    assert not ar.has_unresolved()
    assert ar.resolved == {}
