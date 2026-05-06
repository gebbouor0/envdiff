"""Formatting and reporting of diff results for terminal output."""

from typing import Optional
from envdiff.comparator import DiffResult

ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_CYAN = "\033[96m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_report(
    result: DiffResult,
    left_name: str = "left",
    right_name: str = "right",
    use_color: bool = True,
) -> str:
    """Return a human-readable diff report as a string."""
    lines = []

    header = f"envdiff: {left_name}  vs  {right_name}"
    lines.append(_colorize(header, ANSI_BOLD, use_color))
    lines.append("-" * len(header))

    if not result.has_differences():
        lines.append(_colorize("✓ No differences found.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    if result.missing_in_right:
        lines.append(_colorize(f"\nMissing in {right_name}:", ANSI_RED, use_color))
        for key in sorted(result.missing_in_right):
            lines.append(f"  - {key}")

    if result.missing_in_left:
        lines.append(_colorize(f"\nMissing in {left_name}:", ANSI_YELLOW, use_color))
        for key in sorted(result.missing_in_left):
            lines.append(f"  + {key}")

    if result.mismatched_values:
        lines.append(_colorize("\nMismatched values:", ANSI_CYAN, use_color))
        for key in sorted(result.mismatched_values):
            left_val, right_val = result.mismatched_values[key]
            lines.append(f"  ~ {key}")
            lines.append(f"      {left_name}: {left_val!r}")
            lines.append(f"      {right_name}: {right_val!r}")

    lines.append("")
    lines.append(result.summary())
    return "\n".join(lines)


def print_report(
    result: DiffResult,
    left_name: str = "left",
    right_name: str = "right",
    use_color: bool = True,
) -> None:
    """Print the diff report to stdout."""
    print(format_report(result, left_name, right_name, use_color))
