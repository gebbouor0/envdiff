# envdiff.linter

The `linter` module checks individual `.env` files for style and convention
issues, independent of comparison between environments.

## Usage

```python
from envdiff.parser import parse_env_file
from envdiff.linter import lint

env = parse_env_file(".env")
result = lint(env)

if result.has_issues:
    for issue in result.issues:
        print(issue)
else:
    print(result.summary())
```

## API

### `lint(env: Dict[str, str]) -> LintResult`

Runs all lint checks against a parsed env dictionary and returns a
`LintResult`.

---

### `LintResult`

| Attribute / Property | Type | Description |
|---|---|---|
| `issues` | `List[LintIssue]` | All issues found |
| `has_issues` | `bool` | `True` if any issues exist |
| `errors` | `List[LintIssue]` | Issues with severity `"error"` |
| `warnings` | `List[LintIssue]` | Issues with severity `"warning"` |
| `summary()` | `str` | Human-readable summary line |

---

### `LintIssue`

| Field | Type | Description |
|---|---|---|
| `key` | `str` | The env key that triggered the issue |
| `message` | `str` | Description of the problem |
| `severity` | `str` | `"warning"` or `"error"` |

`str(issue)` returns a formatted string like:
```
[WARNING] database_url: Key should be uppercase (UPPER_SNAKE_CASE).
```

## Checks Performed

### Key naming
- **warning** — key is not fully uppercase (`UPPER_SNAKE_CASE` expected)
- **error** — key contains spaces
- **error** — key starts with a digit

### Value quality
- **warning** — value is empty
- **warning** — value has leading or trailing whitespace
- **warning** — value is longer than 500 characters
