"""Tests for envdiff.reporter."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.reporter import format_report


def _make_result(
    missing_in_right=None,
    missing_in_left=None,
    mismatched_values=None,
):
    return DiffResult(
        missing_in_right=set(missing_in_right or []),
        missing_in_left=set(missing_in_left or []),
        mismatched_values=dict(mismatched_values or {}),
    )


def test_no_differences_message():
    result = _make_result()
    report = format_report(result, use_color=False)
    assert "No differences found" in report


def test_missing_in_right_shown():
    result = _make_result(missing_in_right=["SECRET_KEY"])
    report = format_report(result, left_name="prod", right_name="dev", use_color=False)
    assert "Missing in dev" in report
    assert "SECRET_KEY" in report


def test_missing_in_left_shown():
    result = _make_result(missing_in_left=["NEW_VAR"])
    report = format_report(result, left_name="prod", right_name="dev", use_color=False)
    assert "Missing in prod" in report
    assert "NEW_VAR" in report


def test_mismatched_values_shown():
    result = _make_result(mismatched_values={"DB_HOST": ("localhost", "db.prod.example.com")})
    report = format_report(result, left_name="dev", right_name="prod", use_color=False)
    assert "Mismatched values" in report
    assert "DB_HOST" in report
    assert "localhost" in report
    assert "db.prod.example.com" in report


def test_header_contains_names():
    result = _make_result()
    report = format_report(result, left_name="staging", right_name="production", use_color=False)
    assert "staging" in report
    assert "production" in report


def test_summary_line_included():
    result = _make_result(
        missing_in_right=["A"],
        missing_in_left=["B"],
        mismatched_values={"C": ("1", "2")},
    )
    report = format_report(result, use_color=False)
    # summary() from comparator should appear
    assert "missing" in report.lower() or "mismatch" in report.lower()


def test_color_codes_present_when_enabled():
    result = _make_result(missing_in_right=["KEY"])
    report = format_report(result, use_color=True)
    assert "\033[" in report


def test_color_codes_absent_when_disabled():
    result = _make_result(missing_in_right=["KEY"])
    report = format_report(result, use_color=False)
    assert "\033[" not in report


def test_keys_sorted_in_output():
    result = _make_result(missing_in_right=["ZEBRA", "ALPHA", "MIDDLE"])
    report = format_report(result, use_color=False)
    idx_alpha = report.index("ALPHA")
    idx_middle = report.index("MIDDLE")
    idx_zebra = report.index("ZEBRA")
    assert idx_alpha < idx_middle < idx_zebra
