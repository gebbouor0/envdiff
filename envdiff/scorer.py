"""Score the similarity between two .env files."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envdiff.comparator import DiffResult


@dataclass
class ScoreResult:
    """Holds the similarity score between two env files."""

    total_keys: int
    matching_keys: int
    missing_in_left: int
    missing_in_right: int
    mismatched_values: int

    @property
    def score(self) -> float:
        """Return a 0.0–1.0 similarity score."""
        if self.total_keys == 0:
            return 1.0
        return round(self.matching_keys / self.total_keys, 4)

    @property
    def percent(self) -> float:
        """Return the score as a percentage."""
        return round(self.score * 100, 2)

    def summary(self) -> str:
        return (
            f"Similarity: {self.percent}% "
            f"({self.matching_keys}/{self.total_keys} keys match)"
        )

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "percent": self.percent,
            "total_keys": self.total_keys,
            "matching_keys": self.matching_keys,
            "missing_in_left": self.missing_in_left,
            "missing_in_right": self.missing_in_right,
            "mismatched_values": self.mismatched_values,
        }


def score(result: "DiffResult") -> ScoreResult:
    """Compute a similarity score from a DiffResult."""
    missing_left = len(result.missing_in_left)
    missing_right = len(result.missing_in_right)
    mismatched = len(result.mismatched_values)

    all_keys = (
        set(result.missing_in_left)
        | set(result.missing_in_right)
        | set(result.mismatched_values)
    )
    # Keys that appear in both with same value are not tracked in DiffResult,
    # so we infer total from the union of all problem keys + matching count.
    problem_keys = len(all_keys)
    # matching_keys is whatever isn't a problem
    # We need total_keys — derive it from the DiffResult if possible.
    total_keys = getattr(result, "_total_keys", None)
    if total_keys is None:
        total_keys = problem_keys  # fallback: only problems are known
    matching_keys = max(0, total_keys - problem_keys)

    return ScoreResult(
        total_keys=total_keys,
        matching_keys=matching_keys,
        missing_in_left=missing_left,
        missing_in_right=missing_right,
        mismatched_values=mismatched,
    )
