# Validator

The `envdiff.validator` module lets you validate a parsed `.env` dictionary
against a set of constraints: required keys, an allowlist, and per-key value
rules.

## Quick start

```python
from envdiff.parser import parse_env_file
from envdiff.validator import validate

env = parse_env_file(".env.production")

result = validate(
    env,
    required_keys=["DATABASE_URL", "SECRET_KEY", "APP_ENV"],
    allowed_keys=["DATABASE_URL", "SECRET_KEY", "APP_ENV", "DEBUG"],
    rules={
        "APP_ENV": lambda v: v in ("development", "staging", "production"),
        "DEBUG": lambda v: v in ("true", "false", "1", "0"),
    },
)

if not result.is_valid:
    print(result.summary())
```

## API

### `validate(env, required_keys, allowed_keys, rules) -> ValidationResult`

| Parameter | Type | Description |
|---|---|---|
| `env` | `dict[str, str]` | Parsed env pairs from `parse_env_file`. |
| `required_keys` | `list[str] \| None` | Keys that must be present. |
| `allowed_keys` | `list[str] \| None` | If set, any key outside this list is flagged as unexpected. |
| `rules` | `dict[str, callable] \| None` | Per-key predicates. Return `True` to pass; exceptions are caught and recorded. |

### `ValidationResult`

| Attribute | Type | Description |
|---|---|---|
| `missing_required` | `list[str]` | Required keys absent from the env. |
| `unexpected_keys` | `list[str]` | Keys not in the allowlist. |
| `invalid_values` | `dict[str, str]` | Keys whose values failed a rule, mapped to a reason string. |
| `is_valid` | `bool` | `True` when all three lists/dicts are empty. |
| `summary()` | `str` | Human-readable one-liner describing issues, or `"All keys are valid."` |

## Integration with `diff_env_files`

You can validate each side of a diff independently before comparing:

```python
from envdiff import diff_env_files
from envdiff.parser import parse_env_file
from envdiff.validator import validate

required = ["DATABASE_URL", "SECRET_KEY"]

for path in (".env.staging", ".env.production"):
    env = parse_env_file(path)
    vr = validate(env, required_keys=required)
    if not vr.is_valid:
        print(f"{path}: {vr.summary()}")

diff = diff_env_files(".env.staging", ".env.production")
```
