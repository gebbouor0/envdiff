"""Watch .env files for changes and report diffs on modification."""

from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envdiff.parser import parse_env_file
from envdiff.comparator import compare, DiffResult


@dataclass
class WatchState:
    """Tracks last-seen mtime and parsed contents for a watched file."""
    path: Path
    mtime: float = 0.0
    env: dict[str, str] = field(default_factory=dict)

    def refresh(self) -> bool:
        """Re-read file if modified. Returns True if changed."""
        try:
            new_mtime = os.path.getmtime(self.path)
        except FileNotFoundError:
            return False
        if new_mtime != self.mtime:
            self.mtime = new_mtime
            self.env = parse_env_file(str(self.path))
            return True
        return False


def watch(
    left: str,
    right: str,
    on_change: Callable[[DiffResult], None],
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
) -> None:
    """Poll two env files and call on_change whenever either changes.

    Args:
        left: Path to the left .env file.
        right: Path to the right .env file.
        on_change: Callback invoked with a fresh DiffResult on every change.
        interval: Polling interval in seconds.
        max_cycles: Stop after this many cycles (None = run forever).
    """
    left_state = WatchState(path=Path(left))
    right_state = WatchState(path=Path(right))

    # Prime initial state without triggering callback.
    left_state.refresh()
    right_state.refresh()

    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        time.sleep(interval)
        left_changed = left_state.refresh()
        right_changed = right_state.refresh()
        if left_changed or right_changed:
            result = compare(left_state.env, right_state.env)
            on_change(result)
        cycles += 1
