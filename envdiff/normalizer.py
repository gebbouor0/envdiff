"""Normalize .env key/value pairs across environments.

Provides utilities to canonicalize keys (e.g. strip whitespace, uppercase)
and values (e.g. trim trailing spaces, unify boolean representations)
before comparison or export.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


BOOL_TRUE_ALIASES = {"true", "yes", "1", "on"}
BOOL_FALSE_ALIASES = {"false", "no", "0", "off"}


@dataclass
class NormalizeConfig:
    uppercase_keys: bool = True
    strip_values: bool = True
    normalize_bools: bool = False
    bool_true_canonical: str = "true"
    bool_false_canonical: str = "false"


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changed_keys: Dict[str, str] = field(default_factory=dict)   # old_key -> new_key
    changed_values: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    def has_changes(self) -> bool:
        return bool(self.changed_keys or self.changed_values)

    def summary(self) -> str:
        parts = []
        if self.changed_keys:
            parts.append(f"{len(self.changed_keys)} key(s) renamed")
        if self.changed_values:
            parts.append(f"{len(self.changed_values)} value(s) normalized")
        return ", ".join(parts) if parts else "no changes"


def _normalize_key(key: str, cfg: NormalizeConfig) -> str:
    key = key.strip()
    if cfg.uppercase_keys:
        key = key.upper()
    return key


def _normalize_value(value: str, cfg: NormalizeConfig) -> str:
    if cfg.strip_values:
        value = value.strip()
    if cfg.normalize_bools:
        lower = value.lower()
        if lower in BOOL_TRUE_ALIASES:
            return cfg.bool_true_canonical
        if lower in BOOL_FALSE_ALIASES:
            return cfg.bool_false_canonical
    return value


def normalize(env: Dict[str, str], cfg: Optional[NormalizeConfig] = None) -> NormalizeResult:
    """Return a NormalizeResult with canonicalized keys and values."""
    if cfg is None:
        cfg = NormalizeConfig()

    normalized: Dict[str, str] = {}
    changed_keys: Dict[str, str] = {}
    changed_values: Dict[str, tuple] = {}

    for raw_key, raw_value in env.items():
        new_key = _normalize_key(raw_key, cfg)
        new_value = _normalize_value(raw_value, cfg)

        if new_key != raw_key:
            changed_keys[raw_key] = new_key
        if new_value != raw_value:
            changed_values[new_key] = (raw_value, new_value)

        normalized[new_key] = new_value

    return NormalizeResult(
        original=dict(env),
        normalized=normalized,
        changed_keys=changed_keys,
        changed_values=changed_values,
    )
