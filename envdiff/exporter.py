"""Export diff results to various output formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.comparator import DiffResult

OutputFormat = Literal["json", "csv", "markdown"]


def to_json(result: DiffResult, indent: int = 2) -> str:
    """Serialize a DiffResult to a JSON string."""
    data = {
        "missing_in_right": sorted(result.missing_in_right),
        "missing_in_left": sorted(result.missing_in_left),
        "mismatched": {
            k: {"left": lv, "right": rv}
            for k, (lv, rv) in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=indent)


def to_csv(result: DiffResult) -> str:
    """Serialize a DiffResult to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["type", "key", "left_value", "right_value"])

    for key in sorted(result.missing_in_right):
        writer.writerow(["missing_in_right", key, "", ""])

    for key in sorted(result.missing_in_left):
        writer.writerow(["missing_in_left", key, "", ""])

    for key, (lv, rv) in sorted(result.mismatched.items()):
        writer.writerow(["mismatched", key, lv, rv])

    return buf.getvalue()


def to_markdown(result: DiffResult) -> str:
    """Serialize a DiffResult to a Markdown table string."""
    lines: list[str] = []
    lines.append("| Type | Key | Left Value | Right Value |")
    lines.append("|------|-----|------------|-------------|")

    for key in sorted(result.missing_in_right):
        lines.append(f"| missing_in_right | `{key}` | — | — |")

    for key in sorted(result.missing_in_left):
        lines.append(f"| missing_in_left | `{key}` | — | — |")

    for key, (lv, rv) in sorted(result.mismatched.items()):
        lines.append(f"| mismatched | `{key}` | {lv} | {rv} |")

    if len(lines) == 2:
        lines.append("| ✅ No differences | — | — | — |")

    return "\n".join(lines)


def export(result: DiffResult, fmt: OutputFormat) -> str:
    """Export a DiffResult in the requested format."""
    if fmt == "json":
        return to_json(result)
    if fmt == "csv":
        return to_csv(result)
    if fmt == "markdown":
        return to_markdown(result)
    raise ValueError(f"Unsupported format: {fmt!r}")
