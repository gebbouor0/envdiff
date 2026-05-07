"""Key ignore/allowlist filtering for diff results."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Iterable

from envdiff.comparator import DiffResult


@dataclass
class IgnoreConfig:
    """Configuration for ignoring keys during comparison."""

    patterns: list[str] = field(default_factory=list)
    """Shell-style wildcard patterns (e.g. 'SECRET_*', 'DB_*')."""

    exact_keys: set[str] = field(default_factory=set)
    """Exact key names to ignore."""


def _matches_any(key: str, patterns: Iterable[str]) -> bool:
    """Return True if *key* matches any of the given fnmatch patterns."""
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def should_ignore(key: str, config: IgnoreConfig) -> bool:
    """Return True if *key* should be excluded from the diff result."""
    if key in config.exact_keys:
        return True
    return _matches_any(key, config.patterns)


def apply_ignore(result: DiffResult, config: IgnoreConfig) -> DiffResult:
    """Return a new DiffResult with ignored keys removed from all sections.

    Args:
        result: The original diff result.
        config: Rules describing which keys to ignore.

    Returns:
        A filtered DiffResult instance.
    """
    ignore = lambda k: should_ignore(k, config)  # noqa: E731

    return DiffResult(
        missing_in_right={k: v for k, v in result.missing_in_right.items() if not ignore(k)},
        missing_in_left={k: v for k, v in result.missing_in_left.items() if not ignore(k)},
        mismatched={k: v for k, v in result.mismatched.items() if not ignore(k)},
        common_keys={k for k in result.common_keys if not ignore(k)},
    )


def build_ignore_config(
    patterns: Iterable[str] | None = None,
    exact_keys: Iterable[str] | None = None,
) -> IgnoreConfig:
    """Convenience constructor for IgnoreConfig."""
    return IgnoreConfig(
        patterns=list(patterns or []),
        exact_keys=set(exact_keys or []),
    )
