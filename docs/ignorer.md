# Key Ignorer

The `envdiff.ignorer` module lets you exclude specific keys from a `DiffResult` before reporting or exporting. This is useful for keys that are expected to differ between environments (e.g. secrets, machine-specific values).

## Core concepts

| Concept | Description |
|---|---|
| `IgnoreConfig` | Holds exact key names and/or shell-style wildcard patterns |
| `should_ignore` | Check whether a single key matches any ignore rule |
| `apply_ignore` | Filter an entire `DiffResult`, returning a clean copy |
| `build_ignore_config` | Convenience factory for `IgnoreConfig` |

## Usage

```python
from envdiff.ignorer import apply_ignore, build_ignore_config
from envdiff import diff_env_files

result = diff_env_files(".env.staging", ".env.production")

config = build_ignore_config(
    patterns=["SECRET_*", "AWS_*"],
    exact_keys=["INTERNAL_BUILD_ID"],
)

filtered = apply_ignore(result, config)
```

## Wildcard patterns

Patterns follow Python's `fnmatch` rules:

- `SECRET_*` — matches any key starting with `SECRET_`
- `*_TOKEN` — matches any key ending with `_TOKEN`
- `DB_*_HOST` — matches keys like `DB_PRIMARY_HOST`

## IgnoreConfig dataclass

```python
@dataclass
class IgnoreConfig:
    patterns: list[str]   # fnmatch-style patterns
    exact_keys: set[str]  # literal key names
```

Both fields default to empty, so an `IgnoreConfig()` with no arguments ignores nothing.

## Notes

- `apply_ignore` does **not** mutate the original `DiffResult`; it returns a new instance.
- Keys removed from `missing_in_right`, `missing_in_left`, and `mismatched` are also removed from `common_keys`.
