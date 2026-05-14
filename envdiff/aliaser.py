"""aliaser.py — map canonical key names to one or more aliases across env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class AliasConfig:
    """Maps a canonical key name to a list of known aliases."""
    mappings: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class AliasResult:
    """Outcome of applying alias resolution to a DiffResult."""
    resolved: Dict[str, str]          # alias_key -> canonical_key
    unresolved_missing_right: List[str]
    unresolved_missing_left: List[str]
    unresolved_mismatched: List[str]

    def has_unresolved(self) -> bool:
        return bool(
            self.unresolved_missing_right
            or self.unresolved_missing_left
            or self.unresolved_mismatched
        )

    def summary(self) -> str:
        total = len(self.resolved)
        unresolved = (
            len(self.unresolved_missing_right)
            + len(self.unresolved_missing_left)
            + len(self.unresolved_mismatched)
        )
        return f"{total} alias(es) resolved, {unresolved} key(s) still unresolved"


def build_alias_config(mappings: Dict[str, List[str]]) -> AliasConfig:
    """Create an AliasConfig from a plain dict of canonical -> [aliases]."""
    return AliasConfig(mappings=mappings)


def _find_canonical(key: str, config: AliasConfig) -> Optional[str]:
    """Return the canonical name for *key* if it matches any alias pattern."""
    for canonical, aliases in config.mappings.items():
        for alias in aliases:
            if fnmatch(key, alias):
                return canonical
    return None


def resolve_aliases(result: DiffResult, config: AliasConfig) -> AliasResult:
    """Walk every differing key and attempt to resolve it via aliases."""
    resolved: Dict[str, str] = {}

    def _resolve_list(keys: List[str]) -> List[str]:
        unresolved = []
        for k in keys:
            canonical = _find_canonical(k, config)
            if canonical is not None:
                resolved[k] = canonical
            else:
                unresolved.append(k)
        return unresolved

    unresolved_right = _resolve_list(result.missing_in_right)
    unresolved_left = _resolve_list(result.missing_in_left)
    unresolved_mismatch = _resolve_list(list(result.mismatched_values.keys()))

    return AliasResult(
        resolved=resolved,
        unresolved_missing_right=unresolved_right,
        unresolved_missing_left=unresolved_left,
        unresolved_mismatched=unresolved_mismatch,
    )
