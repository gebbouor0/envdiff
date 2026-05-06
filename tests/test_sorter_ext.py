"""Tests for envdiff.sorter_ext extended sorting utilities."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter_ext import ExtSortOrder, sort_result_ext


@pytest.fixture
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"ZEBRA": "z", "APE": "a", "MONKEY": "m"},
        missing_in_left={"BB": "b", "AAAA": "a"},
        mismatched={
            "KEY": ("short", "much_longer_value"),
            "LONGKEY": ("x", "y"),
        },
    )


def test_insertion_order_preserved(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.INSERTION)
    assert list(sorted_r.missing_in_right.keys()) == ["ZEBRA", "APE", "MONKEY"]
    assert list(sorted_r.missing_in_left.keys()) == ["BB", "AAAA"]
    assert list(sorted_r.mismatched.keys()) == ["KEY", "LONGKEY"]


def test_key_length_sort(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.KEY_LENGTH)
    keys = list(sorted_r.missing_in_right.keys())
    # APE(3) < ZEBRA(5) < MONKEY(6)
    assert keys == ["APE", "ZEBRA", "MONKEY"]


def test_key_length_sort_missing_in_left(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.KEY_LENGTH)
    keys = list(sorted_r.missing_in_left.keys())
    # BB(2) < AAAA(4)
    assert keys == ["BB", "AAAA"]


def test_key_length_sort_mismatched(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.KEY_LENGTH)
    keys = list(sorted_r.mismatched.keys())
    # KEY(3) < LONGKEY(7)
    assert keys == ["KEY", "LONGKEY"]


def test_value_length_sort_missing_in_right(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.VALUE_LENGTH)
    keys = list(sorted_r.missing_in_right.keys())
    # values: z(1), a(1), m(1) — all same length, stable sort keeps original order
    assert set(keys) == {"ZEBRA", "APE", "MONKEY"}


def test_value_length_sort_mismatched_by_left_value(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.VALUE_LENGTH)
    keys = list(sorted_r.mismatched.keys())
    # left values: KEY->"short"(5), LONGKEY->"x"(1)
    # sorted ascending: LONGKEY(1) < KEY(5)
    assert keys == ["LONGKEY", "KEY"]


def test_sort_returns_new_object(sample_result):
    sorted_r = sort_result_ext(sample_result, ExtSortOrder.KEY_LENGTH)
    assert sorted_r is not sample_result


def test_invalid_order_raises(sample_result):
    with pytest.raises((ValueError, AttributeError)):
        sort_result_ext(sample_result, "bad_order")  # type: ignore
