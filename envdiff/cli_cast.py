"""CLI integration for the caster feature."""
from __future__ import annotations

import argparse
import json
from typing import Any

from envdiff.caster import cast_env, CastResult


def add_cast_args(parser: argparse.ArgumentParser) -> None:
    """Register --cast and --cast-schema flags on *parser*."""
    parser.add_argument(
        "--cast",
        action="store_true",
        default=False,
        help="Cast env values according to --cast-schema",
    )
    parser.add_argument(
        "--cast-schema",
        metavar="JSON",
        default=None,
        help='JSON object mapping key names to types, e.g. \'{"PORT":"int"}\'',
    )


def handle_cast(
    args: argparse.Namespace,
    env: dict[str, str],
) -> bool:
    """Run casting if requested.  Returns True when cast output was printed."""
    if not getattr(args, "cast", False):
        return False

    raw_schema = getattr(args, "cast_schema", None) or "{}"
    try:
        schema: dict[str, str] = json.loads(raw_schema)
    except json.JSONDecodeError as exc:
        print(f"[cast] Invalid --cast-schema JSON: {exc}")
        return True

    result: CastResult = cast_env(env, schema)

    print("[cast] " + result.summary())
    if result.has_failures():
        print("[cast] Failures:")
        for key, msg in result.failures.items():
            print(f"  {key}: {msg}")

    print("[cast] Casted values:")
    for key, value in result.casted.items():
        print(f"  {key} = {value!r}  ({type(value).__name__})")

    return True
