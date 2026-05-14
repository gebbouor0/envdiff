"""cli_mask.py — CLI integration for the masker feature."""
from __future__ import annotations

import argparse
import json
from typing import Optional

from envdiff.masker import MaskConfig, build_mask_config, mask_env
from envdiff.parser import parse_env_file


def add_mask_args(parser: argparse.ArgumentParser) -> None:
    """Register --mask and related flags on an existing argument parser."""
    parser.add_argument(
        "--mask",
        action="store_true",
        default=False,
        help="Mask sensitive values before displaying output.",
    )
    parser.add_argument(
        "--mask-patterns",
        nargs="+",
        metavar="PATTERN",
        default=None,
        help="Glob patterns for keys to mask (default: built-in sensitive patterns).",
    )
    parser.add_argument(
        "--mask-placeholder",
        default="***",
        metavar="TEXT",
        help="Replacement text for masked values (default: ***).",
    )


def handle_mask(
    args: argparse.Namespace,
    env_path: Optional[str] = None,
) -> bool:
    """Handle mask-related CLI flags.  Returns True if mask output was produced."""
    if not getattr(args, "mask", False):
        return False

    target = env_path or getattr(args, "left", None)
    if target is None:
        print("[mask] No env file specified.")
        return True

    env = parse_env_file(target)
    config = build_mask_config(
        patterns=args.mask_patterns,
        placeholder=args.mask_placeholder,
    )
    result = mask_env(env, config=config)
    print(result.summary)
    print(json.dumps(result.masked, indent=2))
    return True
