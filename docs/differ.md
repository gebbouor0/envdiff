# Unified Diff Output

The `envdiff.differ` module produces a **unified diff-style** view of differences
between two `.env` files, similar to `diff -u`.

## Overview

Unlike the standard reporter which groups differences by category, the unified
diff interleaves all changes in alphabetical key order with `+`/`-` prefixes,
making it easy to see exactly what changed between environments.

## Functions

### `build_unified_diff(result, left_label, right_label) -> List[str]`

Returns a list of diff lines. The first two lines are the `---`/`+++` headers.
Each subsequent line is prefixed with:

- `-` — key exists only in the left file (or old value of a mismatch)
- `+` — key exists only in the right file (or new value of a mismatch)

### `format_unified_diff(result, left_label, right_label) -> str`

Joins the output of `build_unified_diff` into a single newline-delimited string.

### `print_unified_diff(result, left_label, right_label) -> None`

Prints the formatted diff directly to stdout.

## Example

```python
from envdiff import diff_env_files
from envdiff.differ import print_unified_diff

result = diff_env_files(".env.staging", ".env.production")
print_unified_diff(result, ".env.staging", ".env.production")
```

**Output:**

```
--- .env.staging
+++ .env.production
- DB_HOST=staging-db.internal
+ DB_HOST=prod-db.internal
- DEBUG=true
+ NEW_RELIC_KEY=abc123
```

## Notes

- Keys are sorted alphabetically for consistent, reproducible output.
- Mismatched keys appear as a `-` / `+` pair (old then new).
- Keys present in both files with equal values are **not** shown.
