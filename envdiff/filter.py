"""Filter and search utilities for DiffResult objects."""

from __future__ import annotations

from typing import Optional

from envdiff.comparator import DiffResult


def filter_result(
    result: DiffResult,
    *,
    keys: Optional[list[str]] = None,
    only_missing: bool = False,
    only_mismatched: bool = False,
) -> DiffResult:
    """Return a new DiffResult restricted to the given criteria.

    Args:
        result: The original comparison result.
        keys: If provided, only include entries whose key is in this list.
        only_missing: If True, drop mismatched-value entries (keep missing only).
        only_mismatched: If True, drop missing-key entries (keep mismatches only).

    Returns:
        A filtered DiffResult.
    """
    if only_missing and only_mismatched:
        raise ValueError("only_missing and only_mismatched are mutually exclusive")

    missing_in_right = result.missing_in_right
    missing_in_left = result.missing_in_left
    mismatched = result.mismatched_values

    if keys is not None:
        key_set = set(keys)
        missing_in_right = {k: v for k, v in missing_in_right.items() if k in key_set}
        missing_in_left = {k: v for k, v in missing_in_left.items() if k in key_set}
        mismatched = {k: v for k, v in mismatched.items() if k in key_set}

    if only_missing:
        mismatched = {}
    elif only_mismatched:
        missing_in_right = {}
        missing_in_left = {}

    return DiffResult(
        missing_in_right=missing_in_right,
        missing_in_left=missing_in_left,
        mismatched_values=mismatched,
    )


def search_keys(result: DiffResult, pattern: str) -> DiffResult:
    """Return a new DiffResult keeping only keys that contain *pattern* (case-insensitive).

    Args:
        result: The original comparison result.
        pattern: Substring to search for in key names.

    Returns:
        A filtered DiffResult.
    """
    pat = pattern.lower()
    matching_keys = [
        k
        for k in (
            set(result.missing_in_right)
            | set(result.missing_in_left)
            | set(result.mismatched_values)
        )
        if pat in k.lower()
    ]
    return filter_result(result, keys=matching_keys)
