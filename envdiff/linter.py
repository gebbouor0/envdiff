"""Lint .env files for style and convention issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # "warning" or "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        if not self.has_issues:
            return "No lint issues found."
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) "
            f"across {len(self.issues)} issue(s)."
        )


def _check_key_naming(key: str) -> List[LintIssue]:
    """Keys should be UPPER_SNAKE_CASE."""
    issues = []
    if key != key.upper():
        issues.append(LintIssue(key, "Key should be uppercase (UPPER_SNAKE_CASE).", "warning"))
    if " " in key:
        issues.append(LintIssue(key, "Key contains spaces.", "error"))
    if key and key[0].isdigit():
        issues.append(LintIssue(key, "Key starts with a digit.", "error"))
    return issues


def _check_value(key: str, value: str) -> List[LintIssue]:
    """Check for common value problems."""
    issues = []
    if value == "":
        issues.append(LintIssue(key, "Value is empty.", "warning"))
    if value != value.strip():
        issues.append(LintIssue(key, "Value has leading or trailing whitespace.", "warning"))
    if len(value) > 500:
        issues.append(LintIssue(key, "Value is unusually long (>500 chars).", "warning"))
    return issues


def lint(env: Dict[str, str]) -> LintResult:
    """Run all lint checks on a parsed env dict."""
    result = LintResult()
    for key, value in env.items():
        result.issues.extend(_check_key_naming(key))
        result.issues.extend(_check_value(key, value))
    return result
