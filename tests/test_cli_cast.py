"""Tests for envdiff.cli_cast."""
import argparse
import pytest
from envdiff.cli_cast import add_cast_args, handle_cast


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_cast_args(p)
    return p


def test_add_cast_args_creates_flags(parser):
    actions = {a.dest for a in parser._actions}
    assert "cast" in actions
    assert "cast_schema" in actions


def test_cast_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.cast is False


def test_cast_schema_default_none(parser):
    args = parser.parse_args([])
    assert args.cast_schema is None


def test_handle_cast_returns_false_when_not_requested(parser):
    args = parser.parse_args([])
    assert handle_cast(args, {"PORT": "8080"}) is False


def test_handle_cast_returns_true_when_requested(parser, capsys):
    args = parser.parse_args(["--cast", "--cast-schema", '{"PORT":"int"}'])
    result = handle_cast(args, {"PORT": "8080"})
    assert result is True


def test_handle_cast_output_contains_casted_value(parser, capsys):
    args = parser.parse_args(["--cast", "--cast-schema", '{"PORT":"int"}'])
    handle_cast(args, {"PORT": "9000"})
    out = capsys.readouterr().out
    assert "PORT" in out
    assert "9000" in out
    assert "int" in out


def test_handle_cast_invalid_json_schema(parser, capsys):
    args = parser.parse_args(["--cast", "--cast-schema", "not-json"])
    result = handle_cast(args, {"A": "1"})
    assert result is True
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_handle_cast_failure_shown_in_output(parser, capsys):
    args = parser.parse_args(["--cast", "--cast-schema", '{"PORT":"int"}'])
    handle_cast(args, {"PORT": "not_a_number"})
    out = capsys.readouterr().out
    assert "Failures" in out
    assert "PORT" in out


def test_handle_cast_no_schema_treats_all_as_str(parser, capsys):
    args = parser.parse_args(["--cast"])
    handle_cast(args, {"NAME": "alice"})
    out = capsys.readouterr().out
    assert "NAME" in out
    assert "str" in out
