"""Patch a .env file by applying changes from a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class PatchResult:
    """Outcome of patching a .env file."""

    applied: Dict[str, str] = field(default_factory=dict)
    """Keys that were added or updated."""

    skipped: List[str] = field(default_factory=list)
    """Keys skipped because *keep_existing* was True and key already existed."""

    @property
    def has_changes(self) -> bool:
        return bool(self.applied)

    def summary(self) -> str:
        parts = [f"{len(self.applied)} applied"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        return ", ".join(parts)


def build_patch(diff: DiffResult, direction: str = "left_to_right") -> Dict[str, str]:
    """Build a flat key→value patch dict from *diff*.

    direction:
      - ``left_to_right``: fill keys missing in the right env from the left.
      - ``right_to_left``: fill keys missing in the left env from the right.
    """
    if direction == "left_to_right":
        patch: Dict[str, str] = dict(diff.missing_in_right)
        for key, (left_val, _right_val) in diff.mismatched.items():
            patch[key] = left_val
    elif direction == "right_to_left":
        patch = dict(diff.missing_in_left)
        for key, (_left_val, right_val) in diff.mismatched.items():
            patch[key] = right_val
    else:
        raise ValueError(f"Unknown direction: {direction!r}")
    return patch


def apply_patch(
    env: Dict[str, str],
    patch: Dict[str, str],
    keep_existing: bool = False,
) -> PatchResult:
    """Apply *patch* to *env* in-place and return a :class:`PatchResult`."""
    result = PatchResult()
    for key, value in patch.items():
        if keep_existing and key in env:
            result.skipped.append(key)
        else:
            env[key] = value
            result.applied[key] = value
    return result


def write_patched_env(
    env: Dict[str, str],
    path: Path,
    header: Optional[str] = None,
) -> None:
    """Write *env* dict to *path* in KEY=VALUE format."""
    lines: List[str] = []
    if header:
        for line in header.splitlines():
            lines.append(f"# {line}\n")
        lines.append("\n")
    for key, value in env.items():
        if " " in value or "\t" in value or value == "":
            lines.append(f'{key}="{value}"\n')
        else:
            lines.append(f"{key}={value}\n")
    Path(path).write_text("".join(lines))
