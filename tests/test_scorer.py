"""Tests for envdiff.scorer."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.scorer import ScoreResult, score


def _make_result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched_values=None,
    total_keys=None,
) -> DiffResult:
    r = DiffResult(
        left_name="left",
        right_name="right",
        missing_in_right=missing_in_right or [],
        missing_in_left=missing_in_left or [],
        mismatched_values=mismatched_values or {},
    )
    if total_keys is not None:
        r._total_keys = total_keys
    return r


def test_perfect_match_score():
    result = _make_result(total_keys=5)
    s = score(result)
    assert s.score == 1.0
    assert s.percent == 100.0
    assert s.matching_keys == 5


def test_all_missing_in_right():
    result = _make_result(
        missing_in_right=["A", "B", "C"], total_keys=3
    )
    s = score(result)
    assert s.score == 0.0
    assert s.matching_keys == 0
    assert s.missing_in_right == 3


def test_partial_mismatch():
    result = _make_result(
        mismatched_values={"KEY": ("v1", "v2")},
        total_keys=4,
    )
    s = score(result)
    assert s.matching_keys == 3
    assert s.total_keys == 4
    assert s.score == pytest.approx(0.75)


def test_empty_result_score_is_one():
    result = _make_result(total_keys=0)
    s = score(result)
    assert s.score == 1.0


def test_summary_string():
    result = _make_result(total_keys=10)
    s = score(result)
    assert "100.0%" in s.summary()
    assert "10/10" in s.summary()


def test_as_dict_keys():
    result = _make_result(total_keys=6)
    d = score(result).as_dict()
    assert set(d.keys()) == {
        "score", "percent", "total_keys", "matching_keys",
        "missing_in_left", "missing_in_right", "mismatched_values",
    }


def test_score_result_percent_equals_score_times_100():
    result = _make_result(
        missing_in_right=["X"], missing_in_left=["Y"], total_keys=4
    )
    s = score(result)
    assert abs(s.percent - s.score * 100) < 0.001


def test_fallback_when_total_keys_not_set():
    # _total_keys defaults to 0, so only problem keys are counted
    result = DiffResult(
        missing_in_right=["A"],
        missing_in_left=[],
        mismatched_values={},
    )
    s = score(result)
    # total == problem_keys == 1, matching == 0
    assert s.total_keys == 1
    assert s.matching_keys == 0
