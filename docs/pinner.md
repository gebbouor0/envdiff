# Pinner

The `pinner` module lets you **pin** a snapshot of an env file's key-value pairs as a named baseline, then later **check for drift** — values that changed, keys that appeared, or keys that disappeared.

## Core concepts

| Term | Meaning |
|------|---------|
| **pin** | A saved baseline of key → value pairs with a human label |
| **drift** | Any difference between the baseline and the current env |

## API

### `pin_env(env, label) -> PinResult`

Captures `env` (a `dict`) as a named baseline.

```python
from envdiff.parser import parse_env_file
from envdiff.pinner import pin_env, save_pin
from pathlib import Path

env = parse_env_file(".env.production")
pin = pin_env(env, label="prod-2024-06")
save_pin(pin, Path("pins/prod.json"))
```

### `check_drift(baseline, current) -> PinResult`

Compares a loaded baseline against a fresh env dict.

```python
from envdiff.pinner import load_pin, check_drift

baseline = load_pin(Path("pins/prod.json"))
current = parse_env_file(".env.production")
result = check_drift(baseline, current)

if result.has_drift():
    print(result.summary())
```

### `PinResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `label` | `str` | Human-readable baseline name |
| `pinned` | `dict` | Original key-value snapshot |
| `drifted` | `dict` | Keys whose values changed (key → new value) |
| `new_keys` | `list` | Keys present in current but not in baseline |
| `removed_keys` | `list` | Keys in baseline but missing from current |

## CLI flags

```
--pin FILE          Save current left env as a pin baseline
--pin-label LABEL   Label for the pin (default: baseline)
--check-drift FILE  Compare left env against a saved pin
```

### Example

```bash
# Pin today's production env
envdiff .env.prod .env.staging --pin pins/prod.json --pin-label prod-baseline

# Later, check if prod has drifted
envdiff .env.prod .env.staging --check-drift pins/prod.json
```
