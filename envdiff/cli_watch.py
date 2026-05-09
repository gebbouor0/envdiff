"""CLI helpers for the --watch flag."""

from __future__ import annotations

import argparse
from typing import Any

from envdiff.comparator import DiffResult
from envdiff.reporter import format_report
from envdiff.watcher import watch


def add_watch_args(parser: argparse.ArgumentParser) -> None:
    """Register watch-related arguments on *parser*."""
    parser.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Poll files for changes and print a fresh diff on every modification.",
    )
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval when --watch is active (default: 1.0).",
    )


def handle_watch(args: argparse.Namespace, **_: Any) -> bool:
    """If --watch is set, start the watch loop and return True.

    Returns False when --watch was not requested so the caller can
    continue with normal (single-shot) processing.
    """
    if not args.watch:
        return False

    print(f"Watching {args.left} and {args.right} (interval={args.watch_interval}s) …")
    print("Press Ctrl-C to stop.\n")

    def _on_change(result: DiffResult) -> None:
        print("\n--- change detected ---")
        print(format_report(result))

    try:
        watch(
            args.left,
            args.right,
            on_change=_on_change,
            interval=args.watch_interval,
        )
    except KeyboardInterrupt:
        print("\nWatcher stopped.")

    return True
