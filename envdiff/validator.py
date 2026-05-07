"""Validate .env file keys against a schema or required key list."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    unexpected_keys: List[str] = field(default_factory=list)
    invalid_values: Dict[str, str] = field(default_factory=dict)  # key -> reason

    @property
    def is_valid(self) -> bool:
        return (
            not self.missing_required
            and not self.unexpected_keys
            and not self.invalid_values
        )

    def summary(self) -> str:
        if self.is_valid:
            return "All keys are valid."
        parts = []
        if self.missing_required:
            parts.append(f"{len(self.missing_required)} missing required key(s)")
        if self.unexpected_keys:
            parts.append(f"{len(self.unexpected_keys)} unexpected key(s)")
        if self.invalid_values:
            parts.append(f"{len(self.invalid_values)} invalid value(s)")
        return "; ".join(parts) + "."

    def details(self) -> List[str]:
        """Return a list of human-readable detail lines describing all issues."""
        lines = []
        for key in self.missing_required:
            lines.append(f"Missing required key: {key!r}")
        for key in self.unexpected_keys:
            lines.append(f"Unexpected key: {key!r}")
        for key, reason in self.invalid_values.items():
            lines.append(f"Invalid value for {key!r}: {reason}")
        return lines


def validate(
    env: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    allowed_keys: Optional[List[str]] = None,
    rules: Optional[Dict[str, Callable]] = None,
) -> ValidationResult:
    """Validate an env dict against optional constraints.

    Args:
        env: Parsed env key/value pairs.
        required_keys: Keys that must be present.
        allowed_keys: If provided, keys outside this set are flagged.
        rules: Mapping of key -> predicate(value) -> bool. Failures are recorded.
    """
    result = ValidationResult()

    if required_keys:
        for key in required_keys:
            if key not in env:
                result.missing_required.append(key)

    if allowed_keys:
        allowed: Set[str] = set(allowed_keys)
        for key in env:
            if key not in allowed:
                result.unexpected_keys.append(key)

    if rules:
        for key, predicate in rules.items():
            if key in env:
                try:
                    ok = predicate(env[key])
                except Exception as exc:  # noqa: BLE001
                    ok = False
                    result.invalid_values[key] = str(exc)
                    continue
                if not ok:
                    result.invalid_values[key] = f"value {env[key]!r} failed validation"

    return result
