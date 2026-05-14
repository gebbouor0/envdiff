# masker

The `masker` module masks sensitive values in an env dictionary before display or export, based on configurable glob patterns.

## Usage

```python
from envdiff.masker import mask_env, build_mask_config

env = {
    "DB_HOST": "localhost",
    "DB_PASSWORD": "supersecret",
    "API_KEY": "abc123",
    "APP_NAME": "myapp",
}

result = mask_env(env)
print(result.masked)
# {'DB_HOST': 'localhost', 'DB_PASSWORD': '***', 'API_KEY': '***', 'APP_NAME': 'myapp'}

print(result.summary)
# 2 key(s) masked: API_KEY, DB_PASSWORD
```

## Custom Patterns

```python
config = build_mask_config(
    patterns=["*HIDDEN*", "*PRIV*"],
    placeholder="[REDACTED]",
)
result = mask_env(env, config=config)
```

## MaskConfig

| Field | Type | Default |
|---|---|---|
| `patterns` | `List[str]` | Built-in sensitive patterns |
| `case_sensitive` | `bool` | `False` |
| `placeholder` | `str` | `***` |

## MaskResult

| Attribute | Description |
|---|---|
| `original` | Unmodified input dict |
| `masked` | Dict with sensitive values replaced |
| `masked_keys` | List of keys that were masked |
| `has_masked` | `True` if any keys were masked |
| `summary` | Human-readable summary string |

## Default Patterns

- `*PASSWORD*`
- `*SECRET*`
- `*TOKEN*`
- `*API_KEY*`
- `*PRIVATE_KEY*`
- `*CREDENTIALS*`

## CLI

```
envdiff left.env right.env --mask
envdiff left.env right.env --mask --mask-patterns "*HIDDEN*" --mask-placeholder "[X]"
```
