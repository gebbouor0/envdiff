"""Profile .env files to detect common issues like empty values, duplicate keys, and suspicious patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileResult:
    empty_values: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    suspicious_keys: List[str] = field(default_factory=list)  # e.g. keys with spaces or special chars
    total_keys: int = 0

    @property
    def has_issues(self) -> bool:
        return bool(self.empty_values or self.duplicate_keys or self.suspicious_keys)

    def summary(self) -> str:
        if not self.has_issues:
            return f"No issues found in {self.total_keys} key(s)."
        parts = []
        if self.empty_values:
            parts.append(f"{len(self.empty_values)} empty value(s)")
        if self.duplicate_keys:
            parts.append(f"{len(self.duplicate_keys)} duplicate key(s)")
        if self.suspicious_keys:
            parts.append(f"{len(self.suspicious_keys)} suspicious key(s)")
        return f"Issues found: {', '.join(parts)} (total keys: {self.total_keys})."


_SUSPICIOUS_PATTERN_CHARS = set(" \t!@#$%^&*(){}[]|\\<>?")


def _is_suspicious(key: str) -> bool:
    return any(c in _SUSPICIOUS_PATTERN_CHARS for c in key)


def profile(env_vars: Dict[str, str]) -> ProfileResult:
    """Analyse a parsed env dict and return a ProfileResult."""
    seen: Dict[str, int] = {}
    empty_values: List[str] = []
    suspicious_keys: List[str] = []

    for key, value in env_vars.items():
        seen[key] = seen.get(key, 0) + 1
        if value == "":
            empty_values.append(key)
        if _is_suspicious(key):
            suspicious_keys.append(key)

    duplicate_keys = [k for k, count in seen.items() if count > 1]

    return ProfileResult(
        empty_values=empty_values,
        duplicate_keys=duplicate_keys,
        suspicious_keys=suspicious_keys,
        total_keys=len(env_vars),
    )


def profile_file(path: str) -> ProfileResult:
    """Parse an env file and return a ProfileResult."""
    from envdiff.parser import parse_env_file

    env_vars = parse_env_file(path)
    return profile(env_vars)


def format_profile(result: ProfileResult, filename: str = "") -> str:
    """Return a human-readable report string for a ProfileResult."""
    label = f" [{filename}]" if filename else ""
    lines = [f"Profile Report{label}", "-" * 40]
    lines.append(f"Total keys : {result.total_keys}")
    lines.append(f"Empty values ({len(result.empty_values)}): {', '.join(result.empty_values) or 'none'}")
    lines.append(f"Duplicate keys ({len(result.duplicate_keys)}): {', '.join(result.duplicate_keys) or 'none'}")
    lines.append(f"Suspicious keys ({len(result.suspicious_keys)}): {', '.join(result.suspicious_keys) or 'none'}")
    return "\n".join(lines)
