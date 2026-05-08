"""CLI helpers for the --patch feature."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.parser import parse_env_file
from envdiff.patcher import apply_patch, build_patch, write_patched_env


def add_patch_args(parser: argparse.ArgumentParser) -> None:
    """Register patch-related flags onto *parser*."""
    group = parser.add_argument_group("patching")
    group.add_argument(
        "--patch",
        metavar="OUTPUT",
        default=None,
        help="Write a patched version of the RIGHT file to OUTPUT.",
    )
    group.add_argument(
        "--patch-direction",
        choices=["left_to_right", "right_to_left"],
        default="left_to_right",
        dest="patch_direction",
        help="Which side drives the patch (default: left_to_right).",
    )
    group.add_argument(
        "--patch-keep-existing",
        action="store_true",
        default=False,
        dest="patch_keep_existing",
        help="Do not overwrite keys that already exist in the target file.",
    )


def handle_patch(
    args: argparse.Namespace,
    diff: DiffResult,
    right_file: str,
) -> bool:
    """Execute patching if requested.  Returns True when a patch was written."""
    output: Optional[str] = getattr(args, "patch", None)
    if not output:
        return False

    direction: str = getattr(args, "patch_direction", "left_to_right")
    keep_existing: bool = getattr(args, "patch_keep_existing", False)

    # Load the target env (right side by convention)
    env = parse_env_file(right_file)

    patch = build_patch(diff, direction=direction)
    result = apply_patch(env, patch, keep_existing=keep_existing)

    out_path = Path(output)
    write_patched_env(env, out_path, header=f"patched from {right_file}")

    print(f"[patch] {result.summary()} → {out_path}")
    return True
