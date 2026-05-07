"""Unified diff-style output for .env file comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult


@dataclass
class UnifiedDiffLine:
    tag: str  # '+', '-', ' ', or '!'
    key: str
    value: str | None = None

    def __str__(self) -> str:
        prefix = self.tag
        if self.value is not None:
            return f"{prefix} {self.key}={self.value}"
        return f"{prefix} {self.key}"


def build_unified_diff(
    result: DiffResult,
    left_label: str = "left",
    right_label: str = "right",
) -> List[str]:
    """Return a list of lines representing a unified diff of two env sets."""
    lines: List[str] = []
    lines.append(f"--- {left_label}")
    lines.append(f"+++ {right_label}")

    all_keys: List[str] = sorted(
        set(result.missing_in_right)
        | set(result.missing_in_left)
        | set(result.mismatched.keys())
    )

    for key in all_keys:
        if key in result.missing_in_right:
            lines.append(str(UnifiedDiffLine("-", key, result.missing_in_right[key])))
        elif key in result.missing_in_left:
            lines.append(str(UnifiedDiffLine("+", key, result.missing_in_left[key])))
        elif key in result.mismatched:
            left_val, right_val = result.mismatched[key]
            lines.append(str(UnifiedDiffLine("-", key, left_val)))
            lines.append(str(UnifiedDiffLine("+", key, right_val)))

    return lines


def format_unified_diff(
    result: DiffResult,
    left_label: str = "left",
    right_label: str = "right",
) -> str:
    """Return the unified diff as a single formatted string."""
    return "\n".join(build_unified_diff(result, left_label, right_label))


def print_unified_diff(
    result: DiffResult,
    left_label: str = "left",
    right_label: str = "right",
) -> None:
    """Print the unified diff to stdout."""
    print(format_unified_diff(result, left_label, right_label))
