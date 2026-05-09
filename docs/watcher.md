# envdiff watcher

The `watcher` module polls two `.env` files and fires a callback whenever
either file is modified on disk.

## Quick start

```python
from envdiff.watcher import watch
from envdiff.reporter import print_report

watch(
    "staging.env",
    "production.env",
    on_change=print_report,
    interval=2.0,
)
```

Press **Ctrl-C** to stop.

## API

### `WatchState`

Internal dataclass that tracks the last-seen `mtime` and parsed key/value
dict for a single file.

| Attribute | Type | Description |
|-----------|------|-------------|
| `path` | `Path` | File being watched |
| `mtime` | `float` | Last modification time |
| `env` | `dict[str, str]` | Parsed contents |

`WatchState.refresh()` re-reads the file when the mtime has advanced and
returns `True` if the file changed.

### `watch(left, right, on_change, interval, max_cycles)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `left` | `str` | — | Path to the left `.env` file |
| `right` | `str` | — | Path to the right `.env` file |
| `on_change` | `Callable[[DiffResult], None]` | — | Called on every detected change |
| `interval` | `float` | `1.0` | Seconds between polls |
| `max_cycles` | `int \| None` | `None` | Stop after N cycles; `None` = forever |

## CLI flag

Pass `--watch` to the main CLI to enable continuous watching:

```bash
envdiff staging.env production.env --watch --watch-interval 2
```

The diff is reprinted to stdout every time a change is detected.
