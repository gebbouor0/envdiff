"""Pin current env values as a baseline for future comparisons."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class PinResult:
    label: str
    pinned: Dict[str, str] = field(default_factory=dict)
    drifted: Dict[str, str] = field(default_factory=dict)  # key -> current value
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def has_drift(self) -> bool:
        return bool(self.drifted or self.new_keys or self.removed_keys)

    def summary(self) -> str:
        parts = []
        if self.drifted:
            parts.append(f"{len(self.drifted)} drifted")
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        return ", ".join(parts) if parts else "no drift"

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "pinned": self.pinned,
            "drifted": self.drifted,
            "new_keys": self.new_keys,
            "removed_keys": self.removed_keys,
        }


def pin_env(env: Dict[str, str], label: str) -> PinResult:
    """Create a PinResult capturing the current env as a baseline."""
    return PinResult(label=label, pinned=dict(env))


def check_drift(baseline: PinResult, current: Dict[str, str]) -> PinResult:
    """Compare current env against a pinned baseline and return drift info."""
    drifted: Dict[str, str] = {}
    new_keys: List[str] = []
    removed_keys: List[str] = []

    for key, pinned_val in baseline.pinned.items():
        if key not in current:
            removed_keys.append(key)
        elif current[key] != pinned_val:
            drifted[key] = current[key]

    for key in current:
        if key not in baseline.pinned:
            new_keys.append(key)

    return PinResult(
        label=baseline.label,
        pinned=baseline.pinned,
        drifted=drifted,
        new_keys=sorted(new_keys),
        removed_keys=sorted(removed_keys),
    )


def save_pin(result: PinResult, path: Path) -> None:
    path.write_text(json.dumps(result.as_dict(), indent=2))


def load_pin(path: Path) -> PinResult:
    data = json.loads(path.read_text())
    return PinResult(
        label=data["label"],
        pinned=data["pinned"],
        drifted=data.get("drifted", {}),
        new_keys=data.get("new_keys", []),
        removed_keys=data.get("removed_keys", []),
    )
