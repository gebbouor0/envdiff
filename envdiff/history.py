"""History manager for envdiff snapshots.

Provides functionality to store, load, list, and compare snapshots
over time, enabling drift detection between environments.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from envdiff.snapshotter import Snapshot, from_dict, take_snapshot
from envdiff.comparator import DiffResult


# Default directory for storing history files
DEFAULT_HISTORY_DIR = ".envdiff_history"


def _history_dir(base: Optional[str] = None) -> Path:
    """Return the resolved history directory path."""
    return Path(base or DEFAULT_HISTORY_DIR)


def save_to_history(
    result: DiffResult,
    label: str,
    history_dir: Optional[str] = None,
) -> Path:
    """Take a snapshot of *result* and persist it to the history directory.

    The file is named ``<timestamp>_<label>.json`` so that lexicographic
    ordering matches chronological ordering.

    Args:
        result: The diff result to snapshot.
        label: A short human-readable label (e.g. "staging-vs-prod").
        history_dir: Override the default history directory.

    Returns:
        The path of the written snapshot file.
    """
    snap = take_snapshot(result, label)
    directory = _history_dir(history_dir)
    directory.mkdir(parents=True, exist_ok=True)

    # Sanitize label for use in a filename
    safe_label = label.replace(" ", "_").replace("/", "-")
    # ISO timestamp already uses colons — replace them for filesystem safety
    ts = snap.timestamp.replace(":", "-")
    filename = directory / f"{ts}_{safe_label}.json"

    filename.write_text(json.dumps(snap.as_dict(), indent=2), encoding="utf-8")
    return filename


def load_snapshot(path: str | Path) -> Snapshot:
    """Load a single snapshot from a JSON file.

    Args:
        path: Path to the snapshot JSON file.

    Returns:
        A :class:`~envdiff.snapshotter.Snapshot` instance.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return from_dict(data)


def list_snapshots(history_dir: Optional[str] = None) -> List[Path]:
    """Return all snapshot files in the history directory, sorted oldest-first.

    Args:
        history_dir: Override the default history directory.

    Returns:
        A sorted list of :class:`pathlib.Path` objects.
    """
    directory = _history_dir(history_dir)
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


def load_all_snapshots(history_dir: Optional[str] = None) -> List[Snapshot]:
    """Load every snapshot from the history directory, oldest-first.

    Args:
        history_dir: Override the default history directory.

    Returns:
        A list of :class:`~envdiff.snapshotter.Snapshot` instances.
    """
    return [load_snapshot(p) for p in list_snapshots(history_dir)]


def latest_snapshot(history_dir: Optional[str] = None) -> Optional[Snapshot]:
    """Return the most recent snapshot, or *None* if history is empty.

    Args:
        history_dir: Override the default history directory.
    """
    paths = list_snapshots(history_dir)
    if not paths:
        return None
    return load_snapshot(paths[-1])


def purge_history(history_dir: Optional[str] = None, keep: int = 0) -> int:
    """Delete snapshot files, optionally keeping the *N* most recent.

    Args:
        history_dir: Override the default history directory.
        keep: Number of most-recent snapshots to retain. ``0`` removes all.

    Returns:
        The number of files deleted.
    """
    paths = list_snapshots(history_dir)
    to_delete = paths[: max(0, len(paths) - keep)]
    for p in to_delete:
        os.remove(p)
    return len(to_delete)
