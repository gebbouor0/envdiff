"""Tag keys in a diff result with arbitrary labels for categorization."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Set

from envdiff.comparator import DiffResult


@dataclass
class TagConfig:
    """Maps tag names to lists of key patterns (glob-style)."""
    tags: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class TagResult:
    """Associates each key with a set of tags."""
    tagged: Dict[str, Set[str]] = field(default_factory=dict)

    def tags_for(self, key: str) -> Set[str]:
        return self.tagged.get(key, set())

    def keys_for_tag(self, tag: str) -> List[str]:
        return sorted(k for k, tags in self.tagged.items() if tag in tags)

    def all_tags(self) -> Set[str]:
        result: Set[str] = set()
        for tags in self.tagged.values():
            result |= tags
        return result

    def summary(self) -> str:
        if not self.tagged:
            return "No keys tagged."
        lines = []
        for tag in sorted(self.all_tags()):
            keys = self.keys_for_tag(tag)
            lines.append(f"  [{tag}] {len(keys)} key(s): {', '.join(keys)}")
        return "\n".join(lines)


def _all_keys(result: DiffResult) -> Set[str]:
    return (
        set(result.missing_in_right)
        | set(result.missing_in_left)
        | set(result.mismatched)
    )


def tag_result(result: DiffResult, config: TagConfig) -> TagResult:
    """Apply tag patterns to all keys present in the diff result."""
    keys = _all_keys(result)
    tagged: Dict[str, Set[str]] = {k: set() for k in keys}
    for tag, patterns in config.tags.items():
        for key in keys:
            if any(fnmatch(key, p) for p in patterns):
                tagged[key].add(tag)
    return TagResult(tagged=tagged)


def build_tag_config(raw: Dict[str, List[str]]) -> TagConfig:
    """Build a TagConfig from a plain dict of {tag: [patterns]}."""
    return TagConfig(tags={str(k): list(v) for k, v in raw.items()})
