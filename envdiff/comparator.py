"""Compare two parsed .env dicts and return structured differences."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DiffResult:
    """Holds the result of comparing two env files."""

    left_name: str = "left"
    right_name: str = "right"
    missing_in_right: List[str] = field(default_factory=list)
    missing_in_left: List[str] = field(default_factory=list)
    mismatched_values: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    # internal: total unique keys seen across both sides
    _total_keys: int = field(default=0, repr=False, compare=False)

    def has_differences(self) -> bool:
        return bool(
            self.missing_in_right or self.missing_in_left or self.mismatched_values
        )

    def summary(self) -> str:
        parts = []
        if self.missing_in_right:
            parts.append(
                f"{len(self.missing_in_right)} key(s) missing in {self.right_name}"
            )
        if self.missing_in_left:
            parts.append(
                f"{len(self.missing_in_left)} key(s) missing in {self.left_name}"
            )
        if self.mismatched_values:
            parts.append(f"{len(self.mismatched_values)} value mismatch(es)")
        return ", ".join(parts) if parts else "No differences found."


def compare(
    left: Dict[str, str],
    right: Dict[str, str],
    left_name: str = "left",
    right_name: str = "right",
) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    left_keys = set(left)
    right_keys = set(right)
    all_keys = left_keys | right_keys

    missing_in_right = sorted(left_keys - right_keys)
    missing_in_left = sorted(right_keys - left_keys)
    mismatched: Dict[str, Tuple[str, str]] = {}

    for key in sorted(left_keys & right_keys):
        if left[key] != right[key]:
            mismatched[key] = (left[key], right[key])

    result = DiffResult(
        left_name=left_name,
        right_name=right_name,
        missing_in_right=missing_in_right,
        missing_in_left=missing_in_left,
        mismatched_values=mismatched,
    )
    result._total_keys = len(all_keys)
    return result
