# aliaser

The `aliaser` module lets you declare that certain key names across different `.env` files are semantically equivalent — just named differently. This is common when one environment calls a database connection string `DATABASE_URL` while another uses `DB_URL`.

## Core types

### `AliasConfig`

Holds a dict mapping a **canonical** key name to a list of **alias** patterns (supports `fnmatch` wildcards).

```python
from envdiff.aliaser import build_alias_config

config = build_alias_config({
    "DATABASE_URL": ["DB_URL", "DB_CONNECTION"],
    "SECRET_KEY":   ["APP_SECRET", "SECRET"],
    "AWS_ACCESS_KEY": ["AWS_KEY*"],
})
```

### `AliasResult`

Returned by `resolve_aliases`. Contains:

| Field | Type | Description |
|---|---|---|
| `resolved` | `dict[str, str]` | alias key → canonical key |
| `unresolved_missing_right` | `list[str]` | keys still missing in right after alias lookup |
| `unresolved_missing_left` | `list[str]` | keys still missing in left after alias lookup |
| `unresolved_mismatched` | `list[str]` | mismatched keys with no alias match |

## Usage

```python
from envdiff.comparator import compare
from envdiff.aliaser import build_alias_config, resolve_aliases

diff = compare(left_env, right_env)

config = build_alias_config({
    "DATABASE_URL": ["DB_URL"],
})

result = resolve_aliases(diff, config)
print(result.summary())
# 1 alias(es) resolved, 0 key(s) still unresolved

if result.has_unresolved():
    print("Still unresolved:", result.unresolved_missing_right)
```

## Wildcard patterns

Alias patterns follow `fnmatch` rules:

- `AWS_KEY*` matches `AWS_KEY_ID`, `AWS_KEY_SECRET`, etc.
- `DB_*` matches any key starting with `DB_`.

## Notes

- Matching is case-sensitive by default (mirrors `fnmatch` on most platforms).
- A key is resolved as soon as the **first** matching alias pattern is found.
- The canonical key itself is never looked up as an alias.
