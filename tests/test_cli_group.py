"""Tests for envdiff.cli_group."""

import argparse

import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_group import add_group_args, handle_group


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_group_args(p)
    return p


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_right=["DB_HOST", "APP_NAME"],
        missing_in_left=["AWS_KEY"],
        mismatched=[("DB_PASS", "a", "b")],
    )


def test_add_group_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "group")
    assert hasattr(args, "group_sep")


def test_group_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.group is False


def test_group_sep_default_underscore(parser):
    args = parser.parse_args([])
    assert args.group_sep == "_"


def test_handle_group_returns_false_when_not_requested(parser, diff_result):
    args = parser.parse_args([])
    assert handle_group(args, diff_result) is False


def test_handle_group_returns_true_when_requested(parser, diff_result, capsys):
    args = parser.parse_args(["--group"])
    result = handle_group(args, diff_result)
    assert result is True


def test_handle_group_prints_group_headers(parser, diff_result, capsys):
    args = parser.parse_args(["--group"])
    handle_group(args, diff_result)
    captured = capsys.readouterr()
    assert "DB" in captured.out
    assert "APP" in captured.out
    assert "AWS" in captured.out


def test_handle_group_empty_result_prints_no_groups(parser, capsys):
    args = parser.parse_args(["--group"])
    empty = DiffResult(missing_in_right=[], missing_in_left=[], mismatched=[])
    handle_group(args, empty)
    captured = capsys.readouterr()
    assert "No groups found" in captured.out


def test_handle_group_custom_separator(parser, capsys):
    args = parser.parse_args(["--group", "--group-sep", "."])
    result = DiffResult(
        missing_in_right=["DB.HOST", "DB.PORT"],
        missing_in_left=[],
        mismatched=[],
    )
    handle_group(args, result)
    captured = capsys.readouterr()
    assert "DB" in captured.out
