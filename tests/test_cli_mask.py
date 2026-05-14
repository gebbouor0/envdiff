"""Tests for envdiff.cli_mask."""
import argparse
import json
import pytest
from pathlib import Path

from envdiff.cli_mask import add_mask_args, handle_mask


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_mask_args(p)
    return p


@pytest.fixture
def tmp_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PASSWORD=secret\nAPI_KEY=abc\n")
    return str(f)


def test_add_mask_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "mask")
    assert hasattr(args, "mask_patterns")
    assert hasattr(args, "mask_placeholder")


def test_mask_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.mask is False


def test_mask_patterns_default_none(parser):
    args = parser.parse_args([])
    assert args.mask_patterns is None


def test_mask_placeholder_default(parser):
    args = parser.parse_args([])
    assert args.mask_placeholder == "***"


def test_handle_mask_returns_false_when_not_requested(parser, tmp_env):
    args = parser.parse_args([])
    args.left = tmp_env
    assert handle_mask(args, env_path=tmp_env) is False


def test_handle_mask_returns_true_when_requested(parser, tmp_env, capsys):
    args = parser.parse_args(["--mask"])
    args.left = tmp_env
    result = handle_mask(args, env_path=tmp_env)
    assert result is True


def test_handle_mask_output_contains_placeholder(parser, tmp_env, capsys):
    args = parser.parse_args(["--mask"])
    result = handle_mask(args, env_path=tmp_env)
    captured = capsys.readouterr()
    assert "***" in captured.out


def test_handle_mask_no_env_path_prints_message(parser, capsys):
    args = parser.parse_args(["--mask"])
    # no left attr, no env_path
    result = handle_mask(args, env_path=None)
    captured = capsys.readouterr()
    assert result is True
    assert "No env file" in captured.out


def test_handle_mask_custom_placeholder(parser, tmp_env, capsys):
    args = parser.parse_args(["--mask", "--mask-placeholder", "[HIDDEN]"])
    handle_mask(args, env_path=tmp_env)
    captured = capsys.readouterr()
    assert "[HIDDEN]" in captured.out
