"""Command-line interface for envdiff."""

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and highlight missing or mismatched keys.",
    )
    parser.add_argument("left", type=Path, help="First .env file (reference)")
    parser.add_argument("right", type=Path, help="Second .env file (to compare)")
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found",
    )
    return parser


def run(argv=None) -> int:
    """Entry point; returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    left_path: Path = args.left
    right_path: Path = args.right

    for path in (left_path, right_path):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2

    left_env = parse_env_file(left_path)
    right_env = parse_env_file(right_path)

    result = compare(left_env, right_env)

    print_report(
        result,
        left_name=left_path.name,
        right_name=right_path.name,
        use_color=not args.no_color,
    )

    if args.exit_code and result.has_differences():
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
