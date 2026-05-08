"""Generate .env template files from diff results or parsed env dicts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class TemplateResult:
    """Holds the rendered lines of a generated .env template."""

    lines: List[str] = field(default_factory=list)

    def render(self) -> str:
        """Return the full template as a string."""
        return "\n".join(self.lines)

    def write(self, path: str) -> None:
        """Write the template to *path*."""
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render())
            fh.write("\n")


def _placeholder(key: str, default: Optional[str] = None) -> str:
    """Return a placeholder value for *key*."""
    if default is not None:
        return default
    return f"<{key.lower()}>"


def from_dict(
    env: Dict[str, str],
    *,
    redact_keys: Optional[List[str]] = None,
    placeholder: Optional[str] = None,
) -> TemplateResult:
    """Build a template from a plain env dict.

    Keys whose names contain any substring in *redact_keys* will have their
    values replaced with a placeholder.
    """
    redact_keys = redact_keys or []
    lines: List[str] = []
    for key, value in sorted(env.items()):
        sensitive = any(r.lower() in key.lower() for r in redact_keys)
        display = _placeholder(key, placeholder) if sensitive else value
        lines.append(f"{key}={display}")
    return TemplateResult(lines=lines)


def from_diff(
    result: DiffResult,
    *,
    include_mismatched: bool = True,
    placeholder: Optional[str] = None,
) -> TemplateResult:
    """Build a template that covers all keys seen across both env files.

    - Keys only in the left file or only in the right file get a placeholder.
    - Mismatched keys use the left-side value unless *placeholder* is set.
    """
    lines: List[str] = []
    seen = set()

    for key in sorted(result.missing_in_right):
        lines.append(f"{key}={_placeholder(key, placeholder)}")
        seen.add(key)

    for key in sorted(result.missing_in_left):
        lines.append(f"{key}={_placeholder(key, placeholder)}")
        seen.add(key)

    if include_mismatched:
        for key, (left_val, _right_val) in sorted(result.mismatched.items()):
            display = placeholder if placeholder is not None else left_val
            lines.append(f"{key}={display}")
            seen.add(key)

    return TemplateResult(lines=sorted(lines))
