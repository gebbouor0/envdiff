"""Tests for envdiff.differ unified diff output."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ import (
    UnifiedDiffLine,
    build_unified_diff,
    format_unified_diff,
    print_unified_diff,
)


@pytest.fixture
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"REMOVED_KEY": "old_value"},
        missing_in_left={"NEW_KEY": "new_value"},
        mismatched={"CHANGED": ("before", "after")},
    )


@pytest.fixture
def empty_result() -> DiffResult:
    return DiffResult(missing_in_right={}, missing_in_left={}, mismatched={})


def test_unified_diff_line_with_value():
    line = UnifiedDiffLine("+", "FOO", "bar")
    assert str(line) == "+ FOO=bar"


def test_unified_diff_line_without_value():
    line = UnifiedDiffLine(" ", "FOO")
    assert str(line) == "  FOO"


def test_build_unified_diff_headers(sample_result):
    lines = build_unified_diff(sample_result, "a.env", "b.env")
    assert lines[0] == "--- a.env"
    assert lines[1] == "+++ b.env"


def test_build_unified_diff_missing_in_right(sample_result):
    lines = build_unified_diff(sample_result)
    assert "- REMOVED_KEY=old_value" in lines


def test_build_unified_diff_missing_in_left(sample_result):
    lines = build_unified_diff(sample_result)
    assert "+ NEW_KEY=new_value" in lines


def test_build_unified_diff_mismatched(sample_result):
    lines = build_unified_diff(sample_result)
    assert "- CHANGED=before" in lines
    assert "+ CHANGED=after" in lines


def test_empty_result_only_headers(empty_result):
    lines = build_unified_diff(empty_result)
    assert len(lines) == 2
    assert lines[0].startswith("---")
    assert lines[1].startswith("+++")


def test_format_unified_diff_is_string(sample_result):
    output = format_unified_diff(sample_result)
    assert isinstance(output, str)
    assert "\n" in output


def test_format_unified_diff_contains_all_sections(sample_result):
    output = format_unified_diff(sample_result)
    assert "REMOVED_KEY" in output
    assert "NEW_KEY" in output
    assert "CHANGED" in output


def test_print_unified_diff_outputs(sample_result, capsys):
    print_unified_diff(sample_result, "env.left", "env.right")
    captured = capsys.readouterr()
    assert "--- env.left" in captured.out
    assert "+++ env.right" in captured.out
    assert "REMOVED_KEY" in captured.out
