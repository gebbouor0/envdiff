"""CLI helpers for the transformer feature."""

from __future__ import annotations

import argparse
from typing import List

from envdiff.transformer import get_builtin_rule, transform_env, TransformRule

_AVAILABLE = ["uppercase_keys", "strip_values", "lowercase_values", "uppercase_values"]


def add_transform_args(parser: argparse.ArgumentParser) -> None:
    """Register --transform flags onto an existing argument parser."""
    parser.add_argument(
        "--transform",
        dest="transform_rules",
        nargs="+",
        metavar="RULE",
        default=None,
        help=(
            "Apply one or more built-in transform rules to the parsed env before "
            "diffing. Available: " + ", ".join(_AVAILABLE)
        ),
    )


def handle_transform(
    args: argparse.Namespace,
    env: dict,
) -> dict:
    """If --transform was requested, apply rules and return transformed env.

    Returns the (possibly unchanged) env dict.
    """
    rule_names: List[str] | None = getattr(args, "transform_rules", None)
    if not rule_names:
        return env

    rules: List[TransformRule] = []
    for name in rule_names:
        rule = get_builtin_rule(name)
        if rule is None:
            raise ValueError(
                f"Unknown transform rule '{name}'. "
                f"Available: {', '.join(_AVAILABLE)}"
            )
        rules.append(rule)

    result = transform_env(env, rules)
    return result.transformed
