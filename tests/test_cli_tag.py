"""Tests for envdiff.cli_tag."""

import json
from argparse import ArgumentParser
from pathlib import Path
from types import SimpleNamespace

import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_tag import add_tag_args, handle_tag


@pytest.fixture
def parser() -> ArgumentParser:
    p = ArgumentParser()
    add_tag_args(p)
    return p


@pytest.fixture
def diff_result() -> DiffResult:
    return DiffResult(
        missing_in_right=["DB_HOST"],
        missing_in_left=["REDIS_URL"],
        mismatched={"AWS_KEY": ("a", "b")},
    )


def test_add_tag_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "tag")
    assert hasattr(args, "tag_config")


def test_tag_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.tag is False


def test_tag_config_default_none(parser):
    args = parser.parse_args([])
    assert args.tag_config is None


def test_handle_tag_returns_false_when_not_requested(diff_result):
    args = SimpleNamespace(tag=False, tag_config=None)
    assert handle_tag(args, diff_result) is False


def test_handle_tag_returns_true_when_requested(diff_result, capsys):
    args = SimpleNamespace(tag=True, tag_config=None)
    result = handle_tag(args, diff_result)
    assert result is True


def test_handle_tag_no_config_prints_no_keys_tagged(diff_result, capsys):
    args = SimpleNamespace(tag=True, tag_config=None)
    handle_tag(args, diff_result)
    captured = capsys.readouterr()
    assert "No keys tagged." in captured.out


def test_handle_tag_with_config_file(diff_result, tmp_path, capsys):
    cfg = {"database": ["DB_*"], "cache": ["REDIS_*"]}
    cfg_file = tmp_path / "tags.json"
    cfg_file.write_text(json.dumps(cfg))
    args = SimpleNamespace(tag=True, tag_config=str(cfg_file))
    handle_tag(args, diff_result)
    captured = capsys.readouterr()
    assert "[database]" in captured.out
    assert "[cache]" in captured.out
