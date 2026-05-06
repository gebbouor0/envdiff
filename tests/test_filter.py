"""Tests for envdiff.filter module."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.filter import filter_result, search_keys


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"DB_HOST": "localhost"},
        missing_in_left={"REDIS_URL": "redis://localhost"},
        mismatched_values={"SECRET_KEY": ("abc123", "xyz789"), "LOG_LEVEL": ("DEBUG", "INFO")},
    )


def test_filter_by_keys(sample_result):
    filtered = filter_result(sample_result, keys=["DB_HOST", "SECRET_KEY"])
    assert filtered.missing_in_right == {"DB_HOST": "localhost"}
    assert filtered.missing_in_left == {}
    assert filtered.mismatched_values == {"SECRET_KEY": ("abc123", "xyz789")}


def test_filter_only_missing(sample_result):
    filtered = filter_result(sample_result, only_missing=True)
    assert filtered.missing_in_right == {"DB_HOST": "localhost"}
    assert filtered.missing_in_left == {"REDIS_URL": "redis://localhost"}
    assert filtered.mismatched_values == {}


def test_filter_only_mismatched(sample_result):
    filtered = filter_result(sample_result, only_mismatched=True)
    assert filtered.missing_in_right == {}
    assert filtered.missing_in_left == {}
    assert set(filtered.mismatched_values.keys()) == {"SECRET_KEY", "LOG_LEVEL"}


def test_filter_mutual_exclusion_raises(sample_result):
    with pytest.raises(ValueError, match="mutually exclusive"):
        filter_result(sample_result, only_missing=True, only_mismatched=True)


def test_filter_empty_keys_list(sample_result):
    filtered = filter_result(sample_result, keys=[])
    assert filtered.missing_in_right == {}
    assert filtered.missing_in_left == {}
    assert filtered.mismatched_values == {}


def test_filter_no_criteria_returns_same_data(sample_result):
    filtered = filter_result(sample_result)
    assert filtered.missing_in_right == sample_result.missing_in_right
    assert filtered.missing_in_left == sample_result.missing_in_left
    assert filtered.mismatched_values == sample_result.mismatched_values


def test_search_keys_case_insensitive(sample_result):
    filtered = search_keys(sample_result, "secret")
    assert set(filtered.mismatched_values.keys()) == {"SECRET_KEY"}
    assert filtered.missing_in_right == {}
    assert filtered.missing_in_left == {}


def test_search_keys_matches_multiple(sample_result):
    # 'log' matches LOG_LEVEL
    filtered = search_keys(sample_result, "log")
    assert "LOG_LEVEL" in filtered.mismatched_values


def test_search_keys_no_match_returns_empty(sample_result):
    filtered = search_keys(sample_result, "NONEXISTENT")
    assert not filtered.missing_in_right
    assert not filtered.missing_in_left
    assert not filtered.mismatched_values


def test_search_keys_matches_missing(sample_result):
    filtered = search_keys(sample_result, "DB")
    assert filtered.missing_in_right == {"DB_HOST": "localhost"}
    assert filtered.missing_in_left == {}
    assert filtered.mismatched_values == {}
