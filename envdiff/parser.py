"""Parser for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


COMMENT_RE = re.compile(r"^\s*#.*$")
BLANK_RE = re.compile(r"^\s*$")
KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def parse_env_file(path: str | Path) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    - Comments (lines starting with #) are ignored.
    - Blank lines are ignored.
    - Values may be optionally quoted (single or double); quotes are stripped.
    - Keys with no value (e.g. ``KEY=``) are stored as empty string.

    Args:
        path: Path to the .env file.

    Returns:
        Ordered dict of {key: value} pairs.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If a line cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    result: Dict[str, Optional[str]] = {}

    with path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")

            if COMMENT_RE.match(line) or BLANK_RE.match(line):
                continue

            match = KEY_VALUE_RE.match(line)
            if not match:
                raise ValueError(
                    f"Invalid syntax at {path}:{lineno}: {line!r}"
                )

            key, value = match.group(1), match.group(2).strip()
            value = _strip_quotes(value)
            result[key] = value

    return result


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value
