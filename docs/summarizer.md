# Summarizer

The `envdiff.summarizer` module produces a concise statistical overview of a
`DiffResult` without printing the full key-by-key report.

## API

### `summarize(result: DiffResult) -> DiffSummary`

Returns a `DiffSummary` dataclass with the following fields:

| Field | Type | Description |
|---|---|---|
| `total_keys` | `int` | Union of all keys across both files |
| `missing_in_left_count` | `int` | Keys present only in the right file |
| `missing_in_right_count` | `int` | Keys present only in the left file |
| `mismatched_count` | `int` | Keys present in both but with different values |
| `match_count` | `int` | Keys that are identical in both files |
| `similarity_pct` | `float` | `match_count / total_keys * 100` |
| `type_breakdown` | `dict` | Counts grouped by category |

### `format_summary(summary: DiffSummary) -> str`

Returns a human-readable multi-line string suitable for terminal output.

### `DiffSummary.as_dict() -> dict`

Serialises the summary to a plain dictionary (useful for JSON export).

## CLI flags

Two flags are added by `envdiff.cli_summary.add_summary_args`:

```
--summary        Print a text summary instead of the full diff report.
--summary-json   Print the summary as a JSON object.
```

## Example

```bash
$ envdiff .env.staging .env.production --summary
Total keys : 42
Matching   : 38
Mismatched : 2
Only left  : 1
Only right : 1
Similarity : 90.5%

$ envdiff .env.staging .env.production --summary-json
{
  "total_keys": 42,
  "missing_in_left": 1,
  ...
}
```
