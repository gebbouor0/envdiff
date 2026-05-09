"""Snapshot .env comparison results to disk for later diffing or auditing."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from envdiff.comparator import DiffResult


@dataclass
class Snapshot:
    label: str
    timestamp: str
    missing_in_right: dict[str, str]
    missing_in_left: dict[str, str]
    mismatched: dict[str, tuple[str, str]]
    metadata: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "missing_in_right": self.missing_in_right,
            "missing_in_left": self.missing_in_left,
            "mismatched": {
                k: list(v) for k, v in self.mismatched.items()
            },
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        return Snapshot(
            label=data["label"],
            timestamp=data["timestamp"],
            missing_in_right=data["missing_in_right"],
            missing_in_left=data["missing_in_left"],
            mismatched={
                k: tuple(v) for k, v in data["mismatched"].items()
            },
            metadata=data.get("metadata", {}),
        )


def take_snapshot(
    result: DiffResult,
    label: str,
    metadata: Optional[dict] = None,
) -> Snapshot:
    """Create a Snapshot from a DiffResult."""
    now = datetime.now(timezone.utc).isoformat()
    return Snapshot(
        label=label,
        timestamp=now,
        missing_in_right=dict(result.missing_in_right),
        missing_in_left=dict(result.missing_in_left),
        mismatched=dict(result.mismatched),
        metadata=metadata or {},
    )


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Write a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.as_dict(), fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)
