"""Sorting utilities for DiffResult entries.

Provides functions to reorder the keys within a DiffResult so that
reports are presented in a consistent, predictable order.
"""

from enum import Enum
from typing import Callable

from envdiff.comparator import DiffResult


class SortOrder(str, Enum):
    """Available sort orders for diff results."""

    ALPHA = "alpha"          # alphabetical by key name (default)
    ALPHA_DESC = "alpha_desc"  # reverse alphabetical
    TYPE = "type"            # group by diff type: missing_left, missing_right, mismatched
    NONE = "none"            # preserve original insertion order


# Ordering used when SortOrder.TYPE is selected
_TYPE_RANK: dict[str, int] = {
    "missing_in_right": 0,
    "missing_in_left": 1,
    "mismatched": 2,
}


def _key_alpha(item: tuple[str, object]) -> str:
    """Sort key: alphabetical by env-var name (case-insensitive)."""
    return item[0].lower()


def _key_type_then_alpha(
    item: tuple[str, object],
    source: str,
) -> tuple[int, str]:
    """Sort key: diff-type bucket first, then alphabetical within bucket.

    Args:
        item: A (key, value) pair from one of the DiffResult dicts.
        source: Which dict the item came from – used to determine rank.
    """
    return (_TYPE_RANK.get(source, 99), item[0].lower())


def sort_result(result: DiffResult, order: SortOrder = SortOrder.ALPHA) -> DiffResult:
    """Return a new DiffResult with its entries sorted according to *order*.

    The original DiffResult is not mutated.

    Args:
        result: The comparison result to sort.
        order:  One of the SortOrder enum values.

    Returns:
        A new DiffResult whose internal dicts are sorted.
    """
    if order is SortOrder.NONE:
        # Return a shallow copy so callers always get a new object.
        return DiffResult(
            missing_in_right=dict(result.missing_in_right),
            missing_in_left=dict(result.missing_in_left),
            mismatched=dict(result.mismatched),
        )

    if order is SortOrder.ALPHA:
        key_fn: Callable = _key_alpha
        reverse = False
    elif order is SortOrder.ALPHA_DESC:
        key_fn = _key_alpha
        reverse = True
    elif order is SortOrder.TYPE:
        # For TYPE ordering we sort each sub-dict alphabetically, but keep
        # the sub-dicts themselves in the canonical type order (the DiffResult
        # dataclass fields already encode that order).
        return DiffResult(
            missing_in_right=dict(
                sorted(result.missing_in_right.items(), key=_key_alpha)
            ),
            missing_in_left=dict(
                sorted(result.missing_in_left.items(), key=_key_alpha)
            ),
            mismatched=dict(
                sorted(result.mismatched.items(), key=_key_alpha)
            ),
        )
    else:
        raise ValueError(f"Unknown sort order: {order!r}")

    return DiffResult(
        missing_in_right=dict(
            sorted(result.missing_in_right.items(), key=key_fn, reverse=reverse)
        ),
        missing_in_left=dict(
            sorted(result.missing_in_left.items(), key=key_fn, reverse=reverse)
        ),
        mismatched=dict(
            sorted(result.mismatched.items(), key=key_fn, reverse=reverse)
        ),
    )
