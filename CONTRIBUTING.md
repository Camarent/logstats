# Contributing

## Setup

```bash
uv sync
git config core.hooksPath .githooks
```

The pre-commit hook runs a secret scan with `gitleaks`. Without `gitleaks` installed the commit
fails, unless you set `LOGSTATS_ALLOW_NO_GITLEAKS=1`.

## Checks

Run every check that CI runs, in the same order:

```bash
scripts/ci.sh
```

CI runs `ruff check`, `ruff format --check`, `mypy` (strict) and `pytest` with a coverage gate of 95%.
Keep these green before you open a pull request.

## Pull requests

- Branch from `master`; keep one change per pull request.
- Add or update tests for any behaviour change.
- Use a clear commit message that says what changed and why.
