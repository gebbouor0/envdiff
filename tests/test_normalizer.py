import pytest
from envdiff.normalizer import (
    NormalizeConfig,
    NormalizeResult,
    normalize,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _cfg(**kwargs) -> NormalizeConfig:
    return NormalizeConfig(**kwargs)


# ---------------------------------------------------------------------------
# key normalisation
# ---------------------------------------------------------------------------

def test_uppercase_keys_by_default():
    result = normalize({"db_host": "localhost"})
    assert "DB_HOST" in result.normalized
    assert result.changed_keys == {"db_host": "DB_HOST"}


def test_uppercase_keys_disabled():
    result = normalize({"db_host": "localhost"}, _cfg(uppercase_keys=False))
    assert "db_host" in result.normalized
    assert result.changed_keys == {}


def test_key_with_leading_spaces_stripped():
    result = normalize({"  KEY": "val"})
    assert "KEY" in result.normalized
    assert "  KEY" not in result.normalized


# ---------------------------------------------------------------------------
# value normalisation
# ---------------------------------------------------------------------------

def test_strip_values_by_default():
    result = normalize({"KEY": "  hello  "})
    assert result.normalized["KEY"] == "hello"
    assert result.changed_values["KEY"] == ("  hello  ", "hello")


def test_strip_values_disabled():
    result = normalize({"KEY": "  hello  "}, _cfg(strip_values=False))
    assert result.normalized["KEY"] == "  hello  "
    assert result.changed_values == {}


def test_normalize_bool_true_aliases():
    cfg = _cfg(normalize_bools=True)
    for alias in ("yes", "1", "on", "true", "YES", "True"):
        result = normalize({"FLAG": alias}, cfg)
        assert result.normalized["FLAG"] == "true", alias


def test_normalize_bool_false_aliases():
    cfg = _cfg(normalize_bools=True)
    for alias in ("no", "0", "off", "false", "NO", "False"):
        result = normalize({"FLAG": alias}, cfg)
        assert result.normalized["FLAG"] == "false", alias


def test_normalize_bools_disabled_by_default():
    result = normalize({"FLAG": "yes"})
    assert result.normalized["FLAG"] == "yes"


def test_custom_bool_canonical():
    cfg = _cfg(normalize_bools=True, bool_true_canonical="TRUE", bool_false_canonical="FALSE")
    result = normalize({"A": "yes", "B": "no"}, cfg)
    assert result.normalized["A"] == "TRUE"
    assert result.normalized["B"] == "FALSE"


# ---------------------------------------------------------------------------
# has_changes / summary
# ---------------------------------------------------------------------------

def test_has_changes_false_when_already_normalised():
    result = normalize({"KEY": "value"})
    assert not result.has_changes()


def test_has_changes_true_when_key_renamed():
    result = normalize({"key": "value"})
    assert result.has_changes()


def test_summary_no_changes():
    result = normalize({"KEY": "value"})
    assert result.summary() == "no changes"


def test_summary_with_key_and_value_changes():
    result = normalize({"key": "  val  "})
    s = result.summary()
    assert "key" in s
    assert "value" in s


# ---------------------------------------------------------------------------
# original preserved
# ---------------------------------------------------------------------------

def test_original_dict_unchanged():
    env = {"db_pass": "  secret  "}
    result = normalize(env)
    assert result.original == {"db_pass": "  secret  "}
    assert result.normalized == {"DB_PASS": "secret"}
