"""Tests for envdiff.cli."""

import pytest
from pathlib import Path
from envdiff.cli import run


@pytest.fixture
def tmp_env(tmp_path):
    """Helper that writes a .env file and returns its path."""
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def test_identical_files_exit_zero(tmp_env):
    left = tmp_env("a.env", "KEY=value\nFOO=bar\n")
    right = tmp_env("b.env", "KEY=value\nFOO=bar\n")
    assert run([str(left), str(right), "--no-color"]) == 0


def test_differences_exit_zero_without_flag(tmp_env):
    left = tmp_env("a.env", "KEY=value\n")
    right = tmp_env("b.env", "OTHER=value\n")
    assert run([str(left), str(right), "--no-color"]) == 0


def test_differences_exit_one_with_flag(tmp_env):
    left = tmp_env("a.env", "KEY=value\n")
    right = tmp_env("b.env", "OTHER=value\n")
    assert run([str(left), str(right), "--no-color", "--exit-code"]) == 1


def test_missing_file_returns_2(tmp_env, tmp_path):
    left = tmp_env("a.env", "KEY=value\n")
    missing = tmp_path / "nonexistent.env"
    assert run([str(left), str(missing), "--no-color"]) == 2


def test_output_contains_filenames(tmp_env, capsys):
    left = tmp_env("prod.env", "KEY=value\n")
    right = tmp_env("dev.env", "KEY=value\n")
    run([str(left), str(right), "--no-color"])
    captured = capsys.readouterr()
    assert "prod.env" in captured.out
    assert "dev.env" in captured.out


def test_missing_key_shown_in_output(tmp_env, capsys):
    left = tmp_env("a.env", "SECRET=abc\nCOMMON=x\n")
    right = tmp_env("b.env", "COMMON=x\n")
    run([str(left), str(right), "--no-color"])
    captured = capsys.readouterr()
    assert "SECRET" in captured.out


def test_mismatch_shown_in_output(tmp_env, capsys):
    left = tmp_env("a.env", "DB_URL=localhost\n")
    right = tmp_env("b.env", "DB_URL=remotehost\n")
    run([str(left), str(right), "--no-color"])
    captured = capsys.readouterr()
    assert "DB_URL" in captured.out
