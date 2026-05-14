"""Tests for envdiff.masker."""
import pytest
from envdiff.masker import (
    MaskConfig,
    MaskResult,
    _matches_any,
    build_mask_config,
    mask_env,
    MASK_PLACEHOLDER,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "supersecret",
        "AWS_SECRET_KEY": "abc123",
        "API_KEY": "keyvalue",
        "APP_NAME": "myapp",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_matches_any_default_patterns():
    assert _matches_any("DB_PASSWORD", ["*PASSWORD*"], False) is True
    assert _matches_any("DB_HOST", ["*PASSWORD*"], False) is False


def test_matches_any_case_insensitive():
    assert _matches_any("db_password", ["*PASSWORD*"], False) is True


def test_matches_any_case_sensitive_no_match():
    assert _matches_any("db_password", ["*PASSWORD*"], True) is False


def test_mask_env_masks_sensitive_keys(sample_env):
    result = mask_env(sample_env)
    assert result.masked["DB_PASSWORD"] == MASK_PLACEHOLDER
    assert result.masked["AWS_SECRET_KEY"] == MASK_PLACEHOLDER
    assert result.masked["API_KEY"] == MASK_PLACEHOLDER
    assert result.masked["AUTH_TOKEN"] == MASK_PLACEHOLDER


def test_mask_env_preserves_safe_keys(sample_env):
    result = mask_env(sample_env)
    assert result.masked["DB_HOST"] == "localhost"
    assert result.masked["APP_NAME"] == "myapp"


def test_mask_env_original_unchanged(sample_env):
    result = mask_env(sample_env)
    assert result.original["DB_PASSWORD"] == "supersecret"


def test_masked_keys_list(sample_env):
    result = mask_env(sample_env)
    assert "DB_PASSWORD" in result.masked_keys
    assert "DB_HOST" not in result.masked_keys


def test_has_masked_true(sample_env):
    result = mask_env(sample_env)
    assert result.has_masked is True


def test_has_masked_false():
    result = mask_env({"DB_HOST": "localhost", "APP_NAME": "app"})
    assert result.has_masked is False


def test_summary_no_masked():
    result = mask_env({"DB_HOST": "localhost"})
    assert result.summary == "No keys masked."


def test_summary_with_masked(sample_env):
    result = mask_env(sample_env)
    assert "masked" in result.summary
    assert str(len(result.masked_keys)) in result.summary


def test_custom_placeholder(sample_env):
    config = build_mask_config(placeholder="[REDACTED]")
    result = mask_env(sample_env, config=config)
    assert result.masked["DB_PASSWORD"] == "[REDACTED]"


def test_custom_patterns():
    env = {"MY_SECRET": "val", "CUSTOM_HIDDEN": "val2", "SAFE": "ok"}
    config = build_mask_config(patterns=["*HIDDEN*"])
    result = mask_env(env, config=config)
    assert result.masked["CUSTOM_HIDDEN"] == MASK_PLACEHOLDER
    assert result.masked["MY_SECRET"] == "val"  # not in custom patterns
    assert result.masked["SAFE"] == "ok"


def test_empty_env():
    result = mask_env({})
    assert result.masked == {}
    assert result.masked_keys == []
    assert result.has_masked is False
