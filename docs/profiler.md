# envdiff.profiler

The `profiler` module analyses a single parsed `.env` file and reports common
quality issues such as empty values, duplicate keys, and keys containing
suspicious characters.

## Functions

### `profile(env_vars: Dict[str, str]) -> ProfileResult`

Accepts a dictionary of key/value pairs (as returned by `parse_env_file`) and
returns a `ProfileResult`.

```python
from envdiff.parser import parse_env_file
from envdiff.profiler import profile

vars = parse_env_file(".env.production")
result = profile(vars)
print(result.summary())
```

### `profile_file(path: str) -> ProfileResult`

Convenience wrapper that parses the file at `path` and calls `profile()`.

```python
from envdiff.profiler import profile_file

result = profile_file(".env.staging")
if result.has_issues:
    print(result.summary())
```

### `format_profile(result: ProfileResult, filename: str = "") -> str`

Returns a human-readable multi-line report string.

```python
from envdiff.profiler import profile_file, format_profile

result = profile_file(".env")
print(format_profile(result, filename=".env"))
```

## ProfileResult

| Attribute | Type | Description |
|---|---|---|
| `empty_values` | `List[str]` | Keys whose value is an empty string |
| `duplicate_keys` | `List[str]` | Keys that appeared more than once |
| `suspicious_keys` | `List[str]` | Keys containing spaces or special characters |
| `total_keys` | `int` | Total number of keys parsed |
| `has_issues` | `bool` | `True` if any issue list is non-empty |

### `summary() -> str`

Returns a one-line summary suitable for CLI output.

## Suspicious key detection

A key is considered suspicious if it contains any of the following characters:

```
space  tab  !  @  #  $  %  ^  &  *  (  )  {  }  [  ]  |  \  <  >  ?
```

Standard `.env` keys typically use only uppercase letters, digits, and
underscores (`A-Z`, `0-9`, `_`).
