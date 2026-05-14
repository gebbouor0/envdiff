"""Tests for envdiff.cli_rename."""

import argparse
import json
import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_rename import add_rename_args, handle_rename


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_rename_args(p)
    return p


@pytest.fixture
def diff_result():
    return DiffResult(
        missing_in_right={"OLD_HOST": "localhost"},
        missing_in_left={},
        mismatched={},
        common={},
    )


def test_add_rename_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "rename")
    assert hasattr(args, "rename_map")
    assert hasattr(args, "rename_file")


def test_rename_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.rename is False


def test_rename_map_default_none(parser):
    args = parser.parse_args([])
    assert args.rename_map is None


def test_handle_rename_returns_false_when_not_requested(parser, diff_result):
    args = parser.parse_args([])
    _, applied = handle_rename(args, diff_result)
    assert applied is False


def test_handle_rename_no_map_returns_false(parser, diff_result):
    args = parser.parse_args(["--rename"])
    _, applied = handle_rename(args, diff_result)
    assert applied is False


def test_handle_rename_applies_map(parser, diff_result, capsys):
    mapping = json.dumps({"OLD_HOST": "DB_HOST"})
    args = parser.parse_args(["--rename", "--rename-map", mapping])
    new_result, applied = handle_rename(args, diff_result)
    assert applied is True
    assert "DB_HOST" in new_result.missing_in_right
    assert "OLD_HOST" not in new_result.missing_in_right


def test_handle_rename_prints_summary(parser, diff_result, capsys):
    mapping = json.dumps({"OLD_HOST": "DB_HOST"})
    args = parser.parse_args(["--rename", "--rename-map", mapping])
    handle_rename(args, diff_result)
    captured = capsys.readouterr()
    assert "renamed" in captured.out


def test_handle_rename_from_file(parser, diff_result, tmp_path):
    mapping_file = tmp_path / "renames.json"
    mapping_file.write_text(json.dumps({"OLD_HOST": "DB_HOST"}))
    args = parser.parse_args(["--rename", "--rename-file", str(mapping_file)])
    new_result, applied = handle_rename(args, diff_result)
    assert applied is True
    assert "DB_HOST" in new_result.missing_in_right
