"""CLI integration for the flattener feature."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from envdiff.flattener import flatten_env

if TYPE_CHECKING:
    from envdiff.comparator import DiffResult


def add_flatten_args(parser: argparse.ArgumentParser) -> None:
    """Register --flatten flags onto an existing argument parser."""
    parser.add_argument(
        "--flatten",
        action="store_true",
        default=False,
        help="Group keys by prefix and display flattened structure.",
    )
    parser.add_argument(
        "--flatten-sep",
        default="_",
        metavar="SEP",
        help="Separator used to split key prefixes (default: '_').",
    )
    parser.add_argument(
        "--flatten-prefix",
        default=None,
        metavar="PREFIX",
        help="Only show keys belonging to this prefix group.",
    )


def handle_flatten(
    args: argparse.Namespace,
    result: "DiffResult",
) -> bool:
    """Handle --flatten output if requested.

    Returns True if flatten output was produced, False otherwise.
    """
    if not args.flatten:
        return False

    # Collect all unique keys across both sides
    all_keys = (
        set(result.missing_in_right)
        | set(result.missing_in_left)
        | set(result.mismatched.keys())
    )
    combined: dict[str, str] = {k: "" for k in all_keys}

    flat = flatten_env(
        combined,
        separator=args.flatten_sep,
        prefix_filter=args.flatten_prefix,
    )

    print(f"Flatten summary: {flat.summary()}")
    for group in flat.group_names():
        keys = sorted(flat.get(group).keys())
        print(f"  [{group}] ({len(keys)} key(s))")
        for k in keys:
            print(f"    {k}")

    return True
