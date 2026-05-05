# envdiff

Compare `.env` files across environments and highlight missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourusername/envdiff.git
cd envdiff && pip install -e .
```

---

## Usage

Compare two `.env` files directly from the command line:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
Missing in .env.production:
  - DEBUG
  - STRIPE_TEST_KEY

Mismatched values:
  - DATABASE_URL  (values differ across environments)

✔ 12 keys match
```

You can also compare multiple files at once:

```bash
envdiff .env.development .env.staging .env.production
```

### Python API

```python
from envdiff import compare

results = compare(".env.development", ".env.production")
print(results.missing)
print(results.mismatched)
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)