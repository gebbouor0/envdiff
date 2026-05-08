"""Redact sensitive values in diff results before display or export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult

_DEFAULT_PATTERNS = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

REDACTED = "***REDACTED***"


@dataclass
class RedactConfig:
    patterns: List[str] = field(default_factory=lambda: list(_DEFAULT_PATTERNS))
    placeholder: str = REDACTED
    case_sensitive: bool = False


def _matches_any(key: str, patterns: List[str], case_sensitive: bool) -> bool:
    flags = 0 if case_sensitive else re.IGNORECASE
    return any(re.fullmatch(p, key, flags=flags) for p in patterns)


def _redact_dict(
    d: Dict[str, str],
    patterns: List[str],
    placeholder: str,
    case_sensitive: bool,
) -> Dict[str, str]:
    return {
        k: (placeholder if _matches_any(k, patterns, case_sensitive) else v)
        for k, v in d.items()
    }


def redact_result(result: DiffResult, config: Optional[RedactConfig] = None) -> DiffResult:
    """Return a new DiffResult with sensitive values replaced by the placeholder."""
    if config is None:
        config = RedactConfig()

    p = config.patterns
    ph = config.placeholder
    cs = config.case_sensitive

    new_missing_in_right = _redact_dict(result.missing_in_right, p, ph, cs)
    new_missing_in_left = _redact_dict(result.missing_in_left, p, ph, cs)

    new_mismatched: Dict[str, tuple] = {}
    for key, (lv, rv) in result.mismatched_values.items():
        if _matches_any(key, p, cs):
            new_mismatched[key] = (ph, ph)
        else:
            new_mismatched[key] = (lv, rv)

    return DiffResult(
        missing_in_right=new_missing_in_right,
        missing_in_left=new_missing_in_left,
        mismatched_values=new_mismatched,
    )


def build_redact_config(
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED,
    case_sensitive: bool = False,
) -> RedactConfig:
    """Convenience constructor for RedactConfig."""
    return RedactConfig(
        patterns=patterns if patterns is not None else list(_DEFAULT_PATTERNS),
        placeholder=placeholder,
        case_sensitive=case_sensitive,
    )
