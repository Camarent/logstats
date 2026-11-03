#!/usr/bin/env bash
# Run the same checks as .github/workflows/ci.yml, in the same order.
set -euo pipefail

cd "$(dirname "$0")/.."

uv sync --locked
uv run ruff check
uv run ruff format --check
uv run mypy
uv run pytest
