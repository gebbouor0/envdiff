"""Tests for envdiff.transformer."""

import pytest

from envdiff.transformer import (
    TransformRule,
    TransformResult,
    get_builtin_rule,
    transform_env,
)


@pytest.fixture
def sample_env() -> dict:
    return {
        "db_host": "  localhost  ",
        "db_port": "5432",
        "api_key": "secret",
    }


def test_uppercase_keys_builtin(sample_env):
    rule = get_builtin_rule("uppercase_keys")
    result = transform_env(sample_env, [rule])
    assert "DB_HOST" in result.transformed
    assert "db_host" not in result.transformed
    assert result.has_changes()


def test_strip_values_builtin(sample_env):
    rule = get_builtin_rule("strip_values")
    result = transform_env(sample_env, [rule])
    assert result.transformed["db_host"] == "localhost"
    assert result.has_changes()


def test_lowercase_values_builtin(sample_env):
    rule = get_builtin_rule("lowercase_values")
    env = {"KEY": "HELLO"}
    result = transform_env(env, [rule])
    assert result.transformed["KEY"] == "hello"


def test_uppercase_values_builtin():
    rule = get_builtin_rule("uppercase_values")
    env = {"mode": "production"}
    result = transform_env(env, [rule])
    assert result.transformed["mode"] == "PRODUCTION"


def test_multiple_rules_applied_in_order(sample_env):
    rules = [
        get_builtin_rule("uppercase_keys"),
        get_builtin_rule("strip_values"),
    ]
    result = transform_env(sample_env, rules)
    assert "DB_HOST" in result.transformed
    assert result.transformed["DB_HOST"] == "localhost"
    assert len(result.applied) == 2


def test_no_change_when_already_upper():
    env = {"KEY": "val"}
    rule = get_builtin_rule("uppercase_keys")
    result = transform_env(env, [rule])
    # KEY is already uppercase — no change recorded
    assert "uppercase_keys" not in result.applied
    assert not result.has_changes()


def test_empty_env_no_changes():
    result = transform_env({}, [get_builtin_rule("uppercase_keys")])
    assert result.transformed == {}
    assert not result.has_changes()


def test_custom_rule():
    custom = TransformRule(
        name="prefix_keys",
        fn=lambda k, v: (f"APP_{k}", v),
    )
    result = transform_env({"name": "envdiff"}, [custom])
    assert "APP_name" in result.transformed
    assert result.applied == ["prefix_keys"]


def test_summary_with_changes(sample_env):
    result = transform_env(sample_env, [get_builtin_rule("uppercase_keys")])
    assert "uppercase_keys" in result.summary()


def test_summary_no_changes():
    env = {"KEY": "val"}
    result = transform_env(env, [get_builtin_rule("uppercase_keys")])
    assert result.summary() == "No transformations applied."


def test_as_dict_structure(sample_env):
    result = transform_env(sample_env, [get_builtin_rule("strip_values")])
    d = result.as_dict()
    assert "original" in d
    assert "transformed" in d
    assert "applied" in d
    assert isinstance(d["has_changes"], bool)


def test_get_builtin_rule_unknown_returns_none():
    assert get_builtin_rule("nonexistent") is None
