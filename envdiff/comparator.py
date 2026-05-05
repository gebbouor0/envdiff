"""Compare parsed .env file dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the result of comparing two .env files."""

    left_name: str
    right_name: str
    missing_in_right: List[str] = field(default_factory=list)
    missing_in_left: List[str] = field(default_factory=list)
    mismatched: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_in_right or self.missing_in_left or self.mismatched)

    def summary(self) -> str:
        lines = [f"Comparing '{self.left_name}' vs '{self.right_name}':"]

        if not self.has_differences:
            lines.append("  No differences found.")
            return "\n".join(lines)

        for key in sorted(self.missing_in_right):
            lines.append(f"  - {key!r} only in '{self.left_name}'")

        for key in sorted(self.missing_in_left):
            lines.append(f"  + {key!r} only in '{self.right_name}'")

        for key in sorted(self.mismatched):
            left_val, right_val = self.mismatched[key]
            lines.append(
                f"  ~ {key!r}: '{self.left_name}'={left_val!r} | '{self.right_name}'={right_val!r}"
            )

        return "\n".join(lines)


def compare(
    left: Dict[str, Optional[str]],
    right: Dict[str, Optional[str]],
    left_name: str = "left",
    right_name: str = "right",
) -> DiffResult:
    """Compare two env dictionaries and return a DiffResult."""
    result = DiffResult(left_name=left_name, right_name=right_name)

    left_keys = set(left.keys())
    right_keys = set(right.keys())

    result.missing_in_right = sorted(left_keys - right_keys)
    result.missing_in_left = sorted(right_keys - left_keys)

    for key in left_keys & right_keys:
        if left[key] != right[key]:
            result.mismatched[key] = (left[key], right[key])

    return result
