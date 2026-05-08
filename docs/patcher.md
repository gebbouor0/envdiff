# envdiff.patcher

The `patcher` module lets you **apply a `DiffResult` back to an env dict** and
optionally write the result to disk.

## Quick start

```python
from envdiff import diff_env_files
from envdiff.patcher import build_patch, apply_patch, write_patched_env

diff = diff_env_files(".env.production", ".env.staging")

# Build a patch that brings staging up to date with production
patch = build_patch(diff, direction="left_to_right")

# Load the current staging env
from envdiff.parser import parse_env_file
env = parse_env_file(".env.staging")

# Apply — skip keys that already exist in staging
result = apply_patch(env, patch, keep_existing=True)
print(result.summary())  # e.g. "3 applied, 1 skipped"

# Persist
write_patched_env(env, ".env.staging.patched", header="patched by envdiff")
```

## API

### `build_patch(diff, direction="left_to_right") -> dict`

Converts a `DiffResult` into a flat `{key: value}` patch.

| direction | behaviour |
|---|---|
| `left_to_right` | adds keys missing in the right env; uses **left** value for mismatches |
| `right_to_left` | adds keys missing in the left env; uses **right** value for mismatches |

### `apply_patch(env, patch, keep_existing=False) -> PatchResult`

Mutates *env* in-place.

- `keep_existing=True` — never overwrite a key that already has a value.

### `write_patched_env(env, path, header=None)`

Writes the dict to a file in `KEY=VALUE` format.  
Values containing spaces or tabs are automatically quoted.

### `PatchResult`

| attribute | type | description |
|---|---|---|
| `applied` | `dict[str, str]` | keys that were written |
| `skipped` | `list[str]` | keys skipped due to `keep_existing` |
| `has_changes` | `bool` | `True` when at least one key was applied |
| `summary()` | `str` | human-readable one-liner |
