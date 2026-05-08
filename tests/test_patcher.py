"""Tests for envdiff.patcher."""

from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.patcher import (
    PatchResult,
    apply_patch,
    build_patch,
    write_patched_env,
)


@pytest.fixture()
def diff() -> DiffResult:
    return DiffResult(
        missing_in_right={"NEW_KEY": "new_val"},
        missing_in_left={"EXTRA_KEY": "extra_val"},
        mismatched={"SHARED": ("left_val", "right_val")},
    )


# --- build_patch ---

def test_build_patch_left_to_right_includes_missing(diff):
    patch = build_patch(diff, direction="left_to_right")
    assert "NEW_KEY" in patch
    assert patch["NEW_KEY"] == "new_val"


def test_build_patch_left_to_right_uses_left_value_for_mismatch(diff):
    patch = build_patch(diff, direction="left_to_right")
    assert patch["SHARED"] == "left_val"


def test_build_patch_right_to_left_includes_missing(diff):
    patch = build_patch(diff, direction="right_to_left")
    assert "EXTRA_KEY" in patch
    assert patch["EXTRA_KEY"] == "extra_val"


def test_build_patch_right_to_left_uses_right_value_for_mismatch(diff):
    patch = build_patch(diff, direction="right_to_left")
    assert patch["SHARED"] == "right_val"


def test_build_patch_invalid_direction_raises(diff):
    with pytest.raises(ValueError, match="Unknown direction"):
        build_patch(diff, direction="sideways")


# --- apply_patch ---

def test_apply_patch_adds_new_keys():
    env = {"EXISTING": "yes"}
    result = apply_patch(env, {"ADDED": "value"})
    assert env["ADDED"] == "value"
    assert "ADDED" in result.applied


def test_apply_patch_overwrites_existing_by_default():
    env = {"KEY": "old"}
    apply_patch(env, {"KEY": "new"})
    assert env["KEY"] == "new"


def test_apply_patch_keep_existing_skips_present_key():
    env = {"KEY": "old"}
    result = apply_patch(env, {"KEY": "new"}, keep_existing=True)
    assert env["KEY"] == "old"
    assert "KEY" in result.skipped
    assert "KEY" not in result.applied


def test_apply_patch_keep_existing_adds_absent_key():
    env = {}
    result = apply_patch(env, {"KEY": "val"}, keep_existing=True)
    assert env["KEY"] == "val"
    assert "KEY" in result.applied


# --- PatchResult ---

def test_patch_result_has_changes():
    r = PatchResult(applied={"A": "1"})
    assert r.has_changes


def test_patch_result_no_changes():
    r = PatchResult()
    assert not r.has_changes


def test_patch_result_summary_with_skipped():
    r = PatchResult(applied={"A": "1"}, skipped=["B"])
    assert "1 applied" in r.summary()
    assert "1 skipped" in r.summary()


# --- write_patched_env ---

def test_write_patched_env_creates_file(tmp_path):
    out = tmp_path / ".env.patched"
    write_patched_env({"FOO": "bar"}, out)
    assert out.exists()


def test_write_patched_env_content(tmp_path):
    out = tmp_path / ".env.patched"
    write_patched_env({"FOO": "bar", "BAZ": "qux"}, out)
    text = out.read_text()
    assert "FOO=bar" in text
    assert "BAZ=qux" in text


def test_write_patched_env_quotes_values_with_spaces(tmp_path):
    out = tmp_path / ".env.patched"
    write_patched_env({"MSG": "hello world"}, out)
    assert 'MSG="hello world"' in out.read_text()


def test_write_patched_env_header(tmp_path):
    out = tmp_path / ".env.patched"
    write_patched_env({"X": "1"}, out, header="auto-generated")
    text = out.read_text()
    assert "# auto-generated" in text
