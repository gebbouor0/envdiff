# envdiff.merger

Merge multiple `.env` files into a single resolved dictionary, with full
tracking of which keys were overridden by later files.

## Overview

When managing multiple environment layers (e.g. `.env.defaults`,
`.env.local`, `.env.production`) it is useful to see the final merged
result **and** understand which values were overwritten along the way.

`envdiff.merger` provides exactly that via `merge_env_files`.

---

## API

### `merge_env_files(*paths: str) -> MergeResult`

Merge one or more `.env` files in the order supplied.  Later files take
precedence over earlier ones (*last-write-wins*).

```python
from envdiff.merger import merge_env_files

result = merge_env_files(".env.defaults", ".env.local")
print(result.merged)          # final key→value dict
print(result.overridden_keys) # keys that appeared in >1 file
print(result.summary())       # human-readable summary
```

**Raises** `ValueError` if no paths are provided.

---

### `MergeResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `merged` | `dict[str, str]` | Final resolved environment. |
| `overrides` | `dict[str, list[tuple[str, str]]]` | Per-key history: `[(source_path, value), …]` |
| `overridden_keys` | `list[str]` | Keys that were set by more than one file. |

#### `MergeResult.summary() -> str`

Returns a short human-readable summary, e.g.:

```
Merged keys   : 12
Overridden keys: 3
Keys overridden: DB_HOST, LOG_LEVEL, SECRET_KEY
```

---

## Merge order example

```
.env.defaults   →  DB_HOST=localhost   LOG_LEVEL=info
.env.local      →  DB_HOST=db.local
.env.production →  LOG_LEVEL=warning

Final merged    →  DB_HOST=db.local    LOG_LEVEL=warning
```
