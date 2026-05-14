"""masker.py — Mask sensitive values in env dicts before display or export."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

_DEFAULT_PATTERNS: List[str] = [
    "*PASSWORD*",
    "*SECRET*",
    "*TOKEN*",
    "*API_KEY*",
    "*PRIVATE_KEY*",
    "*CREDENTIALS*",
]

MASK_PLACEHOLDER = "***"


@dataclass
class MaskConfig:
    patterns: List[str] = field(default_factory=lambda: list(_DEFAULT_PATTERNS))
    case_sensitive: bool = False
    placeholder: str = MASK_PLACEHOLDER


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str]

    @property
    def has_masked(self) -> bool:
        return len(self.masked_keys) > 0

    @property
    def summary(self) -> str:
        if not self.has_masked:
            return "No keys masked."
        keys = ", ".join(sorted(self.masked_keys))
        return f"{len(self.masked_keys)} key(s) masked: {keys}"


def _matches_any(key: str, patterns: List[str], case_sensitive: bool) -> bool:
    test_key = key if case_sensitive else key.upper()
    for pat in patterns:
        test_pat = pat if case_sensitive else pat.upper()
        if fnmatch(test_key, test_pat):
            return True
    return False


def build_mask_config(
    patterns: Optional[List[str]] = None,
    case_sensitive: bool = False,
    placeholder: str = MASK_PLACEHOLDER,
) -> MaskConfig:
    return MaskConfig(
        patterns=patterns if patterns is not None else list(_DEFAULT_PATTERNS),
        case_sensitive=case_sensitive,
        placeholder=placeholder,
    )


def mask_env(
    env: Dict[str, str],
    config: Optional[MaskConfig] = None,
) -> MaskResult:
    if config is None:
        config = MaskConfig()
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []
    for key, value in env.items():
        if _matches_any(key, config.patterns, config.case_sensitive):
            masked[key] = config.placeholder
            masked_keys.append(key)
        else:
            masked[key] = value
    return MaskResult(original=dict(env), masked=masked, masked_keys=masked_keys)
