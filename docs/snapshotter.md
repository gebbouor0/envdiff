# Snapshotter

The `envdiff.snapshotter` module lets you capture a `DiffResult` as a
time-stamped snapshot and persist it to disk as JSON. This is useful for
audit trails, CI artefacts, or comparing how your environment drift changes
over time.

## Data model

```python
@dataclass
class Snapshot:
    label: str                              # human-readable name
    timestamp: str                          # ISO-8601 UTC
    missing_in_right: dict[str, str]
    missing_in_left: dict[str, str]
    mismatched: dict[str, tuple[str, str]]
    metadata: dict                          # arbitrary extra info
```

## API

### `take_snapshot(result, label, metadata=None) -> Snapshot`

Create a `Snapshot` from a `DiffResult`.

```python
from envdiff.snapshotter import take_snapshot

snap = take_snapshot(diff, label="prod-2024-06-01", metadata={"author": "ci"})
```

### `save_snapshot(snapshot, path) -> None`

Serialise the snapshot to a JSON file. Intermediate directories are created
automatically.

```python
from envdiff.snapshotter import save_snapshot

save_snapshot(snap, "snapshots/prod.json")
```

### `load_snapshot(path) -> Snapshot`

Deserialise a previously saved snapshot.

```python
from envdiff.snapshotter import load_snapshot

snap = load_snapshot("snapshots/prod.json")
print(snap.label, snap.timestamp)
```

## Round-trip example

```python
from envdiff import diff_env_files
from envdiff.snapshotter import take_snapshot, save_snapshot, load_snapshot

result = diff_env_files(".env.staging", ".env.prod")
snap = take_snapshot(result, label="staging-vs-prod")
save_snapshot(snap, "snapshots/latest.json")

# later …
restored = load_snapshot("snapshots/latest.json")
print(restored.mismatched)
```
