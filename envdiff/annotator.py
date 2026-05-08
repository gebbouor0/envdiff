"""Annotate a dict of env vars with metadata: source file, type guess, and notes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}


@dataclass
class Annotation:
    key: str
    value: str
    source: str
    value_type: str  # "bool", "int", "float", "empty", "url", "string"
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "source": self.source,
            "value_type": self.value_type,
            "notes": self.notes,
        }


def _guess_type(value: str) -> str:
    if value == "":
        return "empty"
    if value.lower() in _BOOL_VALUES:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    if value.startswith(("http://", "https://", "ftp://")):
        return "url"
    return "string"


def _build_notes(key: str, value: str, value_type: str) -> List[str]:
    notes: List[str] = []
    if value_type == "empty":
        notes.append("value is empty")
    if " " in key:
        notes.append("key contains spaces")
    if key != key.upper():
        notes.append("key is not uppercase")
    if len(value) > 200:
        notes.append("value is unusually long")
    return notes


def annotate(env: Dict[str, str], source: str) -> List[Annotation]:
    """Return a list of Annotation objects for each key in *env*."""
    result: List[Annotation] = []
    for key, value in env.items():
        vtype = _guess_type(value)
        notes = _build_notes(key, value, vtype)
        result.append(Annotation(key=key, value=value, source=source, value_type=vtype, notes=notes))
    return result


def annotations_as_dict(annotations: List[Annotation]) -> List[dict]:
    return [a.as_dict() for a in annotations]
