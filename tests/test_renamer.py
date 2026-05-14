"""Tests for envdiff.renamer."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.renamer import (
    RenameConfig,
    RenameResult,
    build_rename_config,
    rename_result,
)


@pytest.fixture
def sample_result():
    return DiffResult(
        missing_in_right={"OLD_DB_HOST": "localhost"},
        missing_in_left={"OLD_API_KEY": "secret"},
        mismatched={"OLD_PORT": ("5432", "3306")},
        common={"APP_NAME": "myapp"},
    )


def test_build_rename_config_stores_mappings():
    cfg = build_rename_config({"OLD_DB_HOST": "DB_HOST"})
    assert cfg.mappings == {"OLD_DB_HOST": "DB_HOST"}


def test_rename_missing_in_right(sample_result):
    cfg = build_rename_config({"OLD_DB_HOST": "DB_HOST"})
    r = rename_result(sample_result, cfg)
    assert "DB_HOST" in r.result.missing_in_right
    assert "OLD_DB_HOST" not in r.result.missing_in_right


def test_rename_missing_in_left(sample_result):
    cfg = build_rename_config({"OLD_API_KEY": "API_KEY"})
    r = rename_result(sample_result, cfg)
    assert "API_KEY" in r.result.missing_in_left
    assert "OLD_API_KEY" not in r.result.missing_in_left


def test_rename_mismatched(sample_result):
    cfg = build_rename_config({"OLD_PORT": "PORT"})
    r = rename_result(sample_result, cfg)
    assert "PORT" in r.result.mismatched
    assert r.result.mismatched["PORT"] == ("5432", "3306")


def test_rename_common_key(sample_result):
    cfg = build_rename_config({"APP_NAME": "APPLICATION_NAME"})
    r = rename_result(sample_result, cfg)
    assert "APPLICATION_NAME" in r.result.common
    assert "APP_NAME" not in r.result.common


def test_no_matching_keys_no_renames(sample_result):
    cfg = build_rename_config({"NONEXISTENT": "SOMETHING"})
    r = rename_result(sample_result, cfg)
    assert not r.has_renames


def test_has_renames_true(sample_result):
    cfg = build_rename_config({"OLD_DB_HOST": "DB_HOST"})
    r = rename_result(sample_result, cfg)
    assert r.has_renames


def test_renamed_keys_list(sample_result):
    cfg = build_rename_config({"OLD_DB_HOST": "DB_HOST", "OLD_PORT": "PORT"})
    r = rename_result(sample_result, cfg)
    assert len(r.renamed_keys) == 2


def test_summary_with_renames(sample_result):
    cfg = build_rename_config({"OLD_DB_HOST": "DB_HOST"})
    r = rename_result(sample_result, cfg)
    assert "1 key(s) renamed" in r.summary()
    assert "OLD_DB_HOST -> DB_HOST" in r.summary()


def test_summary_no_renames(sample_result):
    cfg = build_rename_config({})
    r = rename_result(sample_result, cfg)
    assert r.summary() == "No keys renamed."


def test_empty_mappings_preserves_result(sample_result):
    cfg = build_rename_config({})
    r = rename_result(sample_result, cfg)
    assert r.result.missing_in_right == sample_result.missing_in_right
    assert r.result.missing_in_left == sample_result.missing_in_left
    assert r.result.mismatched == sample_result.mismatched
    assert r.result.common == sample_result.common
