"""Type-casting utilities for .env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


@dataclass
class CastResult:
    casted: Dict[str, Any] = field(default_factory=dict)
    failures: Dict[str, str] = field(default_factory=dict)

    def has_failures(self) -> bool:
        return bool(self.failures)

    def summary(self) -> str:
        ok = len(self.casted)
        fail = len(self.failures)
        return f"{ok} key(s) cast successfully, {fail} failure(s)"


def _cast_value(raw: str, target: str) -> Any:
    """Attempt to cast *raw* to *target* type name."""
    t = target.lower()
    if t == "int":
        return int(raw)
    if t == "float":
        return float(raw)
    if t == "bool":
        low = raw.lower()
        if low in _BOOL_TRUE:
            return True
        if low in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot cast {raw!r} to bool")
    if t == "str":
        return raw
    raise ValueError(f"Unknown target type: {target!r}")


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, str],
) -> CastResult:
    """Cast values in *env* according to *schema* (key -> type name).

    Keys not present in *schema* are kept as-is (str).
    """
    result = CastResult()
    for key, raw in env.items():
        target = schema.get(key, "str")
        try:
            result.casted[key] = _cast_value(raw, target)
        except (ValueError, TypeError) as exc:
            result.failures[key] = str(exc)
    return result


def cast_keys(env: Dict[str, str], keys: List[str], target: str) -> CastResult:
    """Cast a specific list of *keys* in *env* to *target* type."""
    schema = {k: target for k in keys}
    return cast_env(env, schema)
