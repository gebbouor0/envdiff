"""Flatten nested or prefixed env keys into a structured dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    """Result of flattening an env dict by prefix groups."""
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    separator: str = "_"

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def get(self, group: str) -> Dict[str, str]:
        return self.groups.get(group, {})

    def has_group(self, group: str) -> bool:
        return group in self.groups

    def summary(self) -> str:
        total = sum(len(v) for v in self.groups.values())
        return (
            f"{len(self.groups)} group(s), {total} key(s) total"
        )

    def as_dict(self) -> Dict[str, Dict[str, str]]:
        return dict(self.groups)


def _prefix(key: str, separator: str) -> str:
    """Return the prefix portion of a key, or 'OTHER' if none."""
    if separator in key:
        return key.split(separator, 1)[0].upper()
    return "OTHER"


def flatten_env(
    env: Dict[str, str],
    separator: str = "_",
    prefix_filter: Optional[str] = None,
) -> FlattenResult:
    """Group env keys by their prefix.

    Args:
        env: Raw key/value dict from a parsed .env file.
        separator: Character used to split prefix from the rest of the key.
        prefix_filter: If given, only include keys whose prefix matches.

    Returns:
        FlattenResult with keys grouped by prefix.
    """
    groups: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        group = _prefix(key, separator)
        if prefix_filter is not None and group != prefix_filter.upper():
            continue
        groups.setdefault(group, {})[key] = value
    return FlattenResult(groups=groups, separator=separator)
