"""Tests for envdiff.linter."""
import pytest
from envdiff.linter import lint, LintIssue, LintResult


@pytest.fixture
def clean_env():
    return {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}


def test_clean_env_no_issues(clean_env):
    result = lint(clean_env)
    assert not result.has_issues


def test_summary_no_issues(clean_env):
    result = lint(clean_env)
    assert result.summary() == "No lint issues found."


def test_lowercase_key_triggers_warning():
    result = lint({"database_url": "value"})
    assert result.has_issues
    messages = [i.message for i in result.issues]
    assert any("uppercase" in m for m in messages)


def test_key_with_space_triggers_error():
    result = lint({"BAD KEY": "value"})
    errors = result.errors
    assert len(errors) >= 1
    assert any("spaces" in e.message for e in errors)


def test_key_starting_with_digit_triggers_error():
    result = lint({"1BAD": "value"})
    errors = result.errors
    assert any("digit" in e.message for e in errors)


def test_empty_value_triggers_warning():
    result = lint({"MY_KEY": ""})
    warnings = result.warnings
    assert any("empty" in w.message for w in warnings)


def test_whitespace_value_triggers_warning():
    result = lint({"MY_KEY": "  value  "})
    warnings = result.warnings
    assert any("whitespace" in w.message for w in warnings)


def test_very_long_value_triggers_warning():
    result = lint({"MY_KEY": "x" * 501})
    warnings = result.warnings
    assert any("long" in w.message for w in warnings)


def test_summary_with_issues():
    result = lint({"bad key": "", "another": "  "})
    s = result.summary()
    assert "error" in s
    assert "warning" in s


def test_lint_issue_str():
    issue = LintIssue("MY_KEY", "Something is wrong.", "error")
    assert str(issue) == "[ERROR] MY_KEY: Something is wrong."


def test_lint_result_separates_errors_and_warnings():
    result = LintResult(issues=[
        LintIssue("A", "err msg", "error"),
        LintIssue("B", "warn msg", "warning"),
        LintIssue("C", "warn msg 2", "warning"),
    ])
    assert len(result.errors) == 1
    assert len(result.warnings) == 2


def test_empty_env_no_issues():
    result = lint({})
    assert not result.has_issues
