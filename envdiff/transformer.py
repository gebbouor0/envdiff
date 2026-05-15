"""Transform env key-value pairs using user-defined rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformRule:
    """A single transformation rule."""
    name: str
    fn: Callable[[str, str], tuple[str, str]]


@dataclass
class TransformResult:
    """Holds the outcome of applying transformations to an env dict."""
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)  # rule names that changed something

    def has_changes(self) -> bool:
        return self.original != self.transformed

    def summary(self) -> str:
        if not self.has_changes():
            return "No transformations applied."
        return (
            f"{len(self.applied)} rule(s) produced changes: "
            + ", ".join(self.applied)
        )

    def as_dict(self) -> dict:
        return {
            "original": self.original,
            "transformed": self.transformed,
            "applied": self.applied,
            "has_changes": self.has_changes(),
        }


_BUILTIN_RULES: Dict[str, TransformRule] = {
    "uppercase_keys": TransformRule(
        name="uppercase_keys",
        fn=lambda k, v: (k.upper(), v),
    ),
    "strip_values": TransformRule(
        name="strip_values",
        fn=lambda k, v: (k, v.strip()),
    ),
    "lowercase_values": TransformRule(
        name="lowercase_values",
        fn=lambda k, v: (k, v.lower()),
    ),
    "uppercase_values": TransformRule(
        name="uppercase_values",
        fn=lambda k, v: (k, v.upper()),
    ),
}


def get_builtin_rule(name: str) -> Optional[TransformRule]:
    return _BUILTIN_RULES.get(name)


def transform_env(
    env: Dict[str, str],
    rules: List[TransformRule],
) -> TransformResult:
    """Apply a sequence of transform rules to an env dict."""
    original = dict(env)
    current: Dict[str, str] = dict(env)
    applied: List[str] = []

    for rule in rules:
        next_env: Dict[str, str] = {}
        changed = False
        for k, v in current.items():
            nk, nv = rule.fn(k, v)
            next_env[nk] = nv
            if nk != k or nv != v:
                changed = True
        if changed:
            applied.append(rule.name)
        current = next_env

    return TransformResult(original=original, transformed=current, applied=applied)
