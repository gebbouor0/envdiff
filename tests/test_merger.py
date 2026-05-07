"""Tests for envdiff.merger."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from envdiff.merger import MergeResult, merge_env_files


@pytest.fixture()
def tmp(tmp_path: Path):
    """Return a helper that writes a named .env file and returns its path."""

    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return str(p)

    return _write


# ---------------------------------------------------------------------------
# Basic merging
# ---------------------------------------------------------------------------

def test_single_file_returns_all_keys(tmp):
    p = tmp("a.env", """
        FOO=1
        BAR=2
    """)
    result = merge_env_files(p)
    assert result.merged == {"FOO": "1", "BAR": "2"}


def test_later_file_overrides_earlier(tmp):
    a = tmp("a.env", "KEY=original\n")
    b = tmp("b.env", "KEY=overridden\n")
    result = merge_env_files(a, b)
    assert result.merged["KEY"] == "overridden"


def test_non_overlapping_keys_all_present(tmp):
    a = tmp("a.env", "ALPHA=1\n")
    b = tmp("b.env", "BETA=2\n")
    result = merge_env_files(a, b)
    assert result.merged == {"ALPHA": "1", "BETA": "2"}


def test_three_files_last_wins(tmp):
    a = tmp("a.env", "X=1\n")
    b = tmp("b.env", "X=2\n")
    c = tmp("c.env", "X=3\n")
    result = merge_env_files(a, b, c)
    assert result.merged["X"] == "3"


# ---------------------------------------------------------------------------
# Override tracking
# ---------------------------------------------------------------------------

def test_overrides_recorded_for_duplicate_key(tmp):
    a = tmp("a.env", "KEY=v1\n")
    b = tmp("b.env", "KEY=v2\n")
    result = merge_env_files(a, b)
    assert "KEY" in result.overridden_keys
    assert len(result.overrides["KEY"]) == 2


def test_no_overrides_for_unique_keys(tmp):
    a = tmp("a.env", "FOO=1\n")
    b = tmp("b.env", "BAR=2\n")
    result = merge_env_files(a, b)
    assert result.overridden_keys == []


def test_override_history_preserves_order(tmp):
    a = tmp("a.env", "K=first\n")
    b = tmp("b.env", "K=second\n")
    result = merge_env_files(a, b)
    values = [v for _, v in result.overrides["K"]]
    assert values == ["first", "second"]


# ---------------------------------------------------------------------------
# MergeResult helpers
# ---------------------------------------------------------------------------

def test_summary_contains_counts(tmp):
    a = tmp("a.env", "A=1\nB=2\n")
    b = tmp("b.env", "B=99\nC=3\n")
    result = merge_env_files(a, b)
    s = result.summary()
    assert "Merged keys" in s
    assert "Overridden keys" in s


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_no_paths_raises():
    with pytest.raises(ValueError, match="At least one"):
        merge_env_files()
