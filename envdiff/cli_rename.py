"""CLI helpers for the rename feature."""

import argparse
import json
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.renamer import build_rename_config, rename_result


def add_rename_args(parser: argparse.ArgumentParser) -> None:
    """Add rename-related arguments to an argument parser."""
    parser.add_argument(
        "--rename",
        action="store_true",
        default=False,
        help="Apply key renames before comparing output.",
    )
    parser.add_argument(
        "--rename-map",
        metavar="JSON",
        default=None,
        help='JSON object mapping old key names to new ones, e.g. \'{"OLD": "NEW"}\'",',
    )
    parser.add_argument(
        "--rename-file",
        metavar="PATH",
        default=None,
        help="Path to a JSON file containing the rename mappings.",
    )


def _load_mappings(args: argparse.Namespace) -> Optional[dict]:
    """Load rename mappings from --rename-map or --rename-file."""
    if args.rename_file:
        with open(args.rename_file, "r") as fh:
            return json.load(fh)
    if args.rename_map:
        return json.loads(args.rename_map)
    return None


def handle_rename(args: argparse.Namespace, result: DiffResult):
    """Apply renames if requested; returns (modified_result, was_applied)."""
    if not args.rename:
        return result, False

    mappings = _load_mappings(args)
    if not mappings:
        return result, False

    config = build_rename_config(mappings)
    rename_res = rename_result(result, config)

    if rename_res.has_renames:
        print(rename_res.summary())

    return rename_res.result, True
