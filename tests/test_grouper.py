"""Tests for envdiff.grouper."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.grouper import GroupResult, _prefix, group_result


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right=["DB_HOST", "DB_PORT", "APP_NAME"],
        missing_in_left=["AWS_KEY"],
        mismatched=[("DB_PASS", "secret", "other"), ("APP_DEBUG", "true", "false")],
    )


def test_prefix_with_separator():
    assert _prefix("DB_HOST", "_") == "DB"
    assert _prefix("AWS_SECRET_KEY", "_") == "AWS"


def test_prefix_no_separator_returns_other():
    assert _prefix("HOSTNAME", "_") == "__other__"
    assert _prefix("_LEADING", "_") == "__other__"


def test_group_names_sorted(sample_result):
    gr = group_result(sample_result)
    assert gr.group_names == sorted(gr.group_names)


def test_db_group_has_correct_missing(sample_result):
    gr = group_result(sample_result)
    assert "DB" in gr.groups
    db = gr.groups["DB"]
    assert "DB_HOST" in db.missing_in_right
    assert "DB_PORT" in db.missing_in_right


def test_db_group_has_mismatch(sample_result):
    gr = group_result(sample_result)
    db = gr.groups["DB"]
    keys = [k for k, _, _ in db.mismatched]
    assert "DB_PASS" in keys


def test_app_group_split_correctly(sample_result):
    gr = group_result(sample_result)
    assert "APP" in gr.groups
    app = gr.groups["APP"]
    assert "APP_NAME" in app.missing_in_right
    assert any(k == "APP_DEBUG" for k, _, _ in app.mismatched)


def test_aws_group_missing_in_left(sample_result):
    gr = group_result(sample_result)
    assert "AWS" in gr.groups
    assert "AWS_KEY" in gr.groups["AWS"].missing_in_left


def test_empty_result_gives_no_groups():
    empty = DiffResult(missing_in_right=[], missing_in_left=[], mismatched=[])
    gr = group_result(empty)
    assert gr.groups == {}


def test_summary_contains_group_names(sample_result):
    gr = group_result(sample_result)
    summary = gr.summary()
    for name in gr.group_names:
        assert name in summary


def test_custom_separator():
    result = DiffResult(
        missing_in_right=["DB.HOST", "DB.PORT"],
        missing_in_left=[],
        mismatched=[],
    )
    gr = group_result(result, separator=".")
    assert "DB" in gr.groups
    assert len(gr.groups["DB"].missing_in_right) == 2
