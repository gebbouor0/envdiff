"""CLI support for pinning and drift-checking env files."""

from __future__ import annotations

import argparse
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.pinner import check_drift, load_pin, pin_env, save_pin


def add_pin_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--pin",
        metavar="FILE",
        default=None,
        help="Pin current left env to FILE as a baseline",
    )
    parser.add_argument(
        "--check-drift",
        metavar="FILE",
        default=None,
        dest="check_drift",
        help="Check left env for drift against a pinned baseline FILE",
    )
    parser.add_argument(
        "--pin-label",
        default="baseline",
        dest="pin_label",
        help="Label to attach to the pin (default: baseline)",
    )


def handle_pin(args: argparse.Namespace, left_path: str) -> bool:
    """Handle --pin and --check-drift flags. Returns True if action was taken."""
    if args.pin:
        env = parse_env_file(left_path)
        result = pin_env(env, label=args.pin_label)
        save_pin(result, Path(args.pin))
        print(f"Pinned {len(result.pinned)} keys to {args.pin} [{args.pin_label}]")
        return True

    if args.check_drift:
        env = parse_env_file(left_path)
        baseline = load_pin(Path(args.check_drift))
        result = check_drift(baseline, env)
        if result.has_drift():
            print(f"Drift detected against '{baseline.label}': {result.summary()}")
            for key, val in result.drifted.items():
                print(f"  ~ {key}: was {baseline.pinned[key]!r}, now {val!r}")
            for key in result.new_keys:
                print(f"  + {key} (new)")
            for key in result.removed_keys:
                print(f"  - {key} (removed)")
        else:
            print(f"No drift detected against '{baseline.label}'.")
        return True

    return False
