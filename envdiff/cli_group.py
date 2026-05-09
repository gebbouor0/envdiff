"""CLI integration for the grouper feature."""

from __future__ import annotations

import argparse
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.grouper import GroupResult, group_result
from envdiff.reporter import format_report


def add_group_args(parser: argparse.ArgumentParser) -> None:
    """Register --group and --group-sep flags onto an existing parser."""
    parser.add_argument(
        "--group",
        action="store_true",
        default=False,
        help="Group diff output by key prefix.",
    )
    parser.add_argument(
        "--group-sep",
        default="_",
        metavar="SEP",
        help="Separator used to detect key prefixes (default: '_').",
    )


def handle_group(
    args: argparse.Namespace,
    result: DiffResult,
) -> bool:
    """Print grouped report if --group was requested.

    Returns True if grouping was handled, False otherwise.
    """
    if not getattr(args, "group", False):
        return False

    sep = getattr(args, "group_sep", "_")
    gr: GroupResult = group_result(result, separator=sep)

    if not gr.groups:
        print("No groups found — all keys share no common prefix.")
        return True

    for name in gr.group_names:
        print(f"\n=== Group: {name} ===")
        print(format_report(gr.groups[name]))

    return True
