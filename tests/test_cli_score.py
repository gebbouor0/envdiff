"""Tests for envdiff.cli_score."""

import argparse

import pytest

from envdiff.cli_score import add_score_args, handle_score
from envdiff.scorer import ScoreResult


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_score_args(p)
    return p


@pytest.fixture()
def perfect_score() -> ScoreResult:
    return ScoreResult(
        total_keys=10,
        matching_keys=10,
        missing_in_left=0,
        missing_in_right=0,
        mismatched_values=0,
    )


@pytest.fixture()
def low_score() -> ScoreResult:
    return ScoreResult(
        total_keys=10,
        matching_keys=4,
        missing_in_left=3,
        missing_in_right=2,
        mismatched_values=1,
    )


def test_add_score_args_creates_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "score")
    assert hasattr(args, "score_threshold")


def test_score_flag_default_false(parser):
    args = parser.parse_args([])
    assert args.score is False
    assert args.score_threshold is None


def test_handle_score_returns_false_when_not_requested(parser, perfect_score):
    args = parser.parse_args([])
    assert handle_score(args, perfect_score) is False


def test_handle_score_prints_summary(parser, perfect_score, capsys):
    args = parser.parse_args(["--score"])
    handle_score(args, perfect_score)
    out = capsys.readouterr().out
    assert "100.0%" in out


def test_threshold_not_breached_returns_false(parser, perfect_score):
    args = parser.parse_args(["--score-threshold", "80"])
    assert handle_score(args, perfect_score) is False


def test_threshold_breached_returns_true(parser, low_score, capsys):
    args = parser.parse_args(["--score-threshold", "90"])
    result = handle_score(args, low_score)
    assert result is True
    out = capsys.readouterr().out
    assert "below threshold" in out


def test_score_threshold_implies_output(parser, low_score, capsys):
    # --score-threshold alone (no --score) should still print
    args = parser.parse_args(["--score-threshold", "50"])
    handle_score(args, low_score)
    out = capsys.readouterr().out
    assert "Similarity" in out
