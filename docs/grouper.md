# Grouper

The `grouper` module splits a `DiffResult` into sub-results bucketed by **key prefix**.

For example, given keys like `DB_HOST`, `DB_PORT`, `APP_NAME`, and `AWS_KEY`, the grouper produces three groups: `DB`, `APP`, and `AWS`. Keys that have no separator (or start with one) fall into the special `__other__` group.

## API

### `group_result(result, separator="_") -> GroupResult`

Splits the given `DiffResult` into a `GroupResult`.

```python
from envdiff.grouper import group_result

gr = group_result(diff, separator="_")
for name in gr.group_names:
    print(name, gr.groups[name])
```

### `GroupResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `groups` | `dict[str, DiffResult]` | Mapping of prefix → sub-result |
| `separator` | `str` | Separator used during grouping |
| `group_names` | `list[str]` | Sorted list of group names |

`GroupResult.summary()` returns a human-readable overview of all groups.

## CLI

Pass `--group` to the main CLI to print the diff broken down by prefix:

```bash
envdiff .env.staging .env.prod --group
envdiff .env.staging .env.prod --group --group-sep .
```

`--group-sep` lets you choose a different separator (e.g. `.` for `DB.HOST` style keys).

## Notes

- Grouping is case-insensitive for the prefix label (always uppercased).
- An empty `DiffResult` produces no groups.
- Each sub-`DiffResult` is a standard `DiffResult` and is compatible with all other envdiff modules (reporter, exporter, scorer, etc.).
