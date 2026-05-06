"""Tests for envdiff.summarizer."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.summarizer import summarize, format_summary, DiffSummary


@pytest.fixture
def full_result():
    return DiffResult(
        missing_in_left=["KEY_A"],
        missing_in_right=["KEY_B", "KEY_C"],
        mismatched={"KEY_D": ("val1", "val2")},
        common_keys={"KEY_D", "KEY_E"},
    )


@pytest.fixture
def empty_result():
    return DiffResult(
        missing_in_left=[],
        missing_in_right=[],
        mismatched={},
        common_keys={"X", "Y"},
    )


def test_total_keys(full_result):
    s = summarize(full_result)
    # KEY_A, KEY_B, KEY_C, KEY_D, KEY_E
    assert s.total_keys == 5


def test_missing_counts(full_result):
    s = summarize(full_result)
    assert s.missing_in_left_count == 1
    assert s.missing_in_right_count == 2


def test_mismatched_count(full_result):
    s = summarize(full_result)
    assert s.mismatched_count == 1


def test_match_count(full_result):
    s = summarize(full_result)
    # common_keys={KEY_D, KEY_E}, mismatched=1 => match=1
    assert s.match_count == 1


def test_similarity_pct_full(full_result):
    s = summarize(full_result)
    # 1 matching out of 5 total => 20.0%
    assert s.similarity_pct == pytest.approx(20.0, rel=1e-3)


def test_similarity_pct_empty_result():
    result = DiffResult(
        missing_in_left=[],
        missing_in_right=[],
        mismatched={},
        common_keys=set(),
    )
    s = summarize(result)
    assert s.similarity_pct == pytest.approx(100.0)


def test_perfect_match(empty_result):
    s = summarize(empty_result)
    assert s.match_count == 2
    assert s.similarity_pct == pytest.approx(100.0)


def test_as_dict_keys(full_result):
    d = summarize(full_result).as_dict()
    assert set(d.keys()) == {
        "total_keys", "missing_in_left", "missing_in_right",
        "mismatched", "matching", "similarity_pct", "type_breakdown",
    }


def test_format_summary_contains_pct(full_result):
    text = format_summary(summarize(full_result))
    assert "%" in text
    assert "20.0%" in text


def test_format_summary_all_fields(empty_result):
    text = format_summary(summarize(empty_result))
    for label in ("Total", "Matching", "Mismatched", "Similarity"):
        assert label in text
