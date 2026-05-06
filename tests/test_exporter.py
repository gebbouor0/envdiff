"""Tests for envdiff.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export, to_csv, to_json, to_markdown


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_right={"SECRET_KEY"},
        missing_in_left={"NEW_FEATURE"},
        mismatched={"DATABASE_URL": ("postgres://old", "postgres://new")},
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(missing_in_right=set(), missing_in_left=set(), mismatched={})


def test_to_json_structure(sample_result: DiffResult) -> None:
    raw = to_json(sample_result)
    data = json.loads(raw)
    assert data["missing_in_right"] == ["SECRET_KEY"]
    assert data["missing_in_left"] == ["NEW_FEATURE"]
    assert data["mismatched"]["DATABASE_URL"] == {
        "left": "postgres://old",
        "right": "postgres://new",
    }


def test_to_json_empty(empty_result: DiffResult) -> None:
    data = json.loads(to_json(empty_result))
    assert data == {"missing_in_right": [], "missing_in_left": [], "mismatched": {}}


def test_to_csv_headers(sample_result: DiffResult) -> None:
    raw = to_csv(sample_result)
    reader = csv.reader(io.StringIO(raw))
    header = next(reader)
    assert header == ["type", "key", "left_value", "right_value"]


def test_to_csv_rows(sample_result: DiffResult) -> None:
    raw = to_csv(sample_result)
    rows = list(csv.reader(io.StringIO(raw)))[1:]  # skip header
    types = {r[0] for r in rows}
    assert "missing_in_right" in types
    assert "missing_in_left" in types
    assert "mismatched" in types


def test_to_markdown_contains_header(sample_result: DiffResult) -> None:
    md = to_markdown(sample_result)
    assert "| Type |" in md
    assert "|------|" in md


def test_to_markdown_contains_keys(sample_result: DiffResult) -> None:
    md = to_markdown(sample_result)
    assert "`SECRET_KEY`" in md
    assert "`NEW_FEATURE`" in md
    assert "`DATABASE_URL`" in md


def test_to_markdown_empty_shows_no_differences(empty_result: DiffResult) -> None:
    md = to_markdown(empty_result)
    assert "No differences" in md


def test_export_dispatch_json(sample_result: DiffResult) -> None:
    out = export(sample_result, "json")
    json.loads(out)  # must be valid JSON


def test_export_dispatch_csv(sample_result: DiffResult) -> None:
    out = export(sample_result, "csv")
    assert "type" in out


def test_export_dispatch_markdown(sample_result: DiffResult) -> None:
    out = export(sample_result, "markdown")
    assert "|" in out


def test_export_invalid_format_raises(sample_result: DiffResult) -> None:
    with pytest.raises(ValueError, match="Unsupported format"):
        export(sample_result, "xml")  # type: ignore[arg-type]
