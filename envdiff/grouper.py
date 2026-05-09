"""Group diff results by key prefix (e.g. DB_, AWS_, APP_)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult


@dataclass
class GroupResult:
    """Holds keys bucketed by their prefix group."""

    groups: Dict[str, DiffResult] = field(default_factory=dict)
    separator: str = "_"

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def summary(self) -> str:
        lines = [f"{len(self.groups)} group(s) found:"]
        for name in self.group_names:
            r = self.groups[name]
            lines.append(
                f"  [{name}] missing_right={len(r.missing_in_right)}"
                f" missing_left={len(r.missing_in_left)}"
                f" mismatched={len(r.mismatched)}"
            )
        return "\n".join(lines)


def _prefix(key: str, separator: str) -> str:
    """Return the prefix before the first separator, or '__other__'."""
    idx = key.find(separator)
    if idx <= 0:
        return "__other__"
    return key[:idx].upper()


def _empty_diff() -> DiffResult:
    return DiffResult(
        missing_in_right=[],
        missing_in_left=[],
        mismatched=[],
    )


def group_result(result: DiffResult, separator: str = "_") -> GroupResult:
    """Split a DiffResult into per-prefix groups."""
    buckets: Dict[str, DiffResult] = {}

    def bucket(name: str) -> DiffResult:
        if name not in buckets:
            buckets[name] = _empty_diff()
        return buckets[name]

    for key in result.missing_in_right:
        bucket(_prefix(key, separator)).missing_in_right.append(key)

    for key in result.missing_in_left:
        bucket(_prefix(key, separator)).missing_in_left.append(key)

    for key, left_val, right_val in result.mismatched:
        bucket(_prefix(key, separator)).mismatched.append((key, left_val, right_val))

    return GroupResult(groups=buckets, separator=separator)
