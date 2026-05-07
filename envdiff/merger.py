"""Merge multiple .env files into a single resolved dict.

Later files take precedence over earlier ones (last-write-wins),
with optional reporting of which keys were overridden.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class MergeResult:
    """Result of merging two or more .env files."""

    merged: Dict[str, str] = field(default_factory=dict)
    # key -> list of (source_path, value) in the order they were seen
    overrides: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    @property
    def overridden_keys(self) -> List[str]:
        """Keys that appeared in more than one source file."""
        return [k for k, v in self.overrides.items() if len(v) > 1]

    def summary(self) -> str:
        overridden = self.overridden_keys
        lines = [
            f"Merged keys   : {len(self.merged)}",
            f"Overridden keys: {len(overridden)}",
        ]
        if overridden:
            lines.append("Keys overridden: " + ", ".join(sorted(overridden)))
        return "\n".join(lines)


def merge_env_files(*paths: str) -> MergeResult:
    """Merge env files in order; later files override earlier ones.

    Args:
        *paths: One or more paths to .env files.

    Returns:
        A MergeResult containing the final merged dict and override history.

    Raises:
        ValueError: If fewer than one path is supplied.
    """
    if not paths:
        raise ValueError("At least one env file path is required.")

    result = MergeResult()

    for path in paths:
        env = parse_env_file(path)
        for key, value in env.items():
            if key not in result.overrides:
                result.overrides[key] = []
            result.overrides[key].append((path, value))
            result.merged[key] = value

    return result
