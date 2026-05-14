# Caster

The `envdiff.caster` module provides utilities to **type-cast raw string values** from a parsed `.env` file into Python native types (`int`, `float`, `bool`, `str`).

## API

### `cast_env(env, schema) -> CastResult`

Cast every value in *env* according to *schema*, a mapping of key names to type name strings.

```python
from envdiff.caster import cast_env

env = {"PORT": "8080", "DEBUG": "true", "RATIO": "0.5"}
schema = {"PORT": "int", "DEBUG": "bool", "RATIO": "float"}

result = cast_env(env, schema)
print(result.casted)   # {'PORT': 8080, 'DEBUG': True, 'RATIO': 0.5}
print(result.failures) # {}
```

Keys not present in *schema* are kept as plain strings.

### `cast_keys(env, keys, target) -> CastResult`

Convenience wrapper that casts a specific list of *keys* to the same *target* type.

```python
from envdiff.caster import cast_keys

result = cast_keys(env, ["PORT", "WORKERS"], "int")
```

### `CastResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `casted` | `dict[str, Any]` | Successfully cast key/value pairs |
| `failures` | `dict[str, str]` | Keys that failed, mapped to error message |

Methods:
- `has_failures() -> bool`
- `summary() -> str` — human-readable one-liner

## Supported Types

| Type string | Python type | Notes |
|-------------|-------------|-------|
| `"int"` | `int` | |
| `"float"` | `float` | |
| `"bool"` | `bool` | Accepts `true/yes/1/on` and `false/no/0/off` |
| `"str"` | `str` | No-op passthrough |

## CLI

Pass `--cast` together with `--cast-schema` to cast values from the left env file:

```bash
envdiff .env.dev .env.prod --cast --cast-schema '{"PORT":"int","DEBUG":"bool"}'
```
