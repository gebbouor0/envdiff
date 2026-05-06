"""Summarizer module: produce statistical summaries of diff results."""

from dataclasses import dataclass
from typing import Dict, List
from envdiff.comparator import DiffResult


@dataclass
class DiffSummary:
    total_keys: int
    missing_in_left_count: int
    missing_in_right_count: int
    mismatched_count: int
    match_count: int
    similarity_pct: float
    type_breakdown: Dict[str, int]

    def as_dict(self) -> Dict:
        return {
            "total_keys": self.total_keys,
            "missing_in_left": self.missing_in_left_count,
            "missing_in_right": self.missing_in_right_count,
            "mismatched": self.mismatched_count,
            "matching": self.match_count,
            "similarity_pct": round(self.similarity_pct, 2),
            "type_breakdown": self.type_breakdown,
        }


def summarize(result: DiffResult) -> DiffSummary:
    """Compute a statistical summary from a DiffResult."""
    n_left = len(result.missing_in_left)
    n_right = len(result.missing_in_right)
    n_mismatch = len(result.mismatched)

    all_keys: set = set()
    all_keys.update(result.missing_in_left)
    all_keys.update(result.missing_in_right)
    all_keys.update(result.mismatched.keys())
    all_keys.update(result.common_keys)

    total = len(all_keys)
    match_count = len(result.common_keys) - n_mismatch
    match_count = max(match_count, 0)

    similarity = (match_count / total * 100) if total > 0 else 100.0

    type_breakdown = {
        "missing_in_left": n_left,
        "missing_in_right": n_right,
        "mismatched": n_mismatch,
        "matching": match_count,
    }

    return DiffSummary(
        total_keys=total,
        missing_in_left_count=n_left,
        missing_in_right_count=n_right,
        mismatched_count=n_mismatch,
        match_count=match_count,
        similarity_pct=similarity,
        type_breakdown=type_breakdown,
    )


def format_summary(summary: DiffSummary) -> str:
    """Return a human-readable summary string."""
    lines = [
        f"Total keys : {summary.total_keys}",
        f"Matching   : {summary.match_count}",
        f"Mismatched : {summary.mismatched_count}",
        f"Only left  : {summary.missing_in_right_count}",
        f"Only right : {summary.missing_in_left_count}",
        f"Similarity : {summary.similarity_pct:.1f}%",
    ]
    return "\n".join(lines)
