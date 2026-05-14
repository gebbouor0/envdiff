"""Tests for envdiff.cli_flatten."""
import argparse
import pytest

from envdiff.cli_flatten import add_flatten_args, handle_flatten
from envdiff.comparator import DiffResult


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_flatten_args(p)
    return p


@pytest.fixture
def diff_result():
    return DiffResult(
        missing_in_right=["DB_HOST", "DB_PORT"],
        missing_in_left=["AWS_KEY"],
        mismatched={"APP_ENV": ("production", "staging")},
    )


def test_add_flatten_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "flatten")
    assert hasattr(args, "flatten_sep")
    assert hasattr(args, "flatten_prefix")


def test_flatten_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.flatten is False


def test_flatten_sep_default(parser):
    args = parser.parse_args([])
    assert args.flatten_sep == "_"


def test_flatten_prefix_default_none(parser):
    args = parser.parse_args([])
    assert args.flatten_prefix is None


def test_handle_flatten_returns_false_when_not_requested(parser, diff_result):
    args = parser.parse_args([])
    assert handle_flatten(args, diff_result) is False


def test_handle_flatten_returns_true_when_requested(parser, diff_result, capsys):
    args = parser.parse_args(["--flatten"])
    result = handle_flatten(args, diff_result)
    assert result is True


def test_handle_flatten_output_contains_groups(parser, diff_result, capsys):
    args = parser.parse_args(["--flatten"])
    handle_flatten(args, diff_result)
    captured = capsys.readouterr()
    assert "DB" in captured.out
    assert "AWS" in captured.out


def test_handle_flatten_output_contains_summary(parser, diff_result, capsys):
    args = parser.parse_args(["--flatten"])
    handle_flatten(args, diff_result)
    captured = capsys.readouterr()
    assert "Flatten summary" in captured.out
    assert "group" in captured.out


def test_handle_flatten_prefix_filter(parser, diff_result, capsys):
    args = parser.parse_args(["--flatten", "--flatten-prefix", "DB"])
    handle_flatten(args, diff_result)
    captured = capsys.readouterr()
    assert "DB" in captured.out
    assert "AWS" not in captured.out


def test_handle_flatten_custom_separator(parser, capsys):
    result = DiffResult(
        missing_in_right=["DB.HOST", "DB.PORT"],
        missing_in_left=[],
        mismatched={},
    )
    args = parser.parse_args(["--flatten", "--flatten-sep", "."])
    handle_flatten(args, result)
    captured = capsys.readouterr()
    assert "DB" in captured.out
