"""Tests for envdiff.caster."""
import pytest
from envdiff.caster import cast_env, cast_keys, CastResult, _cast_value


# --- _cast_value unit tests ---

def test_cast_int_valid():
    assert _cast_value("42", "int") == 42


def test_cast_float_valid():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_bool_true_variants():
    for raw in ("true", "True", "yes", "1", "on"):
        assert _cast_value(raw, "bool") is True


def test_cast_bool_false_variants():
    for raw in ("false", "False", "no", "0", "off"):
        assert _cast_value(raw, "bool") is False


def test_cast_bool_invalid_raises():
    with pytest.raises(ValueError, match="Cannot cast"):
        _cast_value("maybe", "bool")


def test_cast_str_passthrough():
    assert _cast_value("hello", "str") == "hello"


def test_cast_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown target type"):
        _cast_value("x", "list")


# --- cast_env ---

def test_cast_env_basic():
    env = {"PORT": "8080", "DEBUG": "true", "RATIO": "0.5"}
    schema = {"PORT": "int", "DEBUG": "bool", "RATIO": "float"}
    result = cast_env(env, schema)
    assert result.casted["PORT"] == 8080
    assert result.casted["DEBUG"] is True
    assert result.casted["RATIO"] == pytest.approx(0.5)
    assert not result.has_failures()


def test_cast_env_key_not_in_schema_stays_str():
    env = {"NAME": "alice"}
    result = cast_env(env, {})
    assert result.casted["NAME"] == "alice"


def test_cast_env_failure_recorded():
    env = {"PORT": "not_a_number"}
    schema = {"PORT": "int"}
    result = cast_env(env, schema)
    assert "PORT" in result.failures
    assert result.has_failures()


def test_cast_env_partial_failure():
    env = {"A": "1", "B": "bad"}
    schema = {"A": "int", "B": "int"}
    result = cast_env(env, schema)
    assert result.casted["A"] == 1
    assert "B" in result.failures


def test_cast_env_summary_message():
    env = {"X": "1", "Y": "oops"}
    schema = {"X": "int", "Y": "float"}
    result = cast_env(env, schema)
    s = result.summary()
    assert "1 key(s)" in s
    assert "1 failure" in s


# --- cast_keys ---

def test_cast_keys_converts_subset():
    env = {"A": "10", "B": "20", "C": "hello"}
    result = cast_keys(env, ["A", "B"], "int")
    assert result.casted["A"] == 10
    assert result.casted["B"] == 20
    assert result.casted["C"] == "hello"


def test_cast_keys_failure_in_subset():
    env = {"A": "10", "B": "nope"}
    result = cast_keys(env, ["A", "B"], "int")
    assert result.casted["A"] == 10
    assert "B" in result.failures
