"""Tests for envdiff.validator."""

import pytest

from envdiff.validator import ValidationResult, validate


@pytest.fixture()
def sample_env():
    return {
        "APP_ENV": "production",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "s3cr3t",
    }


def test_valid_with_no_constraints(sample_env):
    result = validate(sample_env)
    assert result.is_valid
    assert result.summary() == "All keys are valid."


def test_missing_required_keys(sample_env):
    result = validate(sample_env, required_keys=["APP_ENV", "MISSING_KEY"])
    assert not result.is_valid
    assert "MISSING_KEY" in result.missing_required
    assert "APP_ENV" not in result.missing_required


def test_all_required_keys_present(sample_env):
    result = validate(sample_env, required_keys=["APP_ENV", "DB_HOST"])
    assert result.is_valid
    assert result.missing_required == []


def test_unexpected_keys_flagged(sample_env):
    allowed = ["APP_ENV", "DB_HOST"]
    result = validate(sample_env, allowed_keys=allowed)
    assert not result.is_valid
    assert "DB_PORT" in result.unexpected_keys
    assert "SECRET_KEY" in result.unexpected_keys
    assert "APP_ENV" not in result.unexpected_keys


def test_allowed_keys_all_present(sample_env):
    allowed = list(sample_env.keys())
    result = validate(sample_env, allowed_keys=allowed)
    assert result.is_valid
    assert result.unexpected_keys == []


def test_rule_passes(sample_env):
    rules = {"DB_PORT": lambda v: v.isdigit()}
    result = validate(sample_env, rules=rules)
    assert result.is_valid
    assert result.invalid_values == {}


def test_rule_fails(sample_env):
    rules = {"APP_ENV": lambda v: v in ("development", "staging")}
    result = validate(sample_env, rules=rules)
    assert not result.is_valid
    assert "APP_ENV" in result.invalid_values


def test_rule_exception_recorded(sample_env):
    def boom(v):
        raise ValueError("not allowed")

    result = validate(sample_env, rules={"DB_HOST": boom})
    assert not result.is_valid
    assert "DB_HOST" in result.invalid_values
    assert "not allowed" in result.invalid_values["DB_HOST"]


def test_summary_lists_issues():
    r = ValidationResult(
        missing_required=["A"],
        unexpected_keys=["B", "C"],
        invalid_values={"D": "bad"},
    )
    s = r.summary()
    assert "1 missing" in s
    assert "2 unexpected" in s
    assert "1 invalid" in s


def test_combined_constraints(sample_env):
    result = validate(
        sample_env,
        required_keys=["APP_ENV", "REDIS_URL"],
        allowed_keys=["APP_ENV", "DB_HOST", "DB_PORT", "SECRET_KEY"],
        rules={"DB_PORT": str.isdigit},
    )
    assert "REDIS_URL" in result.missing_required
    assert result.unexpected_keys == []
    assert result.invalid_values == {}
