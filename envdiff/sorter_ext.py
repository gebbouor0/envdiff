"""Extended sorting utilities for envdiff — sort by key length, value length, or custom order."""

from enum import Enum
from typing import Callable

from envdiff.comparator import DiffResult


class ExtSortOrder(Enum):
    KEY_LENGTH = "key_length"
    VALUE_LENGTH = "value_length"
    INSERTION = "insertion"  # preserve original dict order


def _key_by_length(key: str) -> int:
    return len(key)


def _value_length_sort_key(item: tuple[str, tuple[str, str]]) -> int:
    """Sort mismatched items by the length of the left value."""
    _, (left_val, _) = item
    return len(left_val)


def sort_result_ext(result: DiffResult, order: ExtSortOrder) -> DiffResult:
    """Return a new DiffResult with entries sorted by the given extended order."""
    if order == ExtSortOrder.INSERTION:
        # No-op: preserve existing order
        return DiffResult(
            missing_in_right=dict(result.missing_in_right),
            missing_in_left=dict(result.missing_in_left),
            mismatched=dict(result.mismatched),
        )

    if order == ExtSortOrder.KEY_LENGTH:
        sort_fn: Callable = lambda item: _key_by_length(item[0])
        return DiffResult(
            missing_in_right=dict(sorted(result.missing_in_right.items(), key=sort_fn)),
            missing_in_left=dict(sorted(result.missing_in_left.items(), key=sort_fn)),
            mismatched=dict(sorted(result.mismatched.items(), key=sort_fn)),
        )

    if order == ExtSortOrder.VALUE_LENGTH:
        return DiffResult(
            missing_in_right=dict(
                sorted(result.missing_in_right.items(), key=lambda i: len(i[1]))
            ),
            missing_in_left=dict(
                sorted(result.missing_in_left.items(), key=lambda i: len(i[1]))
            ),
            mismatched=dict(
                sorted(result.mismatched.items(), key=_value_length_sort_key)
            ),
        )

    raise ValueError(f"Unknown ExtSortOrder: {order}")
