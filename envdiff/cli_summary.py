"""CLI helpers for the --summary flag."""

import argparse
from envdiff.comparator import DiffResult
from envdiff.summarizer import summarize, format_summary


def add_summary_args(parser: argparse.ArgumentParser) -> None:
    """Attach --summary flag to an existing argument parser."""
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a statistical summary of the diff instead of the full report.",
    )
    parser.add_argument(
        "--summary-json",
        action="store_true",
        default=False,
        help="Print the summary as a JSON object.",
    )


def handle_summary(
    args: argparse.Namespace,
    result: DiffResult,
) -> bool:
    """Print summary output if requested.  Returns True if summary was printed."""
    if not (args.summary or args.summary_json):
        return False

    s = summarize(result)

    if args.summary_json:
        import json
        print(json.dumps(s.as_dict(), indent=2))
    else:
        print(format_summary(s))

    return True
