"""Tests for envdiff.flattener."""
import pytest
from envdiff.flattener import FlattenResult, flatten_env, _prefix


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "AKID",
        "AWS_SECRET": "secret",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_prefix_with_separator():
    assert _prefix("DB_HOST", "_") == "DB"


def test_prefix_no_separator_returns_other():
    assert _prefix("DEBUG", "_") == "OTHER"


def test_flatten_creates_db_group(sample_env):
    result = flatten_env(sample_env)
    assert "DB" in result.group_names()
    assert result.get("DB") == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_flatten_creates_aws_group(sample_env):
    result = flatten_env(sample_env)
    assert "AWS" in result.group_names()
    assert result.get("AWS") == {"AWS_KEY": "AKID", "AWS_SECRET": "secret"}


def test_flatten_other_group_for_unprefixed(sample_env):
    result = flatten_env(sample_env)
    assert "OTHER" in result.group_names()
    assert "DEBUG" in result.get("OTHER")
    assert "PORT" in result.get("OTHER")


def test_group_names_sorted(sample_env):
    result = flatten_env(sample_env)
    names = result.group_names()
    assert names == sorted(names)


def test_has_group_true(sample_env):
    result = flatten_env(sample_env)
    assert result.has_group("DB")


def test_has_group_false(sample_env):
    result = flatten_env(sample_env)
    assert not result.has_group("REDIS")


def test_prefix_filter_limits_groups(sample_env):
    result = flatten_env(sample_env, prefix_filter="DB")
    assert result.group_names() == ["DB"]
    assert "AWS" not in result.groups
    assert "OTHER" not in result.groups


def test_prefix_filter_case_insensitive(sample_env):
    result = flatten_env(sample_env, prefix_filter="aws")
    assert "AWS" in result.group_names()
    assert len(result.group_names()) == 1


def test_summary_format(sample_env):
    result = flatten_env(sample_env)
    s = result.summary()
    assert "group" in s
    assert "key" in s


def test_as_dict_returns_plain_dict(sample_env):
    result = flatten_env(sample_env)
    d = result.as_dict()
    assert isinstance(d, dict)
    assert d["DB"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_empty_env_returns_empty_result():
    result = flatten_env({})
    assert result.group_names() == []
    assert result.summary() == "0 group(s), 0 key(s) total"


def test_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "DEBUG": "1"}
    result = flatten_env(env, separator=".")
    assert "DB" in result.group_names()
    assert result.get("DB") == {"DB.HOST": "localhost", "DB.PORT": "5432"}
