"""Tests for envdiff.parser."""

import textwrap
from pathlib import Path

import pytest

from envdiff.parser import parse_env_file, _strip_quotes


@pytest.fixture()
def env_file(tmp_path: Path):
    """Factory fixture that writes content to a temp .env file."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p
    return _write


def test_basic_key_value(env_file):
    p = env_file("""
        APP_ENV=production
        DEBUG=false
    """)
    result = parse_env_file(p)
    assert result == {"APP_ENV": "production", "DEBUG": "false"}


def test_quoted_values(env_file):
    p = env_file("""
        SECRET_KEY="my secret"
        GREETING='hello world'
    """)
    result = parse_env_file(p)
    assert result["SECRET_KEY"] == "my secret"
    assert result["GREETING"] == "hello world"


def test_comments_and_blank_lines_ignored(env_file):
    p = env_file("""
        # this is a comment
        FOO=bar

        # another comment
        BAZ=qux
    """)
    result = parse_env_file(p)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_empty_value(env_file):
    p = env_file("EMPTY=\n")
    result = parse_env_file(p)
    assert result["EMPTY"] == ""


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")


def test_invalid_line_raises(env_file):
    p = env_file("THIS IS INVALID\n")
    with pytest.raises(ValueError, match="Invalid syntax"):
        parse_env_file(p)


def test_strip_quotes_double():
    assert _strip_quotes('"hello"') == "hello"


def test_strip_quotes_single():
    assert _strip_quotes("'world'") == "world"


def test_strip_quotes_no_quotes():
    assert _strip_quotes("plain") == "plain"


def test_strip_quotes_mismatched():
    assert _strip_quotes("'mixed\"") == "'mixed\""
