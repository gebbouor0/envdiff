"""Tests for cli_summary helpers."""

import json
import argparse
import pytest
from envdiff.comparator import DiffResult
from envdiff.cli_summary import add_summary_args, handle_summary


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_summary_args(p)
    return p


@pytest.fixture
def diff_result():
    return DiffResult(
        missing_in_left=["A"],
        missing_in_right=["B"],
        mismatched={"C": ("x", "y")},
        common_keys={"C", "D"},
    )


def test_add_summary_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "summary")
    assert hasattr(args, "summary_json")


def test_summary_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.summary is False
    assert args.summary_json is False


def test_handle_summary_returns_false_when_not_requested(parser, diff_result):
    args = parser.parse_args([])
    assert handle_summary(args, diff_result) is False


def test_handle_summary_returns_true_with_flag(parser, diff_result, capsys):
    args = parser.parse_args(["--summary"])
    result = handle_summary(args, diff_result)
    assert result is True


def test_handle_summary_text_output(parser, diff_result, capsys):
    args = parser.parse_args(["--summary"])
    handle_summary(args, diff_result)
    out = capsys.readouterr().out
    assert "Similarity" in out
    assert "%" in out


def test_handle_summary_json_output(parser, diff_result, capsys):
    args = parser.parse_args(["--summary-json"])
    handle_summary(args, diff_result)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "total_keys" in data
    assert "similarity_pct" in data


def test_handle_summary_json_values(parser, diff_result, capsys):
    args = parser.parse_args(["--summary-json"])
    handle_summary(args, diff_result)
    data = json.loads(capsys.readouterr().out)
    assert data["missing_in_left"] == 1
    assert data["missing_in_right"] == 1
    assert data["mismatched"] == 1
