"""CLI helpers for the --score flag."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envdiff.scorer import ScoreResult


def add_score_args(parser: argparse.ArgumentParser) -> None:
    """Register --score and --score-threshold flags on *parser*."""
    parser.add_argument(
        "--score",
        action="store_true",
        default=False,
        help="Print a similarity score (0–100%%) between the two env files.",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=None,
        metavar="THRESHOLD",
        help=(
            "Exit with code 1 if the similarity score is below this value "
            "(0.0–100.0). Implies --score."
        ),
    )


def handle_score(
    args: argparse.Namespace,
    result: "ScoreResult",
) -> bool:
    """Print score info if requested.  Return True if threshold is breached."""
    wants_score = args.score or (args.score_threshold is not None)
    if not wants_score:
        return False

    print(result.summary())

    threshold = args.score_threshold
    if threshold is not None and result.percent < threshold:
        print(
            f"Score {result.percent}% is below threshold {threshold}%."
        )
        return True  # caller should exit 1

    return False
