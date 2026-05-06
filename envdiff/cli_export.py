"""CLI helpers for the --export flag added to envdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.exporter import OutputFormat, export

_FORMATS: tuple[str, ...] = ("json", "csv", "markdown")


def add_export_args(parser: argparse.ArgumentParser) -> None:
    """Attach export-related arguments to an existing ArgumentParser."""
    parser.add_argument(
        "--export-format",
        choices=_FORMATS,
        default=None,
        metavar="FORMAT",
        help="Export diff result as json, csv, or markdown.",
    )
    parser.add_argument(
        "--export-output",
        default=None,
        metavar="FILE",
        help="Write exported result to FILE instead of stdout.",
    )


def handle_export(
    result: DiffResult,
    fmt: Optional[str],
    output_path: Optional[str],
) -> None:
    """Run export if a format was requested.

    Writes to *output_path* when provided, otherwise to stdout.
    Silently does nothing when *fmt* is None.
    """
    if fmt is None:
        return

    if fmt not in _FORMATS:
        print(f"envdiff: unknown export format '{fmt}'", file=sys.stderr)
        sys.exit(2)

    content = export(result, fmt)  # type: ignore[arg-type]

    if output_path:
        path = Path(output_path)
        path.write_text(content, encoding="utf-8")
    else:
        print(content)
