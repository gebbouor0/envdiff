"""Tests for envdiff.annotator."""

import pytest
from envdiff.annotator import (
    Annotation,
    _guess_type,
    _build_notes,
    annotate,
    annotations_as_dict,
)


# ---------------------------------------------------------------------------
# _guess_type
# ---------------------------------------------------------------------------

def test_guess_type_empty():
    assert _guess_type("") == "empty"


def test_guess_type_bool_true():
    assert _guess_type("true") == "bool"
    assert _guess_type("True") == "bool"
    assert _guess_type("yes") == "bool"
    assert _guess_type("0") == "bool"


def test_guess_type_int():
    assert _guess_type("42") == "int"
    assert _guess_type("-7") == "int"


def test_guess_type_float():
    assert _guess_type("3.14") == "float"


def test_guess_type_url():
    assert _guess_type("https://example.com") == "url"
    assert _guess_type("http://localhost:8080") == "url"


def test_guess_type_string():
    assert _guess_type("hello world") == "string"


# ---------------------------------------------------------------------------
# _build_notes
# ---------------------------------------------------------------------------

def test_notes_empty_value():
    notes = _build_notes("MY_KEY", "", "empty")
    assert "value is empty" in notes


def test_notes_key_with_space():
    notes = _build_notes("my key", "val", "string")
    assert "key contains spaces" in notes


def test_notes_lowercase_key():
    notes = _build_notes("my_key", "val", "string")
    assert "key is not uppercase" in notes


def test_notes_clean_key_no_notes():
    notes = _build_notes("MY_KEY", "hello", "string")
    assert notes == []


def test_notes_long_value():
    notes = _build_notes("MY_KEY", "x" * 201, "string")
    assert "value is unusually long" in notes


# ---------------------------------------------------------------------------
# annotate
# ---------------------------------------------------------------------------

def test_annotate_returns_annotation_per_key():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = annotate(env, source=".env")
    assert len(result) == 2
    keys = {a.key for a in result}
    assert keys == {"HOST", "PORT"}


def test_annotate_source_set_correctly():
    result = annotate({"KEY": "val"}, source=".env.production")
    assert result[0].source == ".env.production"


def test_annotate_value_type_detected():
    result = annotate({"DEBUG": "true", "WORKERS": "4"}, source=".env")
    by_key = {a.key: a for a in result}
    assert by_key["DEBUG"].value_type == "bool"
    assert by_key["WORKERS"].value_type == "int"


def test_annotate_empty_env():
    result = annotate({}, source=".env")
    assert result == []


# ---------------------------------------------------------------------------
# annotations_as_dict
# ---------------------------------------------------------------------------

def test_annotations_as_dict_structure():
    result = annotate({"API_URL": "https://api.example.com"}, source=".env")
    data = annotations_as_dict(result)
    assert isinstance(data, list)
    assert data[0]["key"] == "API_URL"
    assert data[0]["value_type"] == "url"
    assert "source" in data[0]
    assert "notes" in data[0]
