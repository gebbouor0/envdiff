"""CLI helpers for the tagger feature."""

from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from typing import Any, Dict

from envdiff.comparator import DiffResult
from envdiff.tagger import build_tag_config, tag_result


def add_tag_args(parser: ArgumentParser) -> None:
    """Register --tag and --tag-config flags on *parser*."""
    parser.add_argument(
        "--tag",
        action="store_true",
        default=False,
        help="Show tag summary for diff keys.",
    )
    parser.add_argument(
        "--tag-config",
        metavar="FILE",
        default=None,
        help="JSON file mapping tag names to key patterns, e.g. {\"db\": [\"DB_*\"]}",
    )


def _load_tag_config_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def handle_tag(args: Namespace, result: DiffResult) -> bool:
    """Print tag summary if --tag was requested.

    Returns True if handled, False otherwise.
    """
    if not getattr(args, "tag", False):
        return False

    raw: Dict[str, Any] = {}
    if args.tag_config:
        raw = _load_tag_config_file(args.tag_config)

    config = build_tag_config(raw)
    tr = tag_result(result, config)
    print(tr.summary())
    return True
