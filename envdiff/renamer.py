"""Rename keys across a DiffResult — useful when a key was renamed between environments."""

from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.comparator import DiffResult


@dataclass
class RenameConfig:
    """Maps old key names to new key names."""
    mappings: Dict[str, str] = field(default_factory=dict)


@dataclass
class RenameResult:
    """Holds the renamed DiffResult and metadata about what was renamed."""
    result: DiffResult
    renamed_keys: List[str] = field(default_factory=list)

    @property
    def has_renames(self) -> bool:
        return len(self.renamed_keys) > 0

    def summary(self) -> str:
        if not self.has_renames:
            return "No keys renamed."
        keys = ", ".join(self.renamed_keys)
        return f"{len(self.renamed_keys)} key(s) renamed: {keys}"


def build_rename_config(mappings: Dict[str, str]) -> RenameConfig:
    """Build a RenameConfig from a plain dict of old->new key mappings."""
    return RenameConfig(mappings=dict(mappings))


def _rename_dict(d: Dict[str, str], mappings: Dict[str, str]) -> Dict[str, str]:
    """Return a new dict with keys replaced according to mappings."""
    return {mappings.get(k, k): v for k, v in d.items()}


def rename_result(result: DiffResult, config: RenameConfig) -> RenameResult:
    """Apply key renames to all sections of a DiffResult."""
    m = config.mappings
    renamed: List[str] = []

    def _track(d: Dict[str, str]) -> Dict[str, str]:
        out = {}
        for k, v in d.items():
            new_k = m.get(k, k)
            if new_k != k:
                renamed.append(f"{k} -> {new_k}")
            out[new_k] = v
        return out

    def _track_mismatch(d: Dict[str, tuple]) -> Dict[str, tuple]:
        out = {}
        for k, v in d.items():
            new_k = m.get(k, k)
            if new_k != k and f"{k} -> {new_k}" not in renamed:
                renamed.append(f"{k} -> {new_k}")
            out[new_k] = v
        return out

    new_result = DiffResult(
        missing_in_right=_track(result.missing_in_right),
        missing_in_left=_track(result.missing_in_left),
        mismatched=_track_mismatch(result.mismatched),
        common=_track(result.common),
    )
    return RenameResult(result=new_result, renamed_keys=renamed)
