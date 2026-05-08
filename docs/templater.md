# `envdiff.templater`

Generate `.env` template files from a parsed environment dictionary or a
`DiffResult`, making it easy to bootstrap new environments from existing ones.

---

## Classes

### `TemplateResult`

Holds the rendered lines of a generated template.

| Attribute | Type | Description |
|-----------|------|-------------|
| `lines` | `list[str]` | Ordered `KEY=VALUE` lines |

**Methods**

- `render() -> str` — Join all lines with `\n` and return the full string.
- `write(path: str) -> None` — Write the rendered template to *path* (appends a trailing newline).

---

## Functions

### `from_dict(env, *, redact_keys=None, placeholder=None) -> TemplateResult`

Build a template from a plain `dict[str, str]`.

```python
from envdiff.templater import from_dict

env = {"DB_HOST": "localhost", "DB_PASSWORD": "s3cr3t", "PORT": "5432"}
tr = from_dict(env, redact_keys=["password"])
print(tr.render())
# DB_HOST=localhost
# DB_PASSWORD=<db_password>
# PORT=5432
```

**Parameters**

| Name | Default | Description |
|------|---------|-------------|
| `redact_keys` | `[]` | Substrings; matching key names get a placeholder |
| `placeholder` | `None` | Override the auto-generated `<key_name>` placeholder |

---

### `from_diff(result, *, include_mismatched=True, placeholder=None) -> TemplateResult`

Build a template covering every key seen in a `DiffResult`.

```python
from envdiff.templater import from_diff

tr = from_diff(diff_result, placeholder="FILL_ME")
tr.write(".env.template")
```

**Parameters**

| Name | Default | Description |
|------|---------|-------------|
| `include_mismatched` | `True` | Whether to include mismatched keys |
| `placeholder` | `None` | Value written for every generated key; defaults to `<key_name>` |

> **Tip:** pipe the output through `sort` or use the built-in `sorter` module
> if you need a specific ordering beyond alphabetical.
